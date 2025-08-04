# 🚀 Real-Time Chat Application

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-chatapp--3g10.onrender.com-blue?style=for-the-badge)](https://chatapp-3g10.onrender.com)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/vaibhavpatil29/real-time-chat-app)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1+-green?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com)

A modern, secure real-time chat application built with Flask, SocketIO, and PostgreSQL. Features comprehensive authentication, real-time messaging, emoji picker, and a beautiful responsive UI.

## 🌟 **[Try the Live Demo →](https://chatapp-3g10.onrender.com)**

> **Note**: The free tier may take 30-60 seconds to wake up from sleep mode on first visit.

## ✨ Features

### 🔐 Authentication & Security
- **Secure Registration** with password strength validation
- **Email Verification** system
- **Password Reset** functionality
- **Account Lockout** protection (5 failed attempts)
- **Session Management** with "Remember Me" option
- **Rate Limiting** to prevent abuse
- **CSRF Protection** and security headers
- **Profile Management** with avatar support

### 💬 Real-Time Chat
- **Instant Messaging** with WebSocket technology
- **Multiple Chat Rooms** support
- **Custom Emoji Picker** with 90+ emojis
- **Quick Emoji Bar** for popular emojis
- **Online User Status** tracking
- **Message History** persistence
- **Mobile-Optimized** chat interface

### 🎨 Modern UI/UX
- **Dark/Light Theme** toggle with smooth transitions
- **Fully Responsive Design** for all devices
- **Mobile Users Sidebar** with slide-out animation
- **Beautiful Glass-morphism** design
- **Touch-Friendly Interface** (44px+ touch targets)
- **Modern Animations** and micro-interactions
- **Professional Gradient Backgrounds**

## 🛠️ Technology Stack

- **Backend**: Flask 3.1+, Flask-SocketIO, SQLAlchemy
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Real-time**: WebSocket with Socket.IO
- **Authentication**: Flask-Login, Werkzeug Security
- **Deployment**: Render.com with gunicorn + eventlet
- **Security**: CSRF protection, rate limiting, password hashing

## 🌐 Live Deployment

**Live Demo**: [https://chatapp-3g10.onrender.com](https://chatapp-3g10.onrender.com)

### Deployment Features:
- ✅ **Production Ready** - Deployed on Render.com
- ✅ **PostgreSQL Database** - Persistent data storage
- ✅ **HTTPS Enabled** - Secure connections
- ✅ **Auto-scaling** - Handles multiple users
- ✅ **WebSocket Support** - Real-time messaging
- ✅ **Mobile Optimized** - Works on all devices

### Test the Live App:
1. **Visit**: [chatapp-3g10.onrender.com](https://chatapp-3g10.onrender.com)
2. **Register** a new account or login
3. **Start chatting** in the general room
4. **Test responsive design** on mobile/tablet
5. **Try dark/light themes** and emoji picker

## 📋 Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Node.js (for frontend dependencies, optional)
- Git

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/real-time-chat-app.git
cd real-time-chat-app
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Database

1. **Install PostgreSQL** if not already installed
2. **Create Database**:
   ```sql
   CREATE DATABASE chatdb;
   ```
3. **Update Configuration** in `config.py` if needed

### 5. Set Up Database Schema
```bash
# Run the migration script
python create_migration.py
```

### 6. Run the Application
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/chatdb

# Email Configuration (for email verification)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Redis (for rate limiting, optional)
REDIS_URL=redis://localhost:6379/0
```

### Database Configuration
Update `config.py` with your database credentials:

```python
SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/chatdb'
```

## 📚 API Documentation

### Authentication Endpoints

- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout
- `POST /forgot-password` - Request password reset
- `POST /reset-password/<token>` - Reset password with token
- `GET /verify-email/<token>` - Verify email address
- `POST /resend-verification` - Resend verification email

### Profile Management

- `GET /profile` - View user profile
- `POST /profile/edit` - Update profile
- `POST /change-password` - Change password

### API Endpoints

- `GET /api/check-username` - Check username availability
- `GET /api/check-email` - Check email availability

### WebSocket Events

- `connect` - User connects to chat
- `disconnect` - User disconnects
- `join_room` - Join a chat room
- `send_message` - Send a message
- `send_file` - Send a file
- `typing` - Typing indicator
- `private_message` - Send private message

## 🔒 Security Features

### Password Security
- Minimum 8 characters
- Must contain uppercase, lowercase, number, and special character
- Bcrypt hashing with salt
- Password strength indicator

### Account Protection
- Account lockout after 5 failed login attempts
- 30-minute lockout duration
- Rate limiting on sensitive endpoints
- CSRF protection on all forms

### Session Security
- Secure session cookies
- HttpOnly and SameSite flags
- Configurable session timeout
- "Remember Me" functionality

## 🎨 UI Themes

The application supports both light and dark themes:
- **Light Theme**: Clean, modern interface
- **Dark Theme**: Easy on the eyes for low-light environments
- **Auto-switching**: Remembers user preference

## 📱 Responsive Design

Optimized for all screen sizes:
- **Desktop**: Full-featured interface
- **Tablet**: Adapted layout with touch-friendly controls
- **Mobile**: Streamlined interface for small screens

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

## 🚀 Deployment

### Production Setup

1. **Set Environment Variables**:
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret-key
   ```

2. **Configure Database**:
   - Use production PostgreSQL instance
   - Set up SSL connections
   - Configure connection pooling

3. **Set Up Web Server**:
   - Use Gunicorn or uWSGI
   - Configure Nginx reverse proxy
   - Set up SSL certificates

4. **Security Considerations**:
   - Enable HTTPS
   - Set secure session cookies
   - Configure firewall rules
   - Set up monitoring and logging

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "run:app"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Check PostgreSQL is running
   - Verify database credentials
   - Ensure database exists

2. **Migration Errors**:
   - Delete migrations folder and recreate
   - Check database permissions
   - Verify model definitions

3. **Socket.IO Issues**:
   - Check firewall settings
   - Verify WebSocket support
   - Check browser compatibility

### Getting Help

- Check the [Issues](https://github.com/your-username/real-time-chat-app/issues) page
- Read the [Wiki](https://github.com/your-username/real-time-chat-app/wiki)
- Join our [Discord](https://discord.gg/your-invite) community

## 🙏 Acknowledgments

- Flask and Flask-SocketIO communities
- Socket.IO for real-time communication
- PostgreSQL for reliable data storage
- All contributors and testers

---

**Made with ❤️ by [Your Name](https://github.com/your-username)** 
