#!/usr/bin/env python3
"""
Test script for Infobip API connection and template functionality
This script tests the exact API format provided by the user.
"""

import http.client
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import INFOBIP_API_KEY, INFOBIP_BASE_URL, INFOBIP_WHATSAPP_NUMBER

def test_basic_connection():
    """Test basic API connection using the exact format provided"""
    
    print("🧪 Testing Infobip API Connection")
    print("=" * 50)
    
    # Test data (replace with actual test number)
    test_phone = "94773274283"  # Sri Lanka number format
    
    print(f"📱 From: {INFOBIP_WHATSAPP_NUMBER}")
    print(f"📱 To: {test_phone}")
    print(f"🔑 API Key: {INFOBIP_API_KEY[:10]}...")
    print(f"🌐 Base URL: {INFOBIP_BASE_URL}")
    print()
    
    try:
        conn = http.client.HTTPSConnection("api.infobip.com")
        
        payload = json.dumps({
            "messages": [
                {
                    "from": INFOBIP_WHATSAPP_NUMBER,
                    "to": test_phone,
                    "messageId": "ccf65936-5cc0-43f7-ae2c-02c97d434dab",
                    "content": {
                        "templateName": "test_whatsapp_template_en",
                        "templateData": {
                            "body": {
                                "placeholders": ["Heart Care+ Test Message"]
                            }
                        },
                        "language": "en"
                    }
                }
            ]
        })
        
        headers = {
            'Authorization': f'App {INFOBIP_API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print("📤 Sending test message...")
        print(f"📋 Payload: {payload}")
        print()
        
        conn.request("POST", "/whatsapp/1/message/template", payload, headers)
        response = conn.getresponse()
        data = response.read()
        
        print(f"📊 Response Status: {response.status}")
        print(f"📋 Response Data: {data.decode('utf-8')}")
        print()
        
        if response.status == 200:
            result = json.loads(data.decode("utf-8"))
            print("✅ Success! Message sent successfully.")
            print(f"📝 Message ID: {result.get('messages', [{}])[0].get('messageId', 'N/A')}")
        else:
            print(f"❌ Error: HTTP {response.status}")
            print(f"📝 Error Details: {data.decode('utf-8')}")
            
            # Try to parse error response
            try:
                error_data = json.loads(data.decode('utf-8'))
                if 'requestError' in error_data:
                    print(f"🔍 Error Type: {error_data['requestError'].get('serviceException', {}).get('textId', 'Unknown')}")
                    print(f"🔍 Error Message: {error_data['requestError'].get('serviceException', {}).get('text', 'Unknown')}")
            except:
                pass
                
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")

def test_formatted_message():
    """Test sending a formatted message with heart care prediction"""
    
    print("\n🧪 Testing Formatted Heart Care+ Message")
    print("=" * 50)
    
    test_phone = "94773274283"  # Replace with actual test number
    
    try:
        conn = http.client.HTTPSConnection("api.infobip.com")
        
        # Create formatted message
        formatted_message = "🏥 Heart Care+ Report - Your heart disease prediction: High Risk. 📊 Analysis: High risk factors detected: Age above 50, elevated blood pressure, and high cholesterol levels. ⚠️ Important: This report is for informational purposes only. Please consult with a healthcare professional for medical advice. Best regards, Heart Care+ Team"
        
        payload = json.dumps({
            "messages": [
                {
                    "from": INFOBIP_WHATSAPP_NUMBER,
                    "to": test_phone,
                    "messageId": "heart_care_formatted_test",
                    "content": {
                        "templateName": "test_whatsapp_template_en",
                        "templateData": {
                            "body": {
                                "placeholders": [formatted_message]
                            }
                        },
                        "language": "en"
                    }
                }
            ]
        })
        
        headers = {
            'Authorization': f'App {INFOBIP_API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print("📤 Sending formatted heart care message...")
        
        conn.request("POST", "/whatsapp/1/message/template", payload, headers)
        response = conn.getresponse()
        data = response.read()
        
        print(f"📊 Response Status: {response.status}")
        
        if response.status == 200:
            result = json.loads(data.decode("utf-8"))
            print("✅ Success! Formatted message sent successfully.")
            print(f"📝 Message ID: {result.get('messages', [{}])[0].get('messageId', 'N/A')}")
        else:
            print(f"❌ Error: HTTP {response.status}")
            print(f"📝 Error Details: {data.decode('utf-8')}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_text_message():
    """Test sending a text message as fallback"""
    
    print("\n🧪 Testing Text Message (Fallback)")
    print("=" * 40)
    
    test_phone = "94773274283"  # Replace with actual test number
    
    try:
        conn = http.client.HTTPSConnection("api.infobip.com")
        
        formatted_message = """🏥 *Heart Care+ Report*

Your heart disease prediction: *High Risk*

📊 Analysis:
High risk factors detected: Age above 50, elevated blood pressure, and high cholesterol levels.

⚠️ Important: This report is for informational purposes only. Please consult with a healthcare professional for medical advice.

Best regards,
Heart Care+ Team"""
        
        payload = json.dumps({
            "messages": [
                {
                    "from": INFOBIP_WHATSAPP_NUMBER,
                    "to": test_phone,
                    "messageId": "heart_care_text_test",
                    "content": {
                        "type": "TEXT",
                        "text": formatted_message
                    }
                }
            ]
        })
        
        headers = {
            'Authorization': f'App {INFOBIP_API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print("📤 Sending text message...")
        
        conn.request("POST", "/whatsapp/1/message", payload, headers)
        response = conn.getresponse()
        data = response.read()
        
        print(f"📊 Response Status: {response.status}")
        
        if response.status == 200:
            result = json.loads(data.decode("utf-8"))
            print("✅ Success! Text message sent successfully.")
            print(f"📝 Message ID: {result.get('messages', [{}])[0].get('messageId', 'N/A')}")
        else:
            print(f"❌ Error: HTTP {response.status}")
            print(f"📝 Error Details: {data.decode('utf-8')}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Infobip API Connection Test Suite")
    print("=" * 50)
    print()
    
    # Check configuration
    if not INFOBIP_API_KEY or INFOBIP_API_KEY == "your_infobip_api_key":
        print("❌ Infobip API key not configured!")
        print("   Please set INFOBIP_API_KEY in config.py")
        sys.exit(1)
    
    if not INFOBIP_WHATSAPP_NUMBER or INFOBIP_WHATSAPP_NUMBER == "your_whatsapp_number":
        print("❌ WhatsApp number not configured!")
        print("   Please set INFOBIP_WHATSAPP_NUMBER in config.py")
        sys.exit(1)
    
    print("✅ Configuration found!")
    print()
    
    # Run tests
    test_basic_connection()
    test_formatted_message()
    test_text_message()
    
    print()
    print("🎉 Testing complete!")
    print("💡 To test with real numbers, update the test_phone variables in this script.") 