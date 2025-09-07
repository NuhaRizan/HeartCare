import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from flask import render_template_string, render_template
from datetime import datetime
from config import (
    TWILIO_ACCOUNT_SID, 
    TWILIO_AUTH_TOKEN, 
    TWILIO_PHONE_NUMBER,
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SENDER_EMAIL,
    SENDER_NAME
)

class TwilioService:
    def __init__(self):
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        self.from_number = TWILIO_PHONE_NUMBER
    
    def send_sms(self, to_number, message):
        """
        Send SMS using Twilio
        """
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_email(self, to_email, subject, message_body, html_body=None):
        """
        Send email using SMTP with optional HTML content
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text version
            msg.attach(MIMEText(message_body, 'plain'))
            
            # Add HTML version if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            text = msg.as_string()
            server.sendmail(SENDER_EMAIL, to_email, text)
            server.quit()
            
            return {
                'success': True,
                'message': 'Email sent successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_heart_report_email(self, to_email, user_name, prediction_data):
        """
        Send formatted heart health report email using HTML template
        """
        try:
            # Read the HTML template
            with open('templates/email_report_template.html', 'r', encoding='utf-8') as f:
                html_template = f.read()
            
            # Prepare template variables
            template_vars = {
                'user_name': user_name,
                'prediction_result': prediction_data.get('prediction', 'N/A'),
                'risk_level': prediction_data.get('risk_level', 'Unknown'),
                'confidence_score': round(prediction_data.get('confidence', 0) * 100, 1),
                'reasoning': prediction_data.get('reasoning', ''),
                'recommendations': prediction_data.get('recommendations', ''),
                'features': prediction_data.get('features', []),
                'download_link': prediction_data.get('download_link', ''),
                'report_date': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                'report_id': prediction_data.get('report_id', ''),
                'unsubscribe_link': prediction_data.get('unsubscribe_link', '#'),
                'unsubscribe_preferences': prediction_data.get('unsubscribe_preferences', '#')
            }
            
            # Render the template
            html_body = render_template_string(html_template, **template_vars)
            
            # Create plain text version
            plain_text = f"""
HeartCare+ - Your Heart Health Report

Dear {user_name or 'Valued User'},

Heart Disease Risk: {prediction_data.get('prediction', 'N/A')}
Risk Level: {prediction_data.get('risk_level', 'Unknown')}
Confidence Score: {round(prediction_data.get('confidence', 0) * 100, 1)}%

{prediction_data.get('reasoning', 'Analysis completed based on your health parameters.')}

Recommendations:
{prediction_data.get('recommendations', 'Please consult with your healthcare provider for personalized advice.')}

Download Full Report: {prediction_data.get('download_link', 'Not available')}

Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Report ID: {prediction_data.get('report_id', '')}

IMPORTANT DISCLAIMER: This assessment is for informational purposes only and should not replace professional medical advice.

Best regards,
HeartCare+ Team
            """
            
            subject = f"HeartCare+ Report - Your Heart Health Assessment ({datetime.now().strftime('%m/%d/%Y')})"
            
            return self.send_email(to_email, subject, plain_text, html_body)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to send heart report email: {str(e)}'
            }

# Create a global instance
twilio_service = TwilioService() 