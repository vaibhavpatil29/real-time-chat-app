# Manual Render Deployment (Alternative Method)

If the Blueprint deployment has issues, follow these manual steps:

## Step 1: Create PostgreSQL Database
1. Go to [render.com](https://render.com) dashboard
2. Click **"New" → "PostgreSQL"**
3. Configure:
   - **Name**: `chatapp-db`
   - **Database**: `chatapp`
   - **User**: `chatapp` (auto-generated)
   - **Region**: Oregon (US West)
   - **Plan**: Free
4. Click **"Create Database"**
5. **Copy the External Database URL** (you'll need this)

## Step 2: Create Web Service
1. Click **"New" → "Web Service"**
2. **Connect Repository**: Select `vaibhavpatil29/real-time-chat-app`
3. Configure:
   - **Name**: `chatapp`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app`
   - **Plan**: Free

## Step 3: Set Environment Variables
In the web service, go to "Environment" and add:

```
FLASK_ENV=production
SECRET_KEY=[Click "Generate" for auto value]
DATABASE_URL=[Paste the External Database URL from Step 1]
SESSION_COOKIE_SECURE=true
REMEMBER_COOKIE_SECURE=true
```

## Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Your app will be live at: `https://chatapp-[random].onrender.com`

## Step 5: Initialize Database
After first deployment:
1. Go to your web service dashboard
2. Click **"Shell"** tab
3. Run: `python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"`

## Troubleshooting
- **Build fails**: Check logs for missing dependencies
- **Database connection**: Verify DATABASE_URL is correct
- **App crashes**: Check if all environment variables are set
- **WebSocket issues**: Ensure eventlet worker is used in start command

Your app should be live and working!
