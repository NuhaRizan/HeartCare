import http.client
import json
import re
from config import INFOBIP_API_KEY, INFOBIP_BASE_URL, INFOBIP_WHATSAPP_NUMBER

class InfobipService:
    def __init__(self):
        self.api_key = INFOBIP_API_KEY
        self.base_url = INFOBIP_BASE_URL.replace('https://', '')  # Remove https:// for http.client
        self.whatsapp_number = INFOBIP_WHATSAPP_NUMBER
        self.headers = {
            'Authorization': f'App {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def clean_message_for_template(self, message):
        """
        Clean message to comply with Infobip template validation requirements
        - Remove newlines and carriage returns
        - Remove excessive spaces (more than 4 consecutive)
        - Truncate if too long
        """
        # Remove newlines and carriage returns
        clean_message = message.replace('\n', ' ').replace('\r', ' ')
        # Remove multiple consecutive spaces
        clean_message = re.sub(r'\s+', ' ', clean_message).strip()
        # Truncate if too long (Infobip has limits)
        if len(clean_message) > 1000:
            clean_message = clean_message[:997] + "..."
        return clean_message
    
    def send_whatsapp(self, to_number, message):
        """
        Send WhatsApp message using Infobip template
        """
        try:
            # Ensure phone number is in international format
            if not to_number.startswith('+'):
                to_number = '+' + to_number
            
            # Clean the message to remove newlines and excessive spaces
            clean_message = self.clean_message_for_template(message)
            
            conn = http.client.HTTPSConnection(self.base_url)
            
            payload = json.dumps({
                "messages": [
                    {
                        "from": self.whatsapp_number,
                        "to": to_number,
                        "messageId": f"heart_care_{to_number.replace('+', '')}",
                        "content": {
                            "templateName": "test_whatsapp_template_en",
                            "templateData": {
                                "body": {
                                    "placeholders": [clean_message]
                                }
                            },
                            "language": "en"
                        }
                    }
                ]
            })
            
            conn.request("POST", "/whatsapp/1/message/template", payload, self.headers)
            response = conn.getresponse()
            data = response.read()
            result = json.loads(data.decode("utf-8"))
            
            if response.status == 200:
                return {
                    'success': True,
                    'message_id': result.get('messages', [{}])[0].get('messageId'),
                    'status': 'sent'
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status}: {data.decode("utf-8")}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_whatsapp_template(self, to_number, template_name, language_code="en", variables=None):
        """
        Send WhatsApp template message using Infobip
        """
        try:
            # Ensure phone number is in international format
            if not to_number.startswith('+'):
                to_number = '+' + to_number
            
            conn = http.client.HTTPSConnection(self.base_url)
            
            payload = {
                "messages": [
                    {
                        "from": self.whatsapp_number,
                        "to": to_number,
                        "messageId": f"template_{to_number.replace('+', '')}",
                        "content": {
                            "templateName": template_name,
                            "language": language_code
                        }
                    }
                ]
            }
            
            # Add variables if provided
            if variables:
                payload["messages"][0]["content"]["templateData"] = {
                    "body": {
                        "placeholders": variables
                    }
                }
            
            payload_json = json.dumps(payload)
            conn.request("POST", "/whatsapp/1/message/template", payload_json, self.headers)
            response = conn.getresponse()
            data = response.read()
            result = json.loads(data.decode("utf-8"))
            
            if response.status == 200:
                return {
                    'success': True,
                    'message_id': result.get('messages', [{}])[0].get('messageId'),
                    'status': 'sent'
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status}: {data.decode("utf-8")}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def send_whatsapp_interactive_report(self, to_number, prediction, reasoning, download_url, risk_level):
        """
        Send interactive WhatsApp message with clickable download button
        """
        try:
            # Ensure phone number is in international format
            if not to_number.startswith('+'):
                to_number = '+' + to_number
            
            conn = http.client.HTTPSConnection(self.base_url)
            
            # Create interactive message with button
            payload = json.dumps({
                "messages": [
                    {
                        "from": self.whatsapp_number,
                        "to": to_number,
                        "messageId": f"interactive_report_{to_number.replace('+', '')}",
                        "content": {
                            "type": "INTERACTIVE",
                            "interactive": {
                                "type": "BUTTON",
                                "header": {
                                    "type": "TEXT",
                                    "text": "🏥 Heart Care+ Report"
                                },
                                "body": {
                                    "text": f"Your heart disease prediction: {risk_level}\n\n{reasoning[:100]}{'...' if len(reasoning) > 100 else ''}\n\nClick the button below to download your full report."
                                },
                                "action": {
                                    "buttons": [
                                        {
                                            "type": "URL",
                                            "reply": {
                                                "id": "download_report",
                                                "title": "📥 Download Report"
                                            },
                                            "url": download_url
                                        }
                                    ]
                                }
                            }
                        }
                    }
                ]
            })
            
            conn.request("POST", "/whatsapp/1/message", payload, self.headers)
            response = conn.getresponse()
            data = response.read()
            result = json.loads(data.decode("utf-8"))
            
            if response.status == 200:
                return {
                    'success': True,
                    'message_id': result.get('messages', [{}])[0].get('messageId'),
                    'status': 'sent',
                    'type': 'interactive'
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status}: {data.decode("utf-8")}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def send_whatsapp_report(self, to_number, prediction, reasoning, download_url, risk_level):
        """
        Send simple WhatsApp message with report download link
        """
        try:
            # Ensure phone number is in international format
            if not to_number.startswith('+'):
                to_number = '+' + to_number
            
            # Create simple message with download link
            simple_message = f"Here is your report download here: {download_url}"
            
            # Clean the message for template compliance
            clean_message = self.clean_message_for_template(simple_message)
            
            conn = http.client.HTTPSConnection(self.base_url)
            
            payload = json.dumps({
                "messages": [
                    {
                        "from": self.whatsapp_number,
                        "to": to_number,
                        "messageId": f"report_{to_number.replace('+', '')}",
                        "content": {
                            "templateName": "test_whatsapp_template_en",
                            "templateData": {
                                "body": {
                                    "placeholders": [clean_message]
                                }
                            },
                            "language": "en"
                        }
                    }
                ]
            })
            
            conn.request("POST", "/whatsapp/1/message/template", payload, self.headers)
            response = conn.getresponse()
            data = response.read()
            result = json.loads(data.decode("utf-8"))
            
            if response.status == 200:
                return {
                    'success': True,
                    'message_id': result.get('messages', [{}])[0].get('messageId'),
                    'status': 'sent',
                    'type': 'template'
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status}: {data.decode("utf-8")}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def send_whatsapp_formatted_text(self, to_number, prediction, reasoning, download_url, risk_level):
        """
        Send simple WhatsApp message as text (fallback method)
        """
        try:
            # Ensure phone number is in international format
            if not to_number.startswith('+'):
                to_number = '+' + to_number
            
            # Create simple message with download link
            simple_message = f"Here is your report download here: {download_url}"
            
            conn = http.client.HTTPSConnection(self.base_url)
            
            payload = json.dumps({
                "messages": [
                    {
                        "from": self.whatsapp_number,
                        "to": to_number,
                        "messageId": f"report_text_{to_number.replace('+', '')}",
                        "content": {
                            "type": "TEXT",
                            "text": simple_message
                        }
                    }
                ]
            })
            
            conn.request("POST", "/whatsapp/1/message", payload, self.headers)
            response = conn.getresponse()
            data = response.read()
            result = json.loads(data.decode("utf-8"))
            
            if response.status == 200:
                return {
                    'success': True,
                    'message_id': result.get('messages', [{}])[0].get('messageId'),
                    'status': 'sent',
                    'type': 'text'
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status}: {data.decode("utf-8")}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def send_sms(self, to_number, message):
        """
        Send SMS using Infobip SMS API
        """
        try:
            # Ensure phone number is in international format
            if not to_number.startswith('+'):
                to_number = '+' + to_number
            
            conn = http.client.HTTPSConnection(self.base_url)
            
            payload = json.dumps({
                "messages": [
                    {
                        "from": self.whatsapp_number,  # You may need a dedicated SMS sender number from Infobip
                        "destinations": [
                            {"to": to_number}
                        ],
                        "text": message
                    }
                ]
            })
            
            conn.request("POST", "/sms/2/text/advanced", payload, self.headers)
            response = conn.getresponse()
            data = response.read()
            result = json.loads(data.decode("utf-8"))
            
            if response.status in [200, 201]:
                return {
                    'success': True,
                    'message_id': result.get('messages', [{}])[0].get('messageId', None),
                    'status': 'sent'
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status}: {data.decode("utf-8")}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Create a global instance
infobip_service = InfobipService() 