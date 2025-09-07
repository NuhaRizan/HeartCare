from flask import Blueprint, render_template, request, session, redirect, url_for, flash, send_file, jsonify
from models.heart_model import predict_heart_disease
from models.user_model import save_record, get_records, get_user_info, save_report_link, get_report_by_id, cleanup_expired_reports
from math import cos, sin, radians
import smtplib
from email.mime.text import MIMEText
import tempfile
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import os
import numpy as np
import sqlite3
from services.twilio_service import twilio_service
from services.infobip_service import infobip_service
import uuid
import json
import http.client
import socket
from config import LOCAL_SERVER_HOST, LOCAL_SERVER_PORT, LOCAL_SERVER_PROTOCOL

main_blueprint = Blueprint('main', __name__)

def get_network_ip():
    """Get the actual network IP address for download links"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        network_ip = s.getsockname()[0]
        s.close()
        return network_ip
    except Exception:
        return LOCAL_SERVER_HOST

def create_download_url(report_id):
    """Create download URL using network IP"""
    network_ip = get_network_ip()
    return f"{LOCAL_SERVER_PROTOCOL}://{network_ip}:{LOCAL_SERVER_PORT}/download_report/{report_id}"

@main_blueprint.route('/')
def landing():
    user_info = None
    if 'user_id' in session:
        user_info = get_user_info(session['user_id'])
    return render_template('landing.html', current_page='home', user_info=user_info)

def get_reasoning(features, prediction):
    # Simple example reasoning based on features
    age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal = features
    reasons = []
    if age > 50: reasons.append('Age above 50 is a risk factor.')
    if chol > 240: reasons.append('High cholesterol level.')
    if trestbps > 130: reasons.append('Elevated blood pressure.')
    if exang == 1: reasons.append('Exercise induced angina present.')
    if oldpeak > 2: reasons.append('Significant ST depression (oldpeak).')
    if not reasons:
        reasons.append('No major risk factors detected.')
    if prediction >= 0.5:
        summary = 'High risk due to: ' + ', '.join(reasons)
    else:
        summary = 'Low risk. ' + ' '.join(reasons)
    return summary

def get_recommendations(features, prediction):
    age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal = features
    recs = []
    if prediction >= 0.5:
        recs.append('Consult a cardiologist for further evaluation.')
        if chol > 240:
            recs.append('Consider dietary changes to lower cholesterol.')
        if trestbps > 130:
            recs.append('Monitor and manage your blood pressure.')
        if oldpeak > 2:
            recs.append('Discuss ST depression findings with your doctor.')
        recs.append('Maintain regular physical activity and a healthy diet.')
    else:
        recs.append('Continue a healthy lifestyle to maintain low risk.')
        if chol > 200:
            recs.append('Watch your cholesterol and consider regular checkups.')
        if trestbps > 120:
            recs.append('Monitor your blood pressure periodically.')
    return recs

def get_reasoning_and_recommendations(features, prediction):
    reasoning = get_reasoning(features, prediction)
    recommendations = get_recommendations(features, prediction)
    return reasoning, recommendations

@main_blueprint.route('/predict', methods=['GET', 'POST'])
def predict():
    prediction = None
    x = y = None
    reasoning = None
    recommendations = None
    features = None
    model_name = 'logistic'  # Default to logistic regression
    if request.method == 'POST':
        # Handle JSON requests from React frontend
        if request.is_json:
            data = request.get_json()
            print("DEBUG: Received JSON data:", data)
            model_name = data.get('model_name', 'logistic')
            features = [
                int(data.get('age')),
                int(data.get('sex')),
                int(data.get('cp')),
                int(data.get('trestbps')),
                int(data.get('chol')),
                int(data.get('fbs')),
                int(data.get('restecg')),
                int(data.get('thalach')),
                int(data.get('exang')),
                float(data.get('oldpeak')),
                int(data.get('slope')),
                int(data.get('ca')),
                int(data.get('thal'))
            ]
        else:
            # Handle form data from traditional web forms
            print("DEBUG: Received form data")
            model_name = request.form.get('model_name', 'logistic')
            features = [
                int(request.form.get('age')),
                int(request.form.get('sex')),
                int(request.form.get('cp')),
                int(request.form.get('trestbps')),
                int(request.form.get('chol')),
                int(request.form.get('fbs')),
                int(request.form.get('restecg')),
                int(request.form.get('thalach')),
                int(request.form.get('exang')),
                float(request.form.get('oldpeak')),
                int(request.form.get('slope')),
                int(request.form.get('ca')),
                int(request.form.get('thal'))
            ]
        
        print(f"DEBUG: User selected model: {model_name}")
        print("DEBUG: Features:", features)
        
        prediction = predict_heart_disease(features, model_name)
        if prediction is not None:
            angle = 160 * (prediction if prediction <= 1 else 1)
            x = 130 + 100 * np.cos(np.radians(200 - angle))
            y = 120 - 100 * np.sin(np.radians(200 - angle))
            reasoning, recommendations = get_reasoning_and_recommendations(features, prediction)
            
            # Determine risk level
            if prediction >= 0.7:
                risk_level = "High"
            elif prediction >= 0.4:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            # Return JSON response for React frontend
            if request.is_json:
                return jsonify({
                    'prediction': 'High Risk' if prediction >= 0.5 else 'Low Risk',
                    'confidence': prediction * 100,
                    'risk_level': risk_level,
                    'reasoning': reasoning,
                    'recommendations': '. '.join(recommendations) if isinstance(recommendations, list) else recommendations
                })
        
        if 'user_id' in session:
            save_record(session['user_id'], features, prediction)
        
        # Return HTML template for traditional web forms
        return render_template('predict.html', prediction=prediction, x=x, y=y, reasoning=reasoning, recommendations=recommendations, features=features, model_name=model_name, current_page='predict')
    
    return render_template('predict.html', prediction=prediction, x=x, y=y, reasoning=reasoning, recommendations=recommendations, features=features, model_name=model_name, current_page='predict')

@main_blueprint.route('/download_report', methods=['POST'])
def download_report():
    import ast
    features = request.form.get('features')
    prediction = request.form.get('prediction')
    reasoning = request.form.get('reasoning')
    recommendations = request.form.get('recommendations')
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    # Custom styles
    title_style = ParagraphStyle('title', parent=styles['Title'], alignment=TA_CENTER, textColor=colors.HexColor('#c0392b'), fontSize=22, spaceAfter=12)
    section_header = ParagraphStyle('section', parent=styles['Heading2'], textColor=colors.HexColor('#c0392b'), spaceBefore=12, spaceAfter=6)
    normal_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold')
    # Header with logo and title
    logo_path = os.path.join(os.path.dirname(__file__), '../../web/static/images/doctor.png')
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=1.1*inch, height=1.1*inch))
    elements.append(Paragraph('Heart Care+ - Heart Disease Prediction Report', title_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#c0392b')))
    elements.append(Spacer(1, 10))
    # Prediction section
    pred_text = f'<b>Prediction:</b> <font color="#c0392b">{"High Risk" if float(prediction) >= 0.5 else "Low Risk"}</font>'
    elements.append(Paragraph(pred_text, section_header))
    elements.append(Spacer(1, 6))
    # Reasoning
    elements.append(Paragraph('<b>Reasoning:</b>', normal_bold))
    elements.append(Paragraph(reasoning, styles['Normal']))
    elements.append(Spacer(1, 8))
    # Recommendations
    if recommendations:
        try:
            recs = ast.literal_eval(recommendations)
            elements.append(Paragraph('<b>Recommendations:</b>', normal_bold))
            for rec in recs:
                elements.append(Paragraph(f'- {rec}', styles['Normal']))
            elements.append(Spacer(1, 8))
        except Exception:
            elements.append(Paragraph(f'<b>Recommendations:</b> {recommendations}', styles['Normal']))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#c0392b')))
    elements.append(Spacer(1, 10))
    # Features table
    try:
        features_list = ast.literal_eval(features)
        feature_names = ['Age', 'Sex', 'CP', 'BP', 'Chol', 'FBS', 'ECG', 'Thalach', 'Exang', 'Oldpeak', 'Slope', 'CA', 'Thal']
        table_data = [['Feature', 'Value']]
        for name, value in zip(feature_names, features_list):
            table_data.append([name, value])
        t = Table(table_data, hAlign='LEFT', colWidths=[2*inch, 2.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#c0392b')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(Paragraph('Input Features', section_header))
        elements.append(t)
    except Exception:
        elements.append(Paragraph(f'<b>Features:</b> {features}', styles['Normal']))
    # Footer
    elements.append(Spacer(1, 24))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#c0392b')))
    elements.append(Paragraph('<font size=10 color="#888">Generated by Heart Care+ | For informational purposes only</font>', styles['Normal']))
    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='heart_care_report.pdf', mimetype='application/pdf')

@main_blueprint.route('/send_report_email', methods=['POST'])
def send_report_email():
    email = request.form.get('email')
    prediction = request.form.get('prediction')
    reasoning = request.form.get('reasoning')
    
    subject = 'Your Heart Disease Prediction Report'
    message_body = f"""
