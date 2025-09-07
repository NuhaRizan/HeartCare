from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.user_model import create_admin, check_admin, get_all_users, delete_user
from models.heart_model import get_model_performance
from models.user_model import get_all_users
from models.heart_model import get_total_reports
from .main_controller import get_all_messages
import sqlite3
import os

admin_blueprint = Blueprint('admin', __name__)

@admin_blueprint.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '')
        password = data.get('password', '')
        
        # Simple hardcoded admin credentials
        if username == 'nuha' and password == '123':
            session['admin_id'] = 1
            session['is_admin'] = True
            if request.is_json:
                return {'success': True, 'message': 'Admin logged in successfully!'}
            flash('Admin logged in successfully!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            if request.is_json:
                return {'success': False, 'message': 'Invalid admin credentials.'}, 401
            flash('Invalid admin credentials.', 'danger')
    return render_template('admin_login.html')

@admin_blueprint.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        try:
            create_admin(username, password, name, email)
            flash('Admin account created! Please log in.', 'success')
            return redirect(url_for('admin.admin_login'))
        except Exception:
            flash('Admin username or email already exists.', 'danger')
    return render_template('admin_signup.html')

@admin_blueprint.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin.admin_login'))
    model_name = request.args.get('model_name', 'logistic')
    performance = get_model_performance(model_name)
    users = get_all_users()
    user_count = len(users)
    report_count = get_total_reports() if 'get_total_reports' in globals() else 0
    return render_template('admin_dashboard.html', performance=performance, user_count=user_count, report_count=report_count, model_name=model_name)

@admin_blueprint.route('/admin/users')
def admin_users():
    if not session.get('is_admin'):
        return redirect(url_for('admin.admin_login'))
    users = get_all_users()
    return render_template('admin_users.html', users=users)

@admin_blueprint.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('is_admin', None)
    flash('Logged out from admin panel.', 'info')
    return redirect(url_for('admin.admin_login'))

@admin_blueprint.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def admin_delete_user(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin.admin_login'))
    delete_user(user_id)
    flash('User deleted.', 'success')
    return redirect(url_for('admin.admin_users'))

@admin_blueprint.route('/admin/messages')
def admin_messages():
    if not session.get('is_admin'):
        return redirect(url_for('admin.admin_login'))
    messages = get_all_messages()
    return render_template('admin_messages.html', messages=messages, current_page='admin_messages')

# API endpoints for React frontend
@admin_blueprint.route('/api/admin/check-auth', methods=['GET'])
def api_check_admin_auth():
    if session.get('is_admin'):
        return {'authenticated': True}
    return {'authenticated': False}, 401

@admin_blueprint.route('/api/admin/stats', methods=['GET'])
def api_admin_stats():
    if not session.get('is_admin'):
        return {'error': 'Unauthorized'}, 401
    
    DB_PATH = os.path.join(os.path.dirname(__file__), '../users.db')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Basic counts
    cursor.execute('SELECT COUNT(*) as count FROM users')
    user_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) as count FROM records')
    record_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) as count FROM report_links')
    report_count = cursor.fetchone()[0]
    
    # Risk distribution
    cursor.execute('SELECT risk, COUNT(*) as count FROM records GROUP BY risk')
    risk_data = cursor.fetchall()
    
    # Age distribution
    cursor.execute('SELECT CASE WHEN age < 30 THEN "20-29" WHEN age < 40 THEN "30-39" WHEN age < 50 THEN "40-49" WHEN age < 60 THEN "50-59" ELSE "60+" END as age_group, COUNT(*) as count FROM records GROUP BY age_group')
    age_data = cursor.fetchall()
    
    # Gender distribution
    cursor.execute('SELECT sex, COUNT(*) as count FROM records GROUP BY sex')
    gender_data = cursor.fetchall()
    
    # Recent registrations (last 7 days)
    cursor.execute('SELECT DATE(created_at) as date, COUNT(*) as count FROM report_links WHERE created_at >= datetime("now", "-7 days") GROUP BY DATE(created_at) ORDER BY date')
    recent_reports = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        'total_users': user_count,
        'total_records': record_count,
        'total_reports': report_count,
        'risk_distribution': [{'risk': row[0], 'count': row[1]} for row in risk_data],
        'age_distribution': [{'age_group': row[0], 'count': row[1]} for row in age_data],
        'gender_distribution': [{'sex': 'Male' if row[0] == 1 else 'Female', 'count': row[1]} for row in gender_data],
        'recent_reports': [{'date': row[0], 'count': row[1]} for row in recent_reports]
    })

@admin_blueprint.route('/api/admin/users', methods=['GET'])
def api_admin_users():
    if not session.get('is_admin'):
        return {'error': 'Unauthorized'}, 401
    
    users = get_all_users()
    return jsonify([{
        'id': user['id'],
        'username': user['username'],
        'name': user['name'],
        'email': user['email'],
        'is_admin': user['is_admin']
    } for user in users])