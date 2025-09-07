#!/usr/bin/env python3
"""
Test script to verify email sending with download links
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import LOCAL_SERVER_HOST, LOCAL_SERVER_PORT, LOCAL_SERVER_PROTOCOL, SENDER_EMAIL, SENDER_NAME
from services.twilio_service import twilio_service
import uuid

def test_email_with_download_link():
    """Test sending email with download link"""
    
    print("🧪 Testing Email with Download Link")
    print("=" * 50)
    
    # Test data
    test_email = input("Enter test email address: ").strip()
    if not test_email:
        print("❌ No email address provided")
        return False
    
    # Generate test report ID
    report_id = str(uuid.uuid4())
    
    # Create download link
    download_url = f"{LOCAL_SERVER_PROTOCOL}://{LOCAL_SERVER_HOST}:{LOCAL_SERVER_PORT}/download_report/{report_id}"
    
    print(f"📧 Test Email: {test_email}")
    print(f"🔗 Download URL: {download_url}")
    print(f"📤 Sender: {SENDER_NAME} <{SENDER_EMAIL}>")
    print()
    
    # Create email content
    subject = "Heart Care+ Report - Test"
    message_body = f"""
Dear User,

Your Heart Disease Risk Assessment Report is ready!

Risk Level: Test Risk
Prediction Score: 0.75

Reasoning: This is a test email to verify download link functionality.

Download your detailed report here: {download_url}

This link will expire in 24 hours.

Important Notes:
- This report is for informational purposes only
- Please consult with a healthcare professional for medical advice
- Keep your health information secure

Best regards,
Heart Care+ Team
    """.strip()
    
    print("📋 Email Content Preview:")
    print("-" * 30)
    print(f"Subject: {subject}")
    print(f"Body Length: {len(message_body)} characters")
    print(f"Download Link Present: {'✅' if download_url in message_body else '❌'}")
    print()
    
    # Send email
    print("📤 Sending test email...")
    result = twilio_service.send_email(test_email, subject, message_body)
    
    print("📋 Result:")
    print(f"   Success: {result['success']}")
    if result['success']:
        print(f"   Message: {result['message']}")
        print("   ✅ Email sent successfully!")
        print("   📧 Check your email for the download link")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    return result['success']

def test_local_server_config():
    """Test local server configuration"""
    
    print("\n🔧 Local Server Configuration")
    print("=" * 40)
    
    print(f"Protocol: {LOCAL_SERVER_PROTOCOL}")
    print(f"Host: {LOCAL_SERVER_HOST}")
    print(f"Port: {LOCAL_SERVER_PORT}")
    
    # Generate sample URLs
    sample_report_id = "test-uuid-123"
    sample_url = f"{LOCAL_SERVER_PROTOCOL}://{LOCAL_SERVER_HOST}:{LOCAL_SERVER_PORT}/download_report/{sample_report_id}"
    
    print(f"\n📋 Sample Download URL:")
    print(f"   {sample_url}")
    
    print(f"\n💡 Make sure your Flask app is running on port {LOCAL_SERVER_PORT}")
    print("   python app.py")

if __name__ == "__main__":
    print("📧 Email Download Link Test")
    print("=" * 40)
    
    test_local_server_config()
    
    print("\n" + "=" * 50)
    
    success = test_email_with_download_link()
    
    if success:
        print("\n✅ Email test completed successfully!")
        print("📧 Check your email for the download link")
    else:
        print("\n❌ Email test failed!")
        print("🔧 Check your SendGrid configuration and sender verification") 