Your Heart Disease Prediction: {'High Risk' if float(prediction) >= 0.5 else 'Low Risk'}

Reasoning: {reasoning}

This report is for informational purposes only. Please consult with a healthcare professional for medical advice.

Best regards,
Heart Care+ Team
    """
    
    result = twilio_service.send_email(email, subject, message_body)
    
    if result['success']:
        flash('Report sent to your email successfully!', 'success')
    else:
        flash(f'Failed to send email: {result["error"]}', 'danger')
    
    return redirect(url_for('main.predict'))

@main_blueprint.route('/send_report_sms', methods=['POST'])
def send_report_sms():
    if 'user_id' not in session:
        flash('Please log in to send SMS messages.', 'warning')
        return redirect(url_for('main.predict'))
    
    phone = request.form.get('phone')
    prediction = request.form.get('prediction')
    reasoning = request.form.get('reasoning')
    recommendations = request.form.get('recommendations')
    features = request.form.get('features')
    
    if not phone:
        flash('Please provide a phone number for SMS.', 'warning')
        return redirect(url_for('main.predict'))
    
    # Generate report immediately
    report_id = str(uuid.uuid4())
    
    # Save report to database
    save_report_link(
        session['user_id'], 
        report_id, 
        prediction, 
        reasoning, 
        recommendations, 
        features
    )
    
    print(f"DEBUG SMS: Saved report with ID: {report_id}")
    print(f"DEBUG SMS: Prediction: {prediction}")
    print(f"DEBUG SMS: Reasoning: {reasoning}")
    print(f"DEBUG SMS: Features: {features}")
    print(f"DEBUG SMS: Recommendations: {recommendations}")
    
    # Create download link using local server
    download_url = create_download_url(report_id)
    
    # Create SMS message with download link
    message = f"Heart Care+: Your report is ready! Download: {download_url} (expires in 24h)"
    
    result = infobip_service.send_sms(phone, message)
    
    if result['success']:
        flash('SMS sent successfully with download link via Infobip!', 'success')
    else:
        flash(f'Failed to send SMS: {result["error"]}', 'danger')
    
    return redirect(url_for('main.predict'))

@main_blueprint.route('/records')
def records():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    records = get_records(session['user_id'])
    return render_template('records.html', records=records, current_page='records')

@main_blueprint.route('/about')
def about():
    return render_template('about.html', current_page='about')

@main_blueprint.route('/how-to-use')
def how_to_use():
    return render_template('how_to_use.html', current_page='how-to-use')

def get_all_messages():
    DB_PATH = os.path.join(os.path.dirname(__file__), '../users.db')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, email, message, created_at FROM messages ORDER BY created_at DESC')
    messages = c.fetchall()
    conn.close()
    return messages

@main_blueprint.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    DB_PATH = os.path.join(os.path.dirname(__file__), '../users.db')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('INSERT INTO messages (name, email, message) VALUES (?, ?, ?)', (name, email, message))
    conn.commit()
    conn.close()
    flash('Your message has been sent! Thank you for contacting us.', 'success')
    return redirect(url_for('main.about'))

@main_blueprint.route('/send_report_link', methods=['POST'])
def send_report_link():
    if 'user_id' not in session:
        flash('Please log in to send report links.', 'warning')
        return redirect(url_for('main.predict'))
    
    prediction = request.form.get('prediction')
    reasoning = request.form.get('reasoning')
    recommendations = request.form.get('recommendations')
    features = request.form.get('features')
    email = request.form.get('email')
    phone = request.form.get('phone')
    whatsapp = request.form.get('whatsapp')
    
    # Generate unique report ID
    report_id = str(uuid.uuid4())
    
    # Save report to database
    save_report_link(
        session['user_id'], 
        report_id, 
        prediction, 
        reasoning, 
        recommendations, 
        features
    )
    
    print(f"DEBUG WHATSAPP: Saved report with ID: {report_id}")
    print(f"DEBUG WHATSAPP: Prediction: {prediction}")
    print(f"DEBUG WHATSAPP: Reasoning: {reasoning}")
    print(f"DEBUG WHATSAPP: Features: {features}")
    print(f"DEBUG WHATSAPP: Recommendations: {recommendations}")
    
    # Create download link using local server
    download_url = create_download_url(report_id)
    
    success_count = 0
    
    # Send email if provided
    if email:
        subject = 'Your Heart Disease Prediction Report - Download Link'
        message_body = f"""
