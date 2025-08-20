#!/usr/bin/env python3
"""
EOD Section Extractor

A tool to extract End of Day (EOD) sections from emails within a specified date range.
Supports multiple output formats and is configurable via YAML configuration.

Author: Auto-generated for Task_List repository
"""

import imaplib
import email
import re
import json
import csv
import yaml
import argparse
import logging
import sys
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from typing import List, Dict, Any, Optional, Tuple
import io


class EODExtractor:
    """Main class for extracting EOD sections from emails."""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize the EOD extractor with configuration."""
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.imap = None
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logging.error(f"Configuration file {config_path} not found. Please copy config.yaml.template to config.yaml and configure it.")
            sys.exit(1)
        except yaml.YAMLError as e:
            logging.error(f"Error parsing configuration file: {e}")
            sys.exit(1)
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def connect_to_email(self) -> bool:
        """Connect to the email server."""
        try:
            email_config = self.config['email']
            
            if email_config['use_ssl']:
                self.imap = imaplib.IMAP4_SSL(email_config['server'], email_config['port'])
            else:
                self.imap = imaplib.IMAP4(email_config['server'], email_config['port'])
            
            self.imap.login(email_config['username'], email_config['password'])
            self.imap.select(email_config['folder'])
            
            logging.info(f"Successfully connected to {email_config['server']}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to connect to email server: {e}")
            return False
    
    def disconnect_from_email(self):
        """Disconnect from the email server."""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
                logging.info("Disconnected from email server")
            except:
                pass
    
    def search_emails_by_date(self, start_date: datetime, end_date: datetime) -> List[str]:
        """Search for emails within the specified date range."""
        try:
            # Format dates for IMAP search
            start_str = start_date.strftime("%d-%b-%Y")
            end_str = end_date.strftime("%d-%b-%Y")
            
            # Search for emails in date range
            search_criteria = f'(SINCE "{start_str}" BEFORE "{end_str}")'
            typ, data = self.imap.search(None, search_criteria)
            
            if typ != 'OK':
                logging.error("Failed to search emails")
                return []
            
            email_ids = data[0].split()
            logging.info(f"Found {len(email_ids)} emails in date range {start_str} to {end_str}")
            return [email_id.decode() for email_id in email_ids]
            
        except Exception as e:
            logging.error(f"Error searching emails: {e}")
            return []
    
    def fetch_email_content(self, email_id: str) -> Optional[Tuple[str, str, datetime]]:
        """Fetch email content and metadata."""
        try:
            typ, data = self.imap.fetch(email_id, '(RFC822)')
            if typ != 'OK':
                return None
            
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Extract email metadata
            subject = email_message.get('Subject', 'No Subject')
            date_str = email_message.get('Date', '')
            
            try:
                email_date = date_parser.parse(date_str)
            except:
                email_date = datetime.now()
            
            # Extract email body
            body = self._get_email_body(email_message)
            
            return subject, body, email_date
            
        except Exception as e:
            logging.error(f"Error fetching email {email_id}: {e}")
            return None
    
    def _get_email_body(self, email_message) -> str:
        """Extract email body from email message."""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    charset = part.get_content_charset()
                    payload = part.get_payload(decode=True)
                    if payload:
                        try:
                            body += payload.decode(charset or 'utf-8', errors='ignore')
                        except:
                            body += str(payload)
        else:
            charset = email_message.get_content_charset()
            payload = email_message.get_payload(decode=True)
            if payload:
                try:
                    body = payload.decode(charset or 'utf-8', errors='ignore')
                except:
                    body = str(payload)
        
        return body
    
    def extract_eod_section(self, email_body: str, subject: str) -> Optional[Dict[str, Any]]:
        """Extract EOD section from email body."""
        parsing_config = self.config['parsing']
        eod_keywords = parsing_config['eod_keywords']
        time_patterns = parsing_config['time_patterns']
        
        # Look for EOD section markers
        eod_pattern = '|'.join([re.escape(keyword) for keyword in eod_keywords])
        eod_regex = re.compile(f'({eod_pattern}).*?:', re.IGNORECASE | re.MULTILINE)
        
        match = eod_regex.search(email_body)
        if not match:
            return None
        
        # Extract content after EOD marker
        eod_start = match.end()
        eod_content = email_body[eod_start:]
        
        # Find the end of EOD section (next major section or end of email)
        # Look for common section markers or significant whitespace
        end_markers = ['Best regards', 'Thanks', 'Regards', 'Sincerely', '\n\n\n', 'From:', 'Sent:']
        end_pattern = '|'.join([re.escape(marker) for marker in end_markers])
        end_regex = re.compile(f'({end_pattern})', re.IGNORECASE)
        
        end_match = end_regex.search(eod_content)
        if end_match:
            eod_content = eod_content[:end_match.start()]
        
        # Parse individual tasks from EOD content
        tasks = self._parse_eod_tasks(eod_content, time_patterns)
        
        if not tasks:
            return None
        
        return {
            'section_header': match.group(1),
            'tasks': tasks,
            'raw_content': eod_content.strip()
        }
    
    def _parse_eod_tasks(self, eod_content: str, time_patterns: List[str]) -> List[Dict[str, str]]:
        """Parse individual tasks from EOD content."""
        tasks = []
        
        # Split content into lines and filter out empty lines
        lines = [line.strip() for line in eod_content.split('\n') if line.strip()]
        
        # Combine time patterns into a single regex
        time_pattern = '|'.join([f'({pattern})' for pattern in time_patterns])
        time_regex = re.compile(time_pattern, re.IGNORECASE)
        
        for line in lines:
            # Skip lines that don't look like task entries
            if not line or len(line) < 5:
                continue
            
            # Look for bullet points or dashes at the start
            if not (line.startswith('-') or line.startswith('•') or line.startswith('*') or 
                   re.match(r'^\d+\.', line) or any(char.isalnum() for char in line[:10])):
                continue
            
            # Clean up the line
            clean_line = line.lstrip('-•*').strip()
            if clean_line.startswith('.'):
                clean_line = clean_line[1:].strip()
            
            # Extract time information
            time_match = time_regex.search(clean_line)
            if time_match:
                time_spent = time_match.group(0)
                # Remove time from task description
                task_description = clean_line[:time_match.start()].strip()
                # Remove common separators
                task_description = task_description.rstrip('-:').strip()
            else:
                time_spent = None
                task_description = clean_line
            
            if task_description:
                tasks.append({
                    'description': task_description,
                    'time_spent': time_spent,
                    'raw_line': line
                })
        
        return tasks
    
    def extract_eod_from_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Extract EOD sections from all emails in the specified date range."""
        if not self.connect_to_email():
            return []
        
        try:
            email_ids = self.search_emails_by_date(start_date, end_date)
            eod_extractions = []
            
            for email_id in email_ids:
                email_data = self.fetch_email_content(email_id)
                if not email_data:
                    continue
                
                subject, body, email_date = email_data
                eod_section = self.extract_eod_section(body, subject)
                
                if eod_section:
                    extraction = {
                        'email_id': email_id,
                        'subject': subject,
                        'date': email_date.isoformat(),
                        'eod_section': eod_section
                    }
                    eod_extractions.append(extraction)
                    logging.info(f"Extracted EOD from email: {subject[:50]}...")
            
            logging.info(f"Successfully extracted EOD sections from {len(eod_extractions)} emails")
            return eod_extractions
            
        finally:
            self.disconnect_from_email()
    
    def output_results(self, results: List[Dict[str, Any]], format_type: str, output_file: Optional[str] = None):
        """Output results in the specified format."""
        if not results:
            print("No EOD sections found in the specified date range.")
            return
        
        output_content = ""
        
        if format_type.lower() == 'json':
            output_content = json.dumps(results, indent=2, default=str)
        
        elif format_type.lower() == 'csv':
            output_buffer = io.StringIO()
            writer = csv.writer(output_buffer)
            
            # Write header
            writer.writerow(['Date', 'Subject', 'Task Description', 'Time Spent', 'Email ID'])
            
            # Write data
            for result in results:
                for task in result['eod_section']['tasks']:
                    writer.writerow([
                        result['date'],
                        result['subject'],
                        task['description'],
                        task.get('time_spent', ''),
                        result['email_id']
                    ])
            
            output_content = output_buffer.getvalue()
        
        elif format_type.lower() == 'text':
            output_lines = []
            for result in results:
                output_lines.append(f"Date: {result['date']}")
                output_lines.append(f"Subject: {result['subject']}")
                output_lines.append(f"EOD Section:")
                
                for task in result['eod_section']['tasks']:
                    time_info = f" - {task['time_spent']}" if task.get('time_spent') else ""
                    output_lines.append(f"  • {task['description']}{time_info}")
                
                output_lines.append("")  # Empty line between emails
            
            output_content = "\n".join(output_lines)
        
        else:
            logging.error(f"Unsupported output format: {format_type}")
            return
        
        # Output to file or stdout
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    f.write(output_content)
                logging.info(f"Results written to {output_file}")
            except Exception as e:
                logging.error(f"Error writing to file {output_file}: {e}")
        else:
            print(output_content)


