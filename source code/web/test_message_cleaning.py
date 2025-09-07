#!/usr/bin/env python3
"""
Test script for message cleaning functionality
This script tests the clean_message_for_template function to ensure compliance with Infobip's validation requirements.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.infobip_service import InfobipService

def test_message_cleaning():
    """Test the message cleaning functionality"""
    
    print("🧪 Testing Message Cleaning Functionality")
    print("=" * 50)
    
    # Create service instance
    service = InfobipService()
    
    # Test cases
    test_cases = [
        {
            "name": "Message with newlines",
            "input": "🏥 Heart Care+ Report\n\nYour heart disease prediction: High Risk\n\n📊 Analysis:\nHigh risk factors detected.\n\nBest regards,\nHeart Care+ Team",
            "expected_issues": ["newlines", "multiple spaces"]
        },
        {
            "name": "Message with excessive spaces",
            "input": "🏥 Heart Care+ Report     Your heart disease prediction: High Risk.     📊 Analysis: High risk factors detected.",
            "expected_issues": ["multiple spaces"]
        },
        {
            "name": "Message with carriage returns",
            "input": "🏥 Heart Care+ Report\r\nYour heart disease prediction: High Risk.\r\n📊 Analysis: High risk factors detected.",
            "expected_issues": ["carriage returns", "newlines"]
        },
        {
            "name": "Very long message",
            "input": "🏥 Heart Care+ Report - " + "This is a very long message. " * 100,
            "expected_issues": ["too long"]
        },
        {
            "name": "Clean message",
            "input": "🏥 Heart Care+ Report - Your heart disease prediction: High Risk. 📊 Analysis: High risk factors detected.",
            "expected_issues": []
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        original = test_case['input']
        cleaned = service.clean_message_for_template(original)
        
        print(f"📝 Original length: {len(original)} characters")
        print(f"🧹 Cleaned length: {len(cleaned)} characters")
        print(f"📋 Original: {repr(original[:100])}{'...' if len(original) > 100 else ''}")
        print(f"🧹 Cleaned: {repr(cleaned[:100])}{'...' if len(cleaned) > 100 else ''}")
        
        # Check for issues
        issues_found = []
        if '\n' in cleaned:
            issues_found.append("newlines")
        if '\r' in cleaned:
            issues_found.append("carriage returns")
        if '    ' in cleaned:  # 4 or more spaces
            issues_found.append("multiple spaces")
        if len(cleaned) > 1000:
            issues_found.append("too long")
        
        if issues_found:
            print(f"⚠️  Issues found: {', '.join(issues_found)}")
        else:
            print("✅ No issues found - message is clean!")
        
        # Check if cleaning resolved expected issues
        expected_resolved = all(issue not in cleaned for issue in test_case['expected_issues'])
        if expected_resolved:
            print("✅ Expected issues resolved!")
        else:
            print("❌ Expected issues not resolved!")

if __name__ == "__main__":
    print("🚀 Message Cleaning Test Suite")
    print("=" * 50)
    
    test_message_cleaning()
    
    print("\n🎉 Testing complete!") 