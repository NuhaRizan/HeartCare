from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.user_model import create_user, check_user, init_db, get_user_info

auth_blueprint = Blueprint('auth', __name__)

# Changed decorator: before_app_first_request is invalid for Blueprints
@auth_blueprint.before_app_request
def setup():
    init_db()

@auth_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle JSON requests from React frontend
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            name = data.get('name')
            email = data.get('email')
        else:
            # Handle form data from traditional web forms
            username = request.form['username']
            password = request.form['password']
            name = request.form['name']
            email = request.form['email']

        # Basic backend validation
        if not (4 <= len(username) <= 20 and username.replace('_', '').isalnum()):
            error_msg = 'Invalid username. Use 4-20 letters, numbers, or underscores.'
            if request.is_json:
                return jsonify({'success': False, 'message': error_msg}), 400
            flash(error_msg, 'danger')
            return render_template('signup.html')
        if len(password) < 6:
            error_msg = 'Password must be at least 6 characters.'
            if request.is_json:
                return jsonify({'success': False, 'message': error_msg}), 400
            flash(error_msg, 'danger')
            return render_template('signup.html')
        if not (2 <= len(name) <= 50 and all(c.isalpha() or c.isspace() for c in name)):
            error_msg = 'Name should be 2-50 letters.'
            if request.is_json:
                return jsonify({'success': False, 'message': error_msg}), 400
            flash(error_msg, 'danger')
            return render_template('signup.html')
        if '@' not in email or '.' not in email:
            error_msg = 'Enter a valid email address.'
            if request.is_json:
                return jsonify({'success': False, 'message': error_msg}), 400
            flash(error_msg, 'danger')
            return render_template('signup.html')
        
        try:
            create_user(username, password, name, email)
            success_msg = 'Account created successfully!'
            if request.is_json:
                return jsonify({'success': True, 'message': success_msg}), 201
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception:
            error_msg = 'Username or email already exists.'
            if request.is_json:
                return jsonify({'success': False, 'message': error_msg}), 409
            flash(error_msg, 'danger')
    return render_template('signup.html')

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle JSON requests from React frontend
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            # Handle form data from traditional web forms
            username = request.form['username']
            password = request.form['password']
        
        user_id = check_user(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            # Fetch and store name/email for navbar dropdown
            user_info = get_user_info(user_id)
            if user_info:
                session['name'] = user_info['name']
                session['email'] = user_info['email']
            
            if request.is_json:
                return jsonify({
                    'success': True, 
                    'message': 'Logged in successfully!',
                    'user': {
                        'id': user_id,
                        'username': username,
                        'name': user_info['name'] if user_info else '',
                        'email': user_info['email'] if user_info else ''
                    }
                }), 200
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.landing'))
        else:
            error_msg = 'Invalid credentials.'
            if request.is_json:
                return jsonify({'success': False, 'message': error_msg}), 401
            flash(error_msg, 'danger')
    return render_template('login.html')

@auth_blueprint.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))