def parse_date(date_string: str) -> datetime:
    """Parse date string into datetime object."""
    try:
        return date_parser.parse(date_string)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_string}")


def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(
        description="Extract EOD (End of Day) sections from emails within a date range",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --start 2024-01-01 --end 2024-01-31
  %(prog)s --start "2024-01-01" --end "2024-01-31" --format json --output results.json
  %(prog)s --start "last week" --end "today" --format csv
        """
    )
    
    parser.add_argument(
        '--start', '--start-date',
        type=parse_date,
        required=True,
        help='Start date for email search (e.g., "2024-01-01", "last week")'
    )
    
    parser.add_argument(
        '--end', '--end-date',
        type=parse_date,
        required=True,
        help='End date for email search (e.g., "2024-01-31", "today")'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json', 'csv'],
        default='json',
        help='Output format (default: json)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file path (default: print to stdout)'
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Configuration file path (default: config.yaml)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate date range
    if args.start >= args.end:
        print("Error: Start date must be before end date")
        sys.exit(1)
    
    # Initialize extractor
    try:
        extractor = EODExtractor(args.config)
    except SystemExit:
        return
    
    # Extract EOD sections
    logging.info(f"Extracting EOD sections from {args.start.date()} to {args.end.date()}")
    results = extractor.extract_eod_from_date_range(args.start, args.end)
    
    # Output results
    extractor.output_results(results, args.format, args.output)


if __name__ == '__main__':
    main()