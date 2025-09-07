#!/usr/bin/env python3
"""
SendGrid Sender Setup and Test Script
This script helps you set up and test SendGrid email sending with verified sender identity.
"""

import os
import sys
from services.twilio_service import twilio_service

def setup_sendgrid_sender():
    """Setup SendGrid sender verification"""
    print("🔧 SendGrid Sender Identity Setup")
    print("=" * 50)
    
    print("\n📋 Steps to verify your sender identity:")
    print("1. Go to https://app.sendgrid.com/settings/sender_auth")
    print("2. Click 'Verify a Single Sender'")
    print("3. Fill in the form with your details:")
    print("   - From Name: Heart Care+ Team")
    print("   - From Email: your_email@yourdomain.com")
    print("   - Reply To: your_email@yourdomain.com")
    print("   - Company: Heart Care+")
    print("4. Check your email and click the verification link")
    
    print("\n⚙️  Configuration:")
    print("After verification, update your config.py or set environment variables:")
    print("SENDER_EMAIL=your_verified_email@yourdomain.com")
    print("SENDER_NAME=Heart Care+ Team")
    
    # Get current configuration
    from config import SENDER_EMAIL, SENDER_NAME, SMTP_SERVER, SMTP_USERNAME
    
    print(f"\n📊 Current Configuration:")
    print(f"SMTP Server: {SMTP_SERVER}")
    print(f"SMTP Username: {SMTP_USERNAME}")
    print(f"Sender Email: {SENDER_EMAIL}")
    print(f"Sender Name: {SENDER_NAME}")
    
    if SENDER_EMAIL == 'your_verified_email@yourdomain.com':
        print("\n⚠️  WARNING: You need to update SENDER_EMAIL with your verified email address!")
        return False
    
    return True

def test_email_sending():
    """Test email sending with current configuration"""
    print("\n🧪 Testing Email Sending")
    print("=" * 30)
    
    # Get test email from user
    test_email = input("Enter test email address: ").strip()
    
    if not test_email:
        print("❌ No email address provided")
        return False
    
    # Test email content
    subject = "Heart Care+ - Email Test"
    message = f"""
Hello!

This is a test email from your Heart Care+ application.

If you received this email, your SendGrid configuration is working correctly!

Best regards,
Heart Care+ Team
    """.strip()
    
    print(f"\n📧 Sending test email to: {test_email}")
    print(f"Subject: {subject}")
    
    try:
        result = twilio_service.send_email(test_email, subject, message)
        
        if result['success']:
            print("✅ Email sent successfully!")
            print(f"Message: {result['message']}")
            return True
        else:
            print("❌ Failed to send email:")
            print(f"Error: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 SendGrid Email Setup and Test")
    print("=" * 40)
    
    # Check if sender is configured
    if not setup_sendgrid_sender():
        print("\n❌ Please complete sender verification first!")
        return
    
    # Ask if user wants to test
    test = input("\n🧪 Would you like to test email sending? (y/n): ").strip().lower()
    
    if test == 'y':
        test_email_sending()
    else:
        print("\n✅ Setup complete! You can now send emails from your application.")

if __name__ == "__main__":
    main() 