Your Heart Disease Prediction Report is ready for download!

Download Link: {download_url}

This link will expire in 24 hours.

Your Prediction: {'High Risk' if float(prediction) >= 0.5 else 'Low Risk'}

This report is for informational purposes only. Please consult with a healthcare professional for medical advice.

Best regards,
Heart Care+ Team
        """
        
        result = twilio_service.send_email(email, subject, message_body)
        if result['success']:
            success_count += 1
            flash('Download link sent to your email!', 'success')
        else:
            flash(f'Failed to send email: {result["error"]}', 'danger')
    
    # Send SMS if provided
    if phone:
        message = f"Heart Care+: Your report is ready! Download: {download_url} (expires in 24h)"
        
        result = infobip_service.send_sms(phone, message)
        if result['success']:
            success_count += 1
            flash('Download link sent to your phone via Infobip SMS!', 'success')
        else:
            flash(f'Failed to send SMS: {result["error"]}', 'danger')
    
    # Send WhatsApp if provided
    if whatsapp:
        # Use the simple WhatsApp report method
        risk_level = 'High Risk' if float(prediction) >= 0.5 else 'Low Risk'
        
        # Try template method first
        result = infobip_service.send_whatsapp_report(
            whatsapp, 
            prediction, 
            reasoning, 
            download_url, 
            risk_level
        )
        
        # If template fails, try text method as fallback
        if not result['success'] and '404' in result.get('error', ''):
            print(f"Template method failed, trying text method: {result['error']}")
            result = infobip_service.send_whatsapp_formatted_text(
                whatsapp, 
                prediction, 
                reasoning, 
                download_url, 
                risk_level
            )
        
        if result['success']:
            success_count += 1
            message_type = result.get('type', 'message')
            flash(f'WhatsApp message sent with download link! ({message_type})', 'success')
        else:
            flash(f'Failed to send WhatsApp: {result["error"]}', 'danger')
    
    if success_count == 0:
        flash('Please provide either email, phone, or WhatsApp number.', 'warning')
    
    return redirect(url_for('main.predict'))

@main_blueprint.route('/send_whatsapp', methods=['POST'])
def send_whatsapp():
    if 'user_id' not in session:
        flash('Please log in to send WhatsApp messages.', 'warning')
        return redirect(url_for('main.predict'))
    
    phone = request.form.get('phone')
    prediction = request.form.get('prediction')
    reasoning = request.form.get('reasoning')
    recommendations = request.form.get('recommendations')
    features = request.form.get('features')
    
    if not phone:
        flash('Please provide a phone number for WhatsApp.', 'warning')
        return redirect(url_for('main.predict'))
    
    # Generate report immediately
    report_id = str(uuid.uuid4())
    
    # Save report to database
    save_report_link(
        session['user_id'], 
        report_id, 
        prediction, 
        reasoning, 
        recommendations, 
        features
    )
    
    print(f"DEBUG WHATSAPP: Saved report with ID: {report_id}")
    print(f"DEBUG WHATSAPP: Prediction: {prediction}")
    print(f"DEBUG WHATSAPP: Reasoning: {reasoning}")
    print(f"DEBUG WHATSAPP: Features: {features}")
    print(f"DEBUG WHATSAPP: Recommendations: {recommendations}")
    
    # Create download link using local server
    download_url = create_download_url(report_id)
    
    # Create simple message with download link
    simple_message = f"Here is your report download here: {download_url}"
    
    # Try template method first
    result = infobip_service.send_whatsapp(phone, simple_message)
    
    # If template fails, try text method as fallback
    if not result['success'] and '404' in result.get('error', ''):
        print(f"Template method failed, trying text method: {result['error']}")
        result = infobip_service.send_whatsapp_formatted_text(
            phone, 
            prediction, 
            reasoning, 
            download_url, 
            'High Risk' if float(prediction) >= 0.5 else 'Low Risk'
        )
    
    if result['success']:
        flash('WhatsApp message sent with download link! Report generated successfully.', 'success')
    else:
        flash(f'Failed to send WhatsApp: {result["error"]}', 'danger')
    
    return redirect(url_for('main.predict'))

@main_blueprint.route('/send_report_email_link', methods=['POST'])
def send_report_email_link():
    if 'user_id' not in session:
        flash('Please log in to send email reports.', 'warning')
        return redirect(url_for('main.predict'))
    
    email = request.form.get('email')
    prediction = request.form.get('prediction')
    reasoning = request.form.get('reasoning')
    recommendations = request.form.get('recommendations')
    features = request.form.get('features')
    
    print(f"DEBUG EMAIL: Email address: {email}")
    print(f"DEBUG EMAIL: Prediction: {prediction}")
    print(f"DEBUG EMAIL: Reasoning: {reasoning}")
    print(f"DEBUG EMAIL: Features: {features}")
    
    if not email:
        flash('Please provide an email address.', 'warning')
        return redirect(url_for('main.predict'))
    
    # Generate report immediately (same as WhatsApp method)
    report_id = str(uuid.uuid4())
    print(f"DEBUG EMAIL: Generated report ID: {report_id}")
    
    # Save report to database (same as WhatsApp method)
    save_report_link(
        session['user_id'], 
        report_id, 
        prediction, 
        reasoning, 
        recommendations, 
        features
    )
    print(f"DEBUG EMAIL: Report saved to database")
    
    # Create download link using local server (same as WhatsApp method)
    download_url = create_download_url(report_id)
    print(f"DEBUG EMAIL: Download URL: {download_url}")
    
    # Create email content (similar to SMS format but for email)
    risk_level = 'High Risk' if float(prediction) >= 0.5 else 'Low Risk'
    subject = f'Heart Care+ Report - {risk_level}'
    
    # Use the same simple message format as WhatsApp
    message_body = f"""
