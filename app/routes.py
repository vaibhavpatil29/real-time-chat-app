from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Message
from app import db, oauth
from app.email_service import send_verification_email, send_password_reset_email, send_welcome_email
import re
from datetime import datetime, timedelta
from functools import wraps
import secrets

main = Blueprint('main', __name__)

# Configure Google OAuth
def configure_google_oauth():
    """Configure Google OAuth client"""
    if not hasattr(configure_google_oauth, 'configured'):
        oauth.register(
            name='google',
            client_id=current_app.config['GOOGLE_CLIENT_ID'],
            client_secret=current_app.config['GOOGLE_CLIENT_SECRET'],
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            authorize_params=None,
            access_token_url='https://accounts.google.com/o/oauth2/token',
            access_token_params=None,
            refresh_token_url=None,
            redirect_uri=None,
            client_kwargs={
                'scope': 'openid email profile',
                'response_type': 'code'
            }
        )
        configure_google_oauth.configured = True

# Password validation function
def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"

# Email validation function
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Rate limiting decorator
def rate_limit(max_requests=5, window=300):  # 5 requests per 5 minutes
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            key = f"{request.remote_addr}:{f.__name__}"
            current_time = datetime.utcnow()
            
            # Clean old entries
            session_key = f"rate_limit_{key}"
            if session_key not in session:
                session[session_key] = []
            
            # Remove old requests outside the window
            session[session_key] = [
                timestamp for timestamp in session[session_key]
                if current_time - datetime.fromisoformat(timestamp) < timedelta(seconds=window)
            ]
            
            if len(session[session_key]) >= max_requests:
                flash('Too many requests. Please try again later.', 'error')
                # Return to home page instead of redirecting to same URL to avoid loop
                return redirect(url_for('main.index'))
            
            session[session_key].append(current_time.isoformat())
            session.permanent = True
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.chat', room='general'))
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.chat', room='general'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores')
        
        if not email or not validate_email(email):
            errors.append('Please enter a valid email address')
        
        if not password:
            errors.append('Password is required')
        else:
            is_valid, message = validate_password(password)
            if not is_valid:
                errors.append(message)
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                errors.append('Username already exists')
            if existing_user.email == email:
                errors.append('Email already registered')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html', 
                                 username=username, 
                                 email=email,
                                 first_name=first_name,
                                 last_name=last_name)
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        new_user.set_password(password)
        
        # In development mode, automatically verify email
        # Check if we're in development (debug mode or no FLASK_ENV set)
        is_development = (current_app.debug or 
                         current_app.config.get('FLASK_ENV') == 'development' or 
                         not current_app.config.get('FLASK_ENV'))
        
        if is_development:
            new_user.email_verified = True
            verification_token = None
        else:
            # Generate email verification token for production
            verification_token = new_user.generate_email_verification_token()
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Handle email verification based on environment
            if is_development:
                flash('Registration successful! You can now log in immediately.', 'success')
                flash('Email verification is disabled in development mode.', 'info')
            else:
                # Send verification email in production
                if verification_token and send_verification_email(new_user, verification_token):
                    flash('Registration successful! Please check your email to verify your account.', 'success')
                else:
                    flash('Registration successful! However, we could not send the verification email. Please contact support.', 'warning')
                    if verification_token:
                        flash(f'Verification link (for testing): /verify-email/{verification_token}', 'info')
            
            return redirect(url_for('main.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.chat', room='general'))
        
    if request.method == 'POST':
        # Apply rate limiting only to POST requests
        key = f"{request.remote_addr}:login_post"
        current_time = datetime.utcnow()
        
        # Clean old entries
        session_key = f"rate_limit_{key}"
        if session_key not in session:
            session[session_key] = []
        
        # Remove old requests outside the window (5 minutes)
        session[session_key] = [
            timestamp for timestamp in session[session_key]
            if current_time - datetime.fromisoformat(timestamp) < timedelta(seconds=300)
        ]
        
        if len(session[session_key]) >= 5:  # 5 login attempts per 5 minutes
            flash('Too many login attempts. Please try again later.', 'error')
            return render_template('login.html')
        
        session[session_key].append(current_time.isoformat())
        session.permanent = True
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        if not username_or_email or not password:
            flash('Please enter both username/email and password.', 'error')
            return render_template('login.html')
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user:
            flash('Invalid credentials.', 'error')
            return render_template('login.html')
        
        # Check if account is locked
        if user.is_account_locked():
            flash('Account is temporarily locked due to too many failed login attempts. Please try again later.', 'error')
            return render_template('login.html')
        
        # Check if account is active
        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'error')
            return render_template('login.html')
        
        # Verify password
        if user.check_password(password):
            # Check if email is verified (skip in development mode)
            is_development = (current_app.debug or 
                             current_app.config.get('FLASK_ENV') == 'development' or 
                             not current_app.config.get('FLASK_ENV'))
            
            if not user.email_verified and not is_development:
                flash('Please verify your email address before logging in.', 'warning')
                return render_template('login.html')
            
            # Successful login
            user.successful_login()
            db.session.commit()
            
            login_user(user, remember=remember_me)
            
            # Redirect to next page or chat
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.chat', room='general'))
        else:
            # Failed login
            user.increment_failed_login()
            db.session.commit()
            
            remaining_attempts = max(0, 5 - user.failed_login_attempts)
            if remaining_attempts > 0:
                flash(f'Invalid credentials. {remaining_attempts} attempts remaining.', 'error')
            else:
                flash('Account locked due to too many failed attempts.', 'error')
    
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/chat/<room>')
@login_required
def chat(room):
    # Update last seen
    current_user.update_last_seen()
    db.session.commit()
    
    messages = Message.query.filter_by(room=room).order_by(Message.timestamp).all()
    return render_template('chat.html', username=current_user.username, messages=messages, room=room)

