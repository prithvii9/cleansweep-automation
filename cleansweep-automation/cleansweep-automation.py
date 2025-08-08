#!/usr/bin/env python3
"""
Directory Cleaning Automation Script with Email Reporting
=========================================================

This script automatically finds and removes duplicate files in a specified directory
and sends an email report with the deletion log as an attachment.

Author: Prithviraj Chavan
Description: Automated directory cleaning with email notifications
Version: 1.0
"""

import sys
import os
import schedule
import datetime
import hashlib
import time
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def CalculateCheckSum(path, BlockSize=1024):
    """
    Calculate MD5 checksum of a file to identify duplicates.
    
    Args:
        path (str): Path to the file
        BlockSize (int): Size of buffer for reading file (default: 1024 bytes)
    
    Returns:
        str: MD5 hexadecimal digest of the file
    
    Note:
        Files with identical checksums are considered duplicates
    """
    # Create MD5 hash object
    hobj = hashlib.md5()
    
    # Open file in binary read mode
    fobj = open(path, 'rb')
    Buffer = fobj.read(BlockSize)

    # Read file in chunks and update hash
    while(len(Buffer) > 0):
        hobj.update(Buffer)
        Buffer = fobj.read(BlockSize)
    
    fobj.close()
    
    # Return hexadecimal representation of the hash
    return hobj.hexdigest()


def FindDuplicate(DirectoryName):
    """
    Scan directory recursively to find duplicate files based on MD5 checksums.
    
    Args:
        DirectoryName (str): Path to the directory to scan
    
    Returns:
        dict: Dictionary with checksum as key and list of file paths as values
              Format: {checksum: [file1_path, file2_path, ...]}
    
    Raises:
        SystemExit: If directory path is invalid or not a directory
    """
    # Convert to absolute path if relative path is provided
    if(os.path.isabs(DirectoryName) == False):
        DirectoryName = os.path.abspath(DirectoryName)
        print("Absolute path:", DirectoryName)

    # Validate directory existence
    if(os.path.exists(DirectoryName) == False):
        print("Error: Invalid path - Directory does not exist")
        exit()

    # Validate that path is a directory
    if(os.path.isdir(DirectoryName) == False):
        print("Error: Path is valid but it is not a directory")
        exit()
    
    # Dictionary to store duplicates: {checksum: [list_of_file_paths]}
    Duplicates = {}
    
    # Walk through all subdirectories and files
    for FolderName, SubFolderName, Files in os.walk(DirectoryName):
        
        for fname in Files:
            # Get full file path
            fname = os.path.join(FolderName, fname)
            
            # Calculate file checksum
            checksum = CalculateCheckSum(fname)
            
            # Group files by checksum (duplicates will have same checksum)
            if checksum in Duplicates:
                Duplicates[checksum].append(fname)
            else:
                Duplicates[checksum] = [fname]

    return Duplicates


