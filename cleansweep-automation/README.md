# cleansweep-automation
An intelligent directory cleaning automation tool that detects and removes duplicate files while providing detailed email reports.


🚀 Features

🔍 Smart Duplicate Detection: Uses MD5 checksums for accurate file comparison

🗂️ Recursive Directory Scanning: Processes all subdirectories automatically

📊 Detailed Logging: Generates timestamped reports with deletion summaries

📧 Email Automation: Sends reports directly to your inbox with log attachments

⏰ Scheduled Execution: Runs at regular intervals for continuous cleanup

🛡️ Safe Operations: Preserves the first occurrence of duplicate files

🎯 Cross-Platform: Works on Windows, macOS, and Linux



🔧 How It Works

1. File Scanning:
Recursively scans the specified directory
Calculates MD5 checksums for all files
Groups files with identical checksums

2. Duplicate Detection:
Compares file checksums to identify duplicates
Preserves the first occurrence of each file
Marks subsequent duplicates for deletion

3. Safe Deletion:
Removes duplicate files while preserving originals
Logs all deletion operations
Handles errors gracefully

4. Report Generation:
Creates timestamped log files
Includes detailed deletion summaries
Provides file paths and checksums

5. Email Notification:
Sends automated email reports
Attaches detailed log files
Includes cleanup statistics


📧 Email Setup:

Supported Email Providers

  1.Gmail (default configuration)
  
  2.Outlook (modify SMTP settings)
  
  3.Yahoo (modify SMTP settings)


Log File Location

Log files are created in the same directory as the script with the naming format:

LogFile_YYYY_MM_DD_HH_MM_SS_microseconds.txt


⚠️ Safety Considerations

1.Backup Important Data: Always backup critical files before running

2.Test on Sample Directory: Try the script on a test folder first

3.Review Log Files: Check deletion logs to ensure expected behavior

4.Network Permissions: Ensure proper permissions for network drives


🔐 Security Notes

1.Never commit email credentials to version control

2.Use environment variables for sensitive information:
  pythonimport os
  EMAIL = os.getenv('CLEANSWEEP_EMAIL')
  PASSWORD = os.getenv('CLEANSWEEP_PASSWORD')
  
3.Consider using OAuth2 for production environments


🤝 Contributing

We welcome contributions! Please follow these steps:

1.Fork the repository

2.Create a feature branch: git checkout -b feature/amazing-feature

3.Commit your changes: git commit -m 'Add amazing feature'

4.Push to the branch: git push origin feature/amazing-feature

5.Open a Pull Request
  
