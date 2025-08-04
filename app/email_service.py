"""
Email service module for sending verification and password reset emails
"""

from flask import current_app, render_template_string
from flask_mail import Mail, Message
import logging

# Initialize Flask-Mail (will be configured in app factory)
mail = Mail()

def send_email(to, subject, template, **kwargs):
    """
    Send an email using Flask-Mail
    
    Args:
        to (str): Recipient email address
        subject (str): Email subject
        template (str): Email template content
        **kwargs: Template variables
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[to],
            html=template,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # In development, just log the email instead of sending
        if current_app.config.get('FLASK_ENV') == 'development':
            current_app.logger.info(f"EMAIL TO: {to}")
            current_app.logger.info(f"SUBJECT: {subject}")
            current_app.logger.info(f"CONTENT: {template}")
            return True
        
        # In production, actually send the email
        mail.send(msg)
        current_app.logger.info(f"Email sent successfully to {to}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {to}: {str(e)}")
        return False

def send_verification_email(user, token):
    """
    Send email verification email to user
    
    Args:
        user: User object
        token (str): Verification token
    
    Returns:
        bool: True if email sent successfully
    """
    verification_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/verify-email/{token}"
    
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Verify Your Email - ChatApp</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Welcome to ChatApp!</h1>
            </div>
            <div class="content">
                <h2>Hi {user.first_name or user.username}!</h2>
                <p>Thanks for signing up for ChatApp. To complete your registration, please verify your email address by clicking the button below:</p>
                
                <p style="text-align: center;">
                    <a href="{verification_url}" class="button">Verify Email Address</a>
                </p>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background: #eee; padding: 10px; border-radius: 5px;">{verification_url}</p>
                
                <p><strong>This link will expire in 24 hours.</strong></p>
                
                <p>If you didn't create an account with ChatApp, you can safely ignore this email.</p>
                
                <p>Happy chatting!<br>The ChatApp Team</p>
            </div>
            <div class="footer">
                <p>© 2024 ChatApp. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(
        to=user.email,
        subject="Verify Your Email - ChatApp",
        template=template
    )

def send_password_reset_email(user, token):
    """
    Send password reset email to user
    
    Args:
        user: User object
        token (str): Password reset token
    
    Returns:
        bool: True if email sent successfully
    """
    reset_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/reset-password/{token}"
    
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Reset Your Password - ChatApp</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Password Reset Request</h1>
            </div>
            <div class="content">
                <h2>Hi {user.first_name or user.username}!</h2>
                <p>We received a request to reset your ChatApp password. If you made this request, click the button below to reset your password:</p>
                
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </p>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background: #eee; padding: 10px; border-radius: 5px;">{reset_url}</p>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong>
                    <ul>
                        <li>This link will expire in 1 hour for security reasons</li>
                        <li>If you didn't request this reset, please ignore this email</li>
                        <li>Your password will remain unchanged until you create a new one</li>
                    </ul>
                </div>
                
                <p>If you continue to have problems, please contact our support team.</p>
                
                <p>Stay secure!<br>The ChatApp Team</p>
            </div>
            <div class="footer">
                <p>© 2024 ChatApp. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(
        to=user.email,
        subject="Reset Your Password - ChatApp",
        template=template
    )

def send_welcome_email(user):
    """
    Send welcome email after successful email verification
    
    Args:
        user: User object
    
    Returns:
        bool: True if email sent successfully
    """
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Welcome to ChatApp!</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .feature {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #667eea; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Welcome to ChatApp!</h1>
            </div>
            <div class="content">
                <h2>Hi {user.first_name or user.username}!</h2>
                <p>Your email has been verified successfully! Welcome to the ChatApp community.</p>
                
                <h3>🚀 Get Started:</h3>
                <div class="feature">
                    <strong>💬 Join Chat Rooms:</strong> Connect with people in various topics and interests
                </div>
                <div class="feature">
                    <strong>📱 Private Messages:</strong> Send direct messages to other users
                </div>
                <div class="feature">
                    <strong>📁 File Sharing:</strong> Share images and files with your friends
                </div>
                <div class="feature">
                    <strong>🎨 Themes:</strong> Switch between light and dark themes
                </div>
                <div class="feature">
                    <strong>👤 Profile:</strong> Customize your profile and manage your account
                </div>
                
                <p>Ready to start chatting? <a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/login" style="color: #667eea;">Log in now</a> and join the conversation!</p>
                
                <p>If you have any questions or need help, don't hesitate to reach out to our support team.</p>
                
                <p>Happy chatting!<br>The ChatApp Team</p>
            </div>
            <div class="footer">
                <p>© 2024 ChatApp. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(
        to=user.email,
        subject="Welcome to ChatApp! 🎉",
        template=template
    )
