#!/usr/bin/env python3
"""
Demo script showing EOD extractor functionality without requiring email access
"""

import json
from datetime import datetime
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eod_extractor import EODExtractor


def demo_eod_extraction():
    """Demonstrate EOD extraction with the exact examples from the issue."""
    print("🚀 EOD Email Extractor Demo")
    print("=" * 50)
    
    # Create sample emails matching the issue examples
    sample_emails = [
        {
            "subject": "Daily Status Update - 2024-01-15",
            "date": "2024-01-15T09:30:00",
            "body": """
Hi Team,

Here's my daily status update:

EOD:
- Checking tracker and tickets-20 min
- Team meeting and discussion-30 min
- TLS #49172 - TLS Error- 01:25 hrs
- Discussion with Ritu regarding their ticket-45 min
- TLS#66638-Require to move TLS project from DCPL framework to DFramework-04:20 hrs
- Discuss with Aayush regarding #66912-20 min
- TLS #66951-System Performance Optimization - DO NOT use lock hints such as NOLOCK/ ROWLOCK-02:20 hrs

Thanks,
John
"""
        },
        {
            "subject": "Weekly Summary - 2024-01-16",
            "date": "2024-01-16T17:00:00",
            "body": """
Team,

End of Day Summary:
• Code review session - 45 min
• Bug fix for issue #12345 - 2.5 hrs
• Client meeting preparation - 30min
• Database optimization task - 01:15 hrs

Best regards,
Sarah
"""
        }
    ]
    
    # Test configuration
    test_config = {
        'parsing': {
            'eod_keywords': ['EOD', 'End of Day', 'Daily Summary', 'Task Summary', 'End of Day Summary'],
            'time_patterns': [
                '\\d+\\s*min',
                '\\d+:\\d+\\s*hrs?',
                '\\d+\\.\\d+\\s*hrs?',
                '\\d+\\s*hrs?'
            ]
        },
        'output': {
            'default_format': 'json',
            'include_metadata': True,
            'file_path': None
        }
    }
    
    # Mock extractor
    class DemoEODExtractor(EODExtractor):
        def __init__(self):
            self.config = test_config
    
    extractor = DemoEODExtractor()
    results = []
    
    print("📧 Processing sample emails...")
    print()
    
    for i, email in enumerate(sample_emails, 1):
        print(f"Email {i}: {email['subject']}")
        
        eod_section = extractor.extract_eod_section(email['body'], email['subject'])
        
        if eod_section:
            print(f"✅ EOD section found with {len(eod_section['tasks'])} tasks")
            
            result = {
                'email_id': f'demo_{i}',
                'subject': email['subject'],
                'date': email['date'],
                'eod_section': eod_section
            }
            results.append(result)
            
            # Show extracted tasks
            for j, task in enumerate(eod_section['tasks'], 1):
                time_info = f" ({task['time_spent']})" if task.get('time_spent') else ""
                print(f"   {j}. {task['description']}{time_info}")
        else:
            print("❌ No EOD section found")
        
        print()
    
    # Demo different output formats
    print("📋 Output Format Examples:")
    print("-" * 30)
    
    if results:
        print("\n🔹 JSON Format:")
        extractor.output_results(results, 'json')
        
        print("\n🔹 CSV Format:")
        extractor.output_results(results, 'csv')
        
        print("\n🔹 Text Format:")
        extractor.output_results(results, 'text')
    
    print("\n" + "=" * 50)
    print("✨ Demo completed successfully!")
    print("\nTo use with real emails:")
    print("1. Copy config.yaml.template to config.yaml")
    print("2. Configure your email settings")
    print("3. Run: python eod_extractor.py --start '2024-01-01' --end '2024-01-31'")


if __name__ == '__main__':
    demo_eod_extraction()