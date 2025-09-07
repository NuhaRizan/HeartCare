#!/usr/bin/env python3
"""
Test script for Infobip WhatsApp formatted messaging
This script demonstrates the new WhatsApp functionality with interactive buttons and formatted messages.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.infobip_service import infobip_service

def test_whatsapp_report():
    """Test the new formatted WhatsApp report functionality"""
    
    # Test data
    test_phone = "+1234567890"  # Replace with actual test number
    test_prediction = "0.75"
    test_reasoning = "High risk factors detected: Age above 50, elevated blood pressure, and high cholesterol levels. Exercise induced angina present."
    test_download_url = "https://yourdomain.com/download_report/test-uuid-123"
    test_risk_level = "High Risk"
    
    print("🧪 Testing Infobip WhatsApp Report Functionality")
    print("=" * 50)
    
    print(f"📱 Phone: {test_phone}")
    print(f"🎯 Risk Level: {test_risk_level}")
    print(f"📊 Prediction: {test_prediction}")
    print(f"🔗 Download URL: {test_download_url}")
    print(f"📝 Reasoning: {test_reasoning[:50]}...")
    print()
    
    # Test the new formatted report method
    print("📤 Sending formatted WhatsApp report...")
    result = infobip_service.send_whatsapp_report(
        test_phone,
        test_prediction,
        test_reasoning,
        test_download_url,
        test_risk_level
    )
    
    print("📋 Result:")
    print(f"   Success: {result['success']}")
    if result['success']:
        print(f"   Message ID: {result.get('message_id', 'N/A')}")
        print(f"   Type: {result.get('type', 'N/A')}")
        print(f"   Status: {result.get('status', 'N/A')}")
        print("   ✅ Formatted WhatsApp message sent successfully!")
    else:
        print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
    
    print()
    print("📋 Message Features:")
    print("   • Interactive button for download link")
    print("   • Formatted text with emojis and styling")
    print("   • Risk level highlighting")
    print("   • Truncated reasoning for readability")
    print("   • Professional medical disclaimer")
    print("   • 24-hour expiration notice")

def test_regular_whatsapp():
    """Test the regular WhatsApp messaging functionality"""
    
    test_phone = "+1234567890"  # Replace with actual test number
    test_prediction = "0.25"
    test_reasoning = "Low risk factors detected. Continue maintaining a healthy lifestyle with regular exercise and balanced diet."
    
    print("🧪 Testing Regular WhatsApp Messaging")
    print("=" * 40)
    
    print(f"📱 Phone: {test_phone}")
    print(f"📊 Prediction: {test_prediction}")
    print(f"📝 Reasoning: {test_reasoning[:50]}...")
    print()
    
    # Test the regular WhatsApp method
    print("📤 Sending regular WhatsApp message...")
    result = infobip_service.send_whatsapp(test_phone, test_reasoning)
    
    print("📋 Result:")
    print(f"   Success: {result['success']}")
    if result['success']:
        print(f"   Message ID: {result.get('message_id', 'N/A')}")
        print(f"   Status: {result.get('status', 'N/A')}")
        print("   ✅ Regular WhatsApp message sent successfully!")
    else:
        print(f"   ❌ Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    print("🚀 Infobip WhatsApp Testing Suite")
    print("=" * 50)
    print()
    
    # Check if Infobip is configured
    if not infobip_service.api_key or infobip_service.api_key == "your_infobip_api_key":
        print("❌ Infobip API key not configured!")
        print("   Please set INFOBIP_API_KEY in config.py")
        sys.exit(1)
    
    if not infobip_service.whatsapp_number or infobip_service.whatsapp_number == "your_whatsapp_number":
        print("❌ WhatsApp number not configured!")
        print("   Please set INFOBIP_WHATSAPP_NUMBER in config.py")
        sys.exit(1)
    
    print("✅ Infobip configuration found!")
    print()
    
    # Run tests
    test_whatsapp_report()
    print()
    test_regular_whatsapp()
    
    print()
    print("🎉 Testing complete!")
    print("💡 To test with real numbers, update the test_phone variables in this script.") 