Heart Care+: Your report is ready! 

Risk Level: {risk_level}
Prediction Score: {float(prediction):.2f}

Download your detailed report here: {download_url}

This link will expire in 24 hours.

Reasoning: {reasoning}

This report is for informational purposes only. Please consult with a healthcare professional for medical advice.

Best regards,
Heart Care+ Team
    """.strip()
    
    print(f"DEBUG EMAIL: Subject: {subject}")
    print(f"DEBUG EMAIL: Message body length: {len(message_body)}")
    print(f"DEBUG EMAIL: Download link in message: {'YES' if download_url in message_body else 'NO'}")
    print(f"DEBUG EMAIL: Message preview: {message_body[:200]}...")
    
    # Send email
    result = twilio_service.send_email(email, subject, message_body)
    print(f"DEBUG EMAIL: Send result: {result}")
    
    if result['success']:
        flash('Email sent with report download link! Report generated successfully.', 'success')
    else:
        flash(f'Failed to send email: {result["error"]}', 'danger')
    
    return redirect(url_for('main.predict'))

@main_blueprint.route('/download_report/<report_id>')
def download_report_by_id(report_id):
    # Clean up expired reports
    cleanup_expired_reports()
    
    # Get report from database
    report = get_report_by_id(report_id)
    
    print(f"DEBUG DOWNLOAD: Report ID: {report_id}")
    print(f"DEBUG DOWNLOAD: Report found: {report is not None}")
    if report:
        print(f"DEBUG DOWNLOAD: Prediction: {report['prediction']}")
        print(f"DEBUG DOWNLOAD: Reasoning: {report['reasoning']}")
        print(f"DEBUG DOWNLOAD: Features: {report['features']}")
        print(f"DEBUG DOWNLOAD: Recommendations: {report['recommendations']}")
    
    if not report:
        flash('Report not found or has expired.', 'danger')
        return redirect(url_for('main.landing'))
    
    # Parse stored data
    import ast
    try:
        features = ast.literal_eval(report['features']) if report['features'] else []
        recommendations = ast.literal_eval(report['recommendations']) if report['recommendations'] else []
        print(f"DEBUG DOWNLOAD: Parsed features: {features}")
        print(f"DEBUG DOWNLOAD: Parsed recommendations: {recommendations}")
    except Exception as e:
        print(f"DEBUG DOWNLOAD: Error parsing data: {e}")
        features = []
        recommendations = []
    
    # Generate PDF report
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle('title', parent=styles['Title'], alignment=TA_CENTER, textColor=colors.HexColor('#c0392b'), fontSize=22, spaceAfter=12)
    section_header = ParagraphStyle('section', parent=styles['Heading2'], textColor=colors.HexColor('#c0392b'), spaceBefore=12, spaceAfter=6)
    normal_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold')
    
    # Header
    logo_path = os.path.join(os.path.dirname(__file__), '../static/images/doctor.png')
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=1.1*inch, height=1.1*inch))
    elements.append(Paragraph('Heart Care+ - Heart Disease Prediction Report', title_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#c0392b')))
    elements.append(Spacer(1, 10))
    
    # Prediction section
    pred_text = f'<b>Prediction:</b> <font color="#c0392b">{"High Risk" if float(report["prediction"]) >= 0.5 else "Low Risk"}</font>'
    elements.append(Paragraph(pred_text, section_header))
    elements.append(Spacer(1, 6))
    
    # Reasoning
    elements.append(Paragraph('<b>Reasoning:</b>', normal_bold))
    elements.append(Paragraph(report['reasoning'], styles['Normal']))
    elements.append(Spacer(1, 8))
    
    # Recommendations
    if recommendations:
        elements.append(Paragraph('<b>Recommendations:</b>', normal_bold))
        for rec in recommendations:
            elements.append(Paragraph(f'- {rec}', styles['Normal']))
        elements.append(Spacer(1, 8))
    
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#c0392b')))
    elements.append(Spacer(1, 10))
    
    # Features table
    if features:
        feature_names = ['Age', 'Sex', 'CP', 'BP', 'Chol', 'FBS', 'ECG', 'Thalach', 'Exang', 'Oldpeak', 'Slope', 'CA', 'Thal']
        table_data = [['Feature', 'Value']]
        for name, value in zip(feature_names, features):
            table_data.append([name, value])
        t = Table(table_data, hAlign='LEFT', colWidths=[2*inch, 2.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#c0392b')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(Paragraph('Input Features', section_header))
        elements.append(t)
    
    # Footer
    elements.append(Spacer(1, 24))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#c0392b')))
    elements.append(Paragraph('<font size=10 color="#888">Generated by Heart Care+ | For informational purposes only</font>', styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f'heart_care_report_{report_id[:8]}.pdf', mimetype='application/pdf')

@main_blueprint.route('/test_email_download', methods=['POST'])
def test_email_download():
    """Test route that uses exact same logic as test script"""
    if 'user_id' not in session:
        flash('Please log in to test email.', 'warning')
        return redirect(url_for('main.predict'))
    
    email = request.form.get('email')
    prediction = request.form.get('prediction')
    reasoning = request.form.get('reasoning')
    
    print(f"TEST EMAIL: Email address: {email}")
    print(f"TEST EMAIL: Prediction: {prediction}")
    print(f"TEST EMAIL: Reasoning: {reasoning}")
    
    if not email:
        flash('Please provide an email address.', 'warning')
        return redirect(url_for('main.predict'))
    
    # Generate test report ID (exact same as test script)
    report_id = str(uuid.uuid4())
    print(f"TEST EMAIL: Generated report ID: {report_id}")
    
    # Create download link (exact same as test script)
    download_url = create_download_url(report_id)
    print(f"TEST EMAIL: Download URL: {download_url}")
    
    # Create email content (exact same as test script)
    subject = "Heart Care+ Report - Test"
    message_body = f"""
Dear User,

Your Heart Disease Risk Assessment Report is ready!

Risk Level: Test Risk
Prediction Score: {prediction}

Reasoning: {reasoning}

Download your detailed report here: {download_url}

This link will expire in 24 hours.

Important Notes:
- This report is for informational purposes only
- Please consult with a healthcare professional for medical advice
- Keep your health information secure

Best regards,
Heart Care+ Team
    """.strip()
    
    print(f"TEST EMAIL: Subject: {subject}")
    print(f"TEST EMAIL: Message body length: {len(message_body)}")
    print(f"TEST EMAIL: Download link in message: {'YES' if download_url in message_body else 'NO'}")
    print(f"TEST EMAIL: Message preview: {message_body[:200]}...")
    
    # Send email (exact same as test script)
    result = twilio_service.send_email(email, subject, message_body)
    print(f"TEST EMAIL: Send result: {result}")
    
    if result['success']:
        flash('Test email sent with download link! Check your email.', 'success')
    else:
        flash(f'Failed to send test email: {result["error"]}', 'danger')
    
    return redirect(url_for('main.predict')) 