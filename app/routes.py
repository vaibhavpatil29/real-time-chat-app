from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Message
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.chat', room='general'))
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists.')
            return redirect(url_for('main.register'))

        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registered successfully. Please log in.')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.chat', room='general'))

        flash('Invalid username or password.')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/chat/<room>')
@login_required
def chat(room):
    messages = Message.query.filter_by(room=room).order_by(Message.timestamp).all()
    return render_template('chat.html', username=current_user.username, messages=messages, room=room)
