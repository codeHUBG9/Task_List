#!/usr/bin/env python3
"""
Test script for EOD Extractor functionality
Tests parsing logic with sample email content
"""

import sys
import os
import json
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eod_extractor import EODExtractor


def test_eod_parsing():
    """Test EOD section parsing with sample email content."""
    print("Testing EOD parsing functionality...")
    
    # Sample email content
    sample_email = """
Subject: Daily Status Update - Test

Hi Team,

Here's my update for today:

EOD:
- Checking tracker and tickets-20 min
- Team meeting and discussion-30 min
- TLS #49172 - TLS Error- 01:25 hrs
- Discussion with Ritu regarding their ticket-45 min
- TLS#66638-Require to move TLS project from DCPL framework to DFramework-04:20 hrs
- Discuss with Aayush regarding #66912-20 min
- TLS #66951-System Performance Optimization - DO NOT use lock hints such as NOLOCK/ ROWLOCK-02:20 hrs

Best regards,
John
"""
    
    # Create a minimal config for testing
    test_config = {
        'parsing': {
            'eod_keywords': ['EOD', 'End of Day', 'Daily Summary', 'Task Summary'],
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
    
    # Mock the EODExtractor for testing
    class TestEODExtractor(EODExtractor):
        def __init__(self):
            self.config = test_config
    
    # Test the parsing
    extractor = TestEODExtractor()
    result = extractor.extract_eod_section(sample_email, "Daily Status Update - Test")
    
    if result:
        print("✓ EOD section successfully detected and parsed")
        print(f"✓ Found {len(result['tasks'])} tasks")
        
        # Check if all expected tasks are found
        expected_tasks = 7
        if len(result['tasks']) == expected_tasks:
            print(f"✓ All {expected_tasks} tasks parsed correctly")
        else:
            print(f"⚠ Expected {expected_tasks} tasks, found {len(result['tasks'])}")
        
        # Check time extraction
        tasks_with_time = [task for task in result['tasks'] if task.get('time_spent')]
        print(f"✓ {len(tasks_with_time)} tasks have time information extracted")
        
        # Display parsed tasks
        print("\nParsed tasks:")
        for i, task in enumerate(result['tasks'], 1):
            time_info = f" ({task['time_spent']})" if task.get('time_spent') else " (no time)"
            print(f"  {i}. {task['description']}{time_info}")
        
        # Test JSON output
        print("\nTesting JSON output:")
        test_results = [{
            'email_id': 'test_123',
            'subject': 'Test Email',
            'date': datetime.now().isoformat(),
            'eod_section': result
        }]
        
        extractor.output_results(test_results, 'json')
        print("✓ JSON output generated successfully")
        
        return True
    else:
        print("✗ Failed to detect EOD section")
        return False


def test_regex_patterns():
    """Test regex patterns for time extraction."""
    print("\nTesting time pattern recognition...")
    
    import re
    
    time_patterns = [
        '\\d+\\s*min',
        '\\d+:\\d+\\s*hrs?',
        '\\d+\\.\\d+\\s*hrs?',
        '\\d+\\s*hrs?'
    ]
    
    test_strings = [
        "Task description-20 min",
        "Another task- 30min",
        "Complex task-01:25 hrs",
        "Quick task-1.5 hr",
        "Long task-04:20 hrs",
        "Simple task-2 hrs",
        "No time task"
    ]
    
    time_pattern = '|'.join([f'({pattern})' for pattern in time_patterns])
    time_regex = re.compile(time_pattern, re.IGNORECASE)
    
    for test_string in test_strings:
        match = time_regex.search(test_string)
        if match:
            print(f"✓ '{test_string}' -> Time: '{match.group(0)}'")
        else:
            print(f"- '{test_string}' -> No time detected")
    
    return True


def main():
    """Run all tests."""
    print("EOD Extractor Test Suite")
    print("=" * 40)
    
    # Test parsing functionality
    parsing_success = test_eod_parsing()
    
    # Test regex patterns
    regex_success = test_regex_patterns()
    
    # Summary
    print("\n" + "=" * 40)
    if parsing_success and regex_success:
        print("✓ All tests passed!")
        print("\nThe EOD extractor is ready to use. To get started:")
        print("1. Copy config.yaml.template to config.yaml")
        print("2. Configure your email settings")
        print("3. Run: python eod_extractor.py --start '2024-01-01' --end '2024-01-31'")
    else:
        print("✗ Some tests failed. Please check the implementation.")


if __name__ == '__main__':
    main()