# Task_List - EOD Email Extractor

An automated tool to extract End of Day (EOD) sections from daily task list emails within a specified date range. This tool helps streamline reporting and tracking of daily completed tasks by automatically parsing email content and extracting structured task information.

## Features

- **Email Integration**: Connects to IMAP email servers (Gmail, Outlook, etc.)
- **Date Range Filtering**: Extract EOD sections from emails within specific date ranges
- **Intelligent Parsing**: Robust pattern matching to identify EOD sections and parse task entries
- **Multiple Output Formats**: Support for JSON, CSV, and text output formats
- **Time Tracking**: Automatically extracts time spent on each task
- **Configurable**: YAML-based configuration for email settings and parsing rules
- **Command Line Interface**: Easy-to-use CLI with various options

## Installation

1. Clone this repository:
```bash
git clone https://github.com/codeHUBG9/Task_List.git
cd Task_List
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up configuration:
```bash
cp config.yaml.template config.yaml
# Edit config.yaml with your email settings
```

## Configuration

Copy `config.yaml.template` to `config.yaml` and configure your email settings:

```yaml
email:
  server: "imap.gmail.com"  # Your IMAP server
  port: 993
  use_ssl: true
  username: "your_email@example.com"
  password: "your_password_or_app_password"
  folder: "INBOX"
```

**Note**: For Gmail, you'll need to use an App Password instead of your regular password. Enable 2-factor authentication and generate an App Password in your Google Account settings.

## Usage

### Basic Usage

Extract EOD sections from emails in the last week:
```bash
python eod_extractor.py --start "2024-01-01" --end "2024-01-31"
```

### Output Formats

**JSON Output (default):**
```bash
python eod_extractor.py --start "2024-01-01" --end "2024-01-31" --format json
```

**CSV Output:**
```bash
python eod_extractor.py --start "2024-01-01" --end "2024-01-31" --format csv --output tasks.csv
```

**Text Output:**
```bash
python eod_extractor.py --start "2024-01-01" --end "2024-01-31" --format text
```

### Advanced Options

```bash
# Custom configuration file
python eod_extractor.py --config my_config.yaml --start "2024-01-01" --end "2024-01-31"

# Verbose logging
python eod_extractor.py --start "2024-01-01" --end "2024-01-31" --verbose

# Save to file
python eod_extractor.py --start "2024-01-01" --end "2024-01-31" --output eod_report.json
```

## EOD Section Format

The tool recognizes EOD sections that start with keywords like "EOD", "End of Day", "Daily Summary", or "Task Summary" and extracts task entries in formats like:

```
EOD:
- Checking tracker and tickets-20 min
- Team meeting and discussion-30 min
- TLS #49172 - TLS Error- 01:25 hrs
- Discussion with Ritu regarding their ticket-45 min
- TLS#66638-Require to move TLS project from DCPL framework to DFramework-04:20 hrs
```

## Example Output

### JSON Format
```json
[
  {
    "email_id": "123",
    "subject": "Daily Status Update - 2024-01-15",
    "date": "2024-01-15T10:30:00",
    "eod_section": {
      "section_header": "EOD",
      "tasks": [
        {
          "description": "Checking tracker and tickets",
          "time_spent": "20 min",
          "raw_line": "- Checking tracker and tickets-20 min"
        },
        {
          "description": "Team meeting and discussion",
          "time_spent": "30 min",
          "raw_line": "- Team meeting and discussion-30 min"
        }
      ]
    }
  }
]
```

### CSV Format
```csv
Date,Subject,Task Description,Time Spent,Email ID
2024-01-15T10:30:00,Daily Status Update,Checking tracker and tickets,20 min,123
2024-01-15T10:30:00,Daily Status Update,Team meeting and discussion,30 min,123
```

## Customization

### Adding New EOD Keywords

Edit `config.yaml` to add custom EOD section keywords:

```yaml
parsing:
  eod_keywords:
    - "EOD"
    - "End of Day"
    - "Daily Summary"
    - "Your Custom Keyword"
```

### Time Pattern Recognition

The tool recognizes various time formats. Add custom patterns in `config.yaml`:

```yaml
parsing:
  time_patterns:
    - "\\d+\\s*min"          # e.g., "20 min"
    - "\\d+:\\d+\\s*hrs?"    # e.g., "01:25 hrs"
    - "\\d+\\.\\d+\\s*hrs?"  # e.g., "1.5 hrs"
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**: 
   - For Gmail: Use App Password, not regular password
   - Enable 2-factor authentication first
   - Check server settings in config.yaml

2. **No EOD Sections Found**:
   - Check if your emails contain the configured EOD keywords
   - Verify the date range includes emails with EOD sections
   - Use `--verbose` flag for detailed logging

3. **IMAP Connection Issues**:
   - Verify server and port settings
   - Check if IMAP is enabled in your email account
   - Ensure firewall allows IMAP connections

### Email Provider Settings

**Gmail:**
- Server: imap.gmail.com
- Port: 993
- SSL: true
- Enable 2FA and use App Password

**Outlook/Hotmail:**
- Server: outlook.office365.com
- Port: 993
- SSL: true

## Requirements

- Python 3.6+
- PyYAML
- python-dateutil
- IMAP access to your email account

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review existing GitHub issues
3. Create a new issue with detailed information about your problem
