#!/usr/bin/env python3
"""
Test script for simple WhatsApp messaging
This script tests sending simple WhatsApp messages with download links.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.infobip_service import infobip_service
from config import LOCAL_SERVER_HOST, LOCAL_SERVER_PORT, LOCAL_SERVER_PROTOCOL

def test_simple_whatsapp_report():
    """Test simple WhatsApp message with download link"""
    
    print("🧪 Testing Simple WhatsApp Report")
    print("=" * 40)
    
    # Test data
    test_phone = "+94773274283"  # Replace with actual test number
    test_prediction = "0.75"
    test_reasoning = "High risk factors detected: Age above 50, elevated blood pressure, and high cholesterol levels."
    test_download_url = f"{LOCAL_SERVER_PROTOCOL}://{LOCAL_SERVER_HOST}:{LOCAL_SERVER_PORT}/download_report/test-uuid-123"
    test_risk_level = "High Risk"
    
    print(f"📱 Phone: {test_phone}")
    print(f"🔗 Download URL: {test_download_url}")
    print()
    
    # Test simple message
    print("📤 Sending simple WhatsApp message...")
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
        print("   ✅ Simple message sent with download link!")
    else:
        print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
    
    print()
    print("📋 Message Content:")
    print("   Here is your report download here: [download_url]")
    print("   • Simple and direct")
    print("   • Clean format")
    print("   • Easy to read")

def test_simple_whatsapp_text():
    """Test simple WhatsApp text message (fallback)"""
    
    print("\n🧪 Testing Simple WhatsApp Text (Fallback)")
    print("=" * 45)
    
    # Test data
    test_phone = "+94773274283"  # Replace with actual test number
    test_prediction = "0.25"
    test_reasoning = "Low risk factors detected. Continue maintaining a healthy lifestyle."
    test_download_url = f"{LOCAL_SERVER_PROTOCOL}://{LOCAL_SERVER_HOST}:{LOCAL_SERVER_PORT}/download_report/test-uuid-456"
    test_risk_level = "Low Risk"
    
    print(f"📱 Phone: {test_phone}")
    print(f"🔗 Download URL: {test_download_url}")
    print()
    
    # Test text message
    print("📤 Sending simple text message...")
    result = infobip_service.send_whatsapp_formatted_text(
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
        print("   ✅ Simple text message sent!")
    else:
        print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
    
    print()
    print("📋 Text Message Content:")
    print("   Here is your report download here: [download_url]")
    print("   • Plain text format")
    print("   • No formatting")
    print("   • Works with all clients")

def test_regular_whatsapp():
    """Test regular WhatsApp message without download link"""
    
    print("\n🧪 Testing Regular WhatsApp Message")
    print("=" * 40)
    
    # Test data
    test_phone = "+94773274283"  # Replace with actual test number
    test_prediction = "0.50"
    test_reasoning = "Moderate risk factors detected. Some concerning indicators present."
    
    print(f"📱 Phone: {test_phone}")
    print()
    
    # Create simple message
    simple_message = f"Here is your heart care prediction report. Your risk level: {'High Risk' if float(test_prediction) >= 0.5 else 'Low Risk'}. {test_reasoning[:100]}{'...' if len(test_reasoning) > 100 else ''}"
    
    print("📤 Sending regular WhatsApp message...")
    result = infobip_service.send_whatsapp(test_phone, simple_message)
    
    print("📋 Result:")
    print(f"   Success: {result['success']}")
    if result['success']:
        print(f"   Message ID: {result.get('message_id', 'N/A')}")
        print(f"   Status: {result.get('status', 'N/A')}")
        print("   ✅ Regular message sent!")
    else:
        print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
    
    print()
    print("📋 Regular Message Content:")
    print(f"   {simple_message}")
    print("   • Simple prediction report")
    print("   • No download link")
    print("   • Basic information only")

def test_local_server_config():
    """Test local server configuration"""
    
    print("\n🖥️  Testing Local Server Configuration")
    print("=" * 45)
    
    print(f"🌐 Host: {LOCAL_SERVER_HOST}")
    print(f"🔌 Port: {LOCAL_SERVER_PORT}")
    print(f"🔗 Protocol: {LOCAL_SERVER_PROTOCOL}")
    print()
    
    # Generate sample download URL
    sample_url = f"{LOCAL_SERVER_PROTOCOL}://{LOCAL_SERVER_HOST}:{LOCAL_SERVER_PORT}/download_report/test-uuid-123"
    print(f"📥 Sample download URL: {sample_url}")
    print()
    print("💡 This URL will be sent in WhatsApp messages")
    print("📱 Users can click this link to download their report")

if __name__ == "__main__":
    print("🚀 Simple WhatsApp Test Suite (Local Server)")
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
    
    # Test local server config
    test_local_server_config()
    
    # Run tests
    test_simple_whatsapp_report()
    test_simple_whatsapp_text()
    test_regular_whatsapp()
    
    print()
    print("🎉 Testing complete!")
    print("💡 To test with real numbers, update the test_phone variables in this script.")
    print("📱 All messages now use your local server for download links!")
    print()
    print("🌐 Make sure your Flask app is running:")
    print("   python app.py")
    print("   or")
    print("   flask run --host=0.0.0.0 --port=5000") 