def DeleteDuplicates(DirectoryName):
    """
    Delete duplicate files from directory and create a detailed log report.
    Automatically emails the log file to specified recipient.
    
    Args:
        DirectoryName (str): Path to the directory to clean
    
    Process:
        1. Find all duplicate files using FindDuplicate()
        2. Keep the first occurrence of each duplicate set
        3. Delete all other duplicates
        4. Create timestamped log file with deletion details
        5. Send email with log file attached
    """
    # Find all duplicate files
    print("Scanning for duplicate files...")
    Duplicates = FindDuplicate(DirectoryName)
    
    # Formatting variables
    border = '-' * 55
    Count = 0       # Counter for files in current duplicate group
    DelCount = 0    # Total count of deleted files
    
    # Generate timestamp for log file name
    curr_time = str(datetime.datetime.now())
    curr_time = curr_time.replace("-", "_")
    curr_time = curr_time.replace(":", "_")
    curr_time = curr_time.replace(".", "_")
    curr_time = curr_time.replace(" ", "_")
    print(f"Current timestamp: {curr_time}")
    
    # Create log file with timestamp
    FileName = f"LogFile_{curr_time}.txt"
    fobj = open(FileName, 'w')
    fobj.write(f"{border} DELETED FILES REPORT {border}\n")
    fobj.write(f"Directory Cleaned: {DirectoryName}\n")
    fobj.write(f"Scan Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    fobj.write(f"{border}\n\n")

    # Process each group of duplicate files
    for checksum in Duplicates:
        duplicate_files = Duplicates[checksum]
        
        # Only process if there are actual duplicates (more than 1 file)
        if len(duplicate_files) > 1:
            fobj.write("Deleted:\n")
            
            # Delete all duplicates except the first one
            for file_path in duplicate_files[1:]:
                try:
                    fobj.write(f"  - {file_path}\n")
                    os.remove(file_path)
                    DelCount += 1
                except OSError as e:
                    print(f"Error deleting {file_path}: {e}")
                    fobj.write(f"  - ERROR deleting {file_path}: {e}\n")
    
    # Write summary to log file
    fobj.write(f"\n{border}\n")
    fobj.write(f"SUMMARY:\n")
    fobj.write(f"Total Duplicate Files Deleted: {DelCount}\n")
    fobj.write(f"Log Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    fobj.write(f"{border}\n")
    fobj.close()
    
    print(f"Cleanup completed. Deleted {DelCount} duplicate files.")
    print(f"Log file created: {FileName}")
    
    # ========================================================================
    # EMAIL AUTOMATION SECTION
    # ========================================================================
    
    # Email configuration
    # NOTE: Replace with your actual email credentials
    load_dotenv(dotenv_path=".env.local")

    EMAIL =  os.getenv("USER_EMAIL")    # Sender's email address
    PASSWORD = os.getenv("USER_PASSWORD")        # App password (not regular password)
    RECIPIENT = 'aayushmusale04@gmail.com'  # Recipient's email address
    
    try:
        # Create email message
        msg = EmailMessage()
        msg['Subject'] = f'Directory Cleanup Report - {DelCount} Files Deleted'
        msg['From'] = EMAIL
        msg['To'] = RECIPIENT
        
        # Email body content
        email_body = f"""
        Directory Cleanup Automation Report
        ====================================
        
        Directory Cleaned: {DirectoryName}
        Scan Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Total Duplicate Files Deleted: {DelCount}
        
        Please find the detailed log file attached.
        
        This is an automated message from Directory Cleaning Script.
        
        Best regards,
        Aayush Musale
        """
        msg.set_content(email_body)

        # Attach the log file
        file_path = FileName
        file_name = os.path.basename(file_path)

        with open(file_path, 'rb') as f:
            file_data = f.read()
            # Attach as text file
            msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

        # Send the email via Gmail SMTP
        print("Sending email report...")
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()  # Enable TLS encryption
            smtp.login(EMAIL, PASSWORD)
            smtp.send_message(msg)
        
        print(f"Email report sent successfully to {RECIPIENT}")
        
    except Exception as e:
        print(f"Error sending email: {e}")
        print("Log file has been created locally even though email failed.")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Main function that handles command line arguments and schedules the cleanup task.
    
    Command Line Arguments:
        --h, --H : Display help information
        --u, --U : Display usage information
        <directory_path> : Path to directory to clean (runs scheduled cleanup)
    
    Scheduling:
        - Runs cleanup every 1 hour when directory path is provided
        - Continues running until manually stopped (Ctrl+C)
    """
    # Display header
    Border = '-' * 110
    print(Border)
    print("\t\t\t\t\tAayush Musale")
    print("\t\t\t\tDirectory Cleaning Automation Tool")
    print(Border)

    # Handle command line arguments
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        
        # Help flag
        if arg in ['--h', '--H']:
            print("DIRECTORY CLEANING AUTOMATION TOOL")
            print("==================================")
            print("This application automatically finds and removes duplicate files")
            print("from a specified directory and sends an email report.")
            print()
            print("Features:")
            print("- Recursive directory scanning")
            print("- MD5 checksum-based duplicate detection")
            print("- Automatic deletion of duplicate files")
            print("- Detailed log file generation")
            print("- Email notification with log attachment")
            print("- Scheduled execution every hour")
            
        # Usage flag
        elif arg in ['--u', '--U']:
            print("USAGE INSTRUCTIONS")
            print("==================")
            print("Command format:")
            print("  python cleansweep.py <directory_path>")
            print()
            print("Examples:")
            print("  python cleansweep.py /home/user/Downloads")
            print("  python cleansweep.py C:\\Users\\User\\Documents")
            print()
            print("Notes:")
            print("- Provide absolute or relative directory path")
            print("- Script will run continuously, checking every hour")
            print("- Press Ctrl+C to stop the script")
            print("- Ensure email credentials are configured in the script")
            
        # Directory path provided - start scheduled cleanup
        else:
            directory_path = arg
            print(f"Starting automated cleanup for directory: {directory_path}")
            print("Cleanup will run every 1 hour...")
            print("Press Ctrl+C to stop the automation")
            print()
            
            # Schedule the cleanup task to run every hour
            schedule.every(1).hour.do(DeleteDuplicates, directory_path)

            try:
                # Keep the script running and execute scheduled tasks
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nScript stopped by user. Goodbye!")
                
    else:
        # Invalid number of arguments
        print("ERROR: Invalid number of command line arguments")
        print()
        print("Available options:")
        print("  --h  : Display help information")
        print("  --u  : Display usage instructions")
        print("  <directory_path> : Start automated cleanup for specified directory")
        print()
        print("Example: python cleansweep.py /path/to/directory")

    # Display footer
    print(Border)
    print("----------- Thank you for using our script -----------")
    print("---------------------Aayush Musale-- -----------------")
    print(Border)


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()