# Email Verification Routes
@main.route('/verify-email/<token>')
def verify_email(token):
    user = User.query.filter_by(email_verification_token=token).first()
    
    if not user:
        flash('Invalid or expired verification token.', 'error')
        return redirect(url_for('main.login'))
    
    if user.verify_email_token(token):
        db.session.commit()
        
        # Send welcome email
        send_welcome_email(user)
        
        flash('Email verified successfully! You can now log in.', 'success')
    else:
        flash('Email verification failed.', 'error')
    
    return redirect(url_for('main.login'))

@main.route('/resend-verification', methods=['GET', 'POST'])
@rate_limit(max_requests=3, window=600)  # 3 requests per 10 minutes
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email or not validate_email(email):
            flash('Please enter a valid email address.', 'error')
            return render_template('resend_verification.html')
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Don't reveal if email exists or not
            flash('If this email is registered, you will receive a verification link.', 'info')
            return render_template('resend_verification.html')
        
        if user.email_verified:
            flash('This email is already verified.', 'info')
            return redirect(url_for('main.login'))
        
        # Generate new verification token
        verification_token = user.generate_email_verification_token()
        db.session.commit()
        
        # Send verification email
        if send_verification_email(user, verification_token):
            flash('Verification email sent! Please check your inbox.', 'success')
        else:
            flash('Failed to send verification email. Please try again later.', 'error')
            flash(f'Verification link (for testing): /verify-email/{verification_token}', 'info')
        
        return redirect(url_for('main.login'))
    
    return render_template('resend_verification.html')

