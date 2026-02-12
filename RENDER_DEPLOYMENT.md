# Deploy to Render - Step by Step Guide

## Files Created for Deployment ✅

1. **requirements.txt** - Python dependencies
2. **render.yaml** - Render configuration
3. **Procfile** - Startup command
4. **runtime.txt** - Python version
5. **.gitignore** - Files to exclude from Git

## Deployment Steps

### Step 1: Push Code to GitHub

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Ready for Render deployment"
   ```

2. **Create GitHub Repository**:
   - Go to https://github.com/new
   - Name: `CarParkProject` (or any name)
   - Don't initialize with README
   - Click "Create repository"

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/CarParkProject.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Render

1. **Sign Up/Login to Render**:
   - Go to https://render.com
   - Sign up with GitHub (recommended)

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `CarParkProject`

3. **Configure Service**:
   - **Name**: `carpark-project` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`

4. **Advanced Settings** (Optional):
   - Add Environment Variables if needed
   - Set Health Check Path: `/`

5. **Create Web Service** - Click the button!

### Step 3: Wait for Deployment

- Render will:
  - Clone your repository
  - Install dependencies (~5-10 minutes)
  - Start your application
  
- Watch the logs for any errors

### Step 4: Access Your App

Once deployed, you'll get a URL like:
```
https://carpark-project.onrender.com
```

Share this with your evaluators!

## Important Notes

⚠️ **Free Tier Limitations**:
- App sleeps after 15 minutes of inactivity
- Takes 30-60 seconds to wake up on first request
- 750 hours/month free

⚠️ **Database**:
- SQLite will work but data resets on each deployment
- For persistent data, upgrade to PostgreSQL (also has free tier)

⚠️ **Video Processing**:
- May be slow on free tier
- Limited CPU/RAM
- Consider disabling real-time video for demo

## Troubleshooting

**Build Fails?**
- Check logs in Render dashboard
- Verify requirements.txt has correct packages
- Check Python version compatibility

**App Crashes?**
- Look for errors in Render logs
- May need to disable video processing
- Check file paths (use relative paths)

**Database Issues?**
- SQLite file won't persist between deploys
- Need to initialize DB on startup
- Consider PostgreSQL for production

## Testing Locally First

Before deploying, test with Gunicorn locally:
```bash
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:5000
```

If this works, deployment should work!

## Admin Access

Login to admin dashboard at:
```
https://your-app.onrender.com/admin/login
Email: admin@parkease.com
Password: admin123
```

**⚠️ Change these credentials after deployment!**

## Next Steps After Deployment

1. Test all features on live URL
2. Share URL with evaluators
3. Monitor Render logs for errors
4. Consider upgrading for better performance
5. Add custom domain (optional)

---

Need help? Check Render docs: https://docs.render.com