# Password Reset Routes
@main.route('/forgot-password', methods=['GET', 'POST'])
@rate_limit(max_requests=3, window=600)  # 3 requests per 10 minutes
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.chat', room='general'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email or not validate_email(email):
            flash('Please enter a valid email address.', 'error')
            return render_template('forgot_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        # Always show success message to prevent email enumeration
        flash('If this email is registered, you will receive a password reset link.', 'info')
        
        if user and user.is_active:
            # Generate password reset token
            reset_token = user.generate_password_reset_token()
            db.session.commit()
            
            # Send password reset email
            if send_password_reset_email(user, reset_token):
                pass  # Success message already shown above
            else:
                flash(f'Reset link (for testing): /reset-password/{reset_token}', 'info')
        
        return redirect(url_for('main.login'))
    
    return render_template('forgot_password.html')

@main.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.chat', room='general'))
    
    user = User.query.filter_by(password_reset_token=token).first()
    
    if not user or not user.verify_password_reset_token(token):
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('main.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not password:
            errors.append('Password is required')
        else:
            is_valid, message = validate_password(password)
            if not is_valid:
                errors.append(message)
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('reset_password.html', token=token)
        
        # Reset password
        user.reset_password(password)
        db.session.commit()
        
        flash('Password reset successful! You can now log in with your new password.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('reset_password.html', token=token)

# Profile Management Routes
@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        bio = request.form.get('bio', '').strip()
        
        # Update profile
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.bio = bio
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('edit_profile.html', user=current_user)

@main.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not current_password:
            errors.append('Current password is required')
        elif not current_user.check_password(current_password):
            errors.append('Current password is incorrect')
        
        if not new_password:
            errors.append('New password is required')
        else:
            is_valid, message = validate_password(new_password)
            if not is_valid:
                errors.append(message)
        
        if new_password != confirm_password:
            errors.append('New passwords do not match')
        
        if current_password == new_password:
            errors.append('New password must be different from current password')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('change_password.html')
        
        # Change password
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('change_password.html')

# API Routes for AJAX requests
@main.route('/api/check-username')
def check_username():
    username = request.args.get('username', '').strip()
    
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'})
    
    if len(username) < 3:
        return jsonify({'available': False, 'message': 'Username must be at least 3 characters long'})
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return jsonify({'available': False, 'message': 'Username can only contain letters, numbers, and underscores'})
    
    user = User.query.filter_by(username=username).first()
    
    if user:
        return jsonify({'available': False, 'message': 'Username is already taken'})
    
    return jsonify({'available': True, 'message': 'Username is available'})

@main.route('/api/check-email')
def check_email():
    email = request.args.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'available': False, 'message': 'Email is required'})
    
    if not validate_email(email):
        return jsonify({'available': False, 'message': 'Please enter a valid email address'})
    
    user = User.query.filter_by(email=email).first()
    
    if user:
        return jsonify({'available': False, 'message': 'Email is already registered'})
    
    return jsonify({'available': True, 'message': 'Email is available'})

# Google OAuth Routes
@main.route('/auth/google')
def google_login():
    """Initiate Google OAuth login"""
    configure_google_oauth()
    
    # Store the next URL in session if provided
    next_url = request.args.get('next')
    if next_url:
        session['next_url'] = next_url
    
    redirect_uri = url_for('main.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@main.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    configure_google_oauth()
    
    try:
        # Get the authorization token
        token = oauth.google.authorize_access_token()
        
        # Get user info from Google using the access token
        resp = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo', token=token)
        user_info = resp.json()
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')
        avatar_url = user_info.get('picture', '')
        
        if not google_id or not email:
            flash('Failed to get user information from Google.', 'error')
            return redirect(url_for('main.login'))
        
        # Check if user already exists with this Google ID
        user = User.query.filter_by(google_id=google_id).first()
        
        if user:
            # User exists, log them in
            login_user(user, remember=True)
            flash(f'Welcome back, {user.first_name or user.username}!', 'success')
        else:
            # Check if user exists with this email (link accounts)
            existing_user = User.query.filter_by(email=email).first()
            
            if existing_user:
                # Link Google account to existing user
                existing_user.google_id = google_id
                existing_user.oauth_provider = 'google'
                existing_user.avatar_url = avatar_url
                existing_user.email_verified = True  # Google emails are verified
                
                db.session.commit()
                login_user(existing_user, remember=True)
                flash(f'Google account linked successfully! Welcome back, {existing_user.first_name or existing_user.username}!', 'success')
                user = existing_user
            else:
                # Create new user
                # Generate unique username from email
                base_username = email.split('@')[0]
                username = base_username
                counter = 1
                
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                new_user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    avatar_url=avatar_url,
                    google_id=google_id,
                    oauth_provider='google',
                    email_verified=True,  # Google emails are verified
                    is_active=True
                )
                
                db.session.add(new_user)
                db.session.commit()
                
                login_user(new_user, remember=True)
                flash(f'Account created successfully! Welcome to ChatApp, {first_name or username}!', 'success')
                
                # Send welcome email
                try:
                    send_welcome_email(new_user.email, new_user.first_name or new_user.username)
                except Exception as e:
                    current_app.logger.error(f'Failed to send welcome email: {str(e)}')
                
                user = new_user
        
        # Update last login
        user.update_last_login()
        db.session.commit()
        
        # Redirect to next URL or chat
        next_url = session.pop('next_url', None)
        if next_url:
            return redirect(next_url)
        
        return redirect(url_for('main.chat', room='general'))
        
    except Exception as e:
        current_app.logger.error(f'Google OAuth error: {str(e)}')
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('main.login'))
