# Fix Registration on Render - Deployment Guide

## Problem
SQLite database on Render gets wiped after each deployment/restart because Render's filesystem is ephemeral.

## Solution
Use PostgreSQL (free on Render) for production while keeping SQLite for local development.

## Changes Made

### 1. Updated Files
- ✅ `requirements.txt` - Added `psycopg2-binary` for PostgreSQL support
- ✅ `render.yaml` - Added PostgreSQL database configuration
- ✅ `database.py` - Updated to support both PostgreSQL and SQLite
- ✅ `app.py` - Fixed registration validation issues

### 2. Database Configuration
The app now automatically detects the environment:
- **Local (no DATABASE_URL)**: Uses SQLite (`parkease.db`)
- **Render (DATABASE_URL exists)**: Uses PostgreSQL

## Deployment Steps

### Step 1: Commit and Push Changes
```bash
git add .
git commit -m "Fix: Add PostgreSQL support for Render deployment"
git push origin main
```

### Step 2: Deploy to Render
1. Go to your Render dashboard: https://dashboard.render.com
2. Your app will automatically detect the new `render.yaml` file
3. Render will:
   - Create a new PostgreSQL database named `carpark-db`
   - Install `psycopg2-binary` from requirements.txt
   - Connect your web service to the database automatically

### Step 3: Verify Deployment
1. Wait for the deployment to complete (usually 2-5 minutes)
2. Check the logs for "Database initialized successfully"
3. Visit your app URL
4. Try registering a new user - it should work now!

## How It Works

### Database Auto-Detection
```python
DATABASE_URL = os.environ.get('DATABASE_URL')  # Set by Render
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    # Use PostgreSQL on Render
    conn = psycopg2.connect(DATABASE_URL)
else:
    # Use SQLite locally
    conn = sqlite3.connect('parkease.db')
```

### SQL Compatibility
The code now handles differences between PostgreSQL and SQLite:
- **Primary Keys**: `SERIAL` (PostgreSQL) vs `AUTOINCREMENT` (SQLite)
- **Text Type**: `VARCHAR` (PostgreSQL) vs `TEXT` (SQLite)
- **Parameters**: `%s` (PostgreSQL) vs `?` (SQLite)

## Testing Locally

Your local environment still uses SQLite, so nothing changes for local development:

```bash
# Activate virtual environment
.venv-1\Scripts\Activate.ps1

# Run locally (uses SQLite)
python app.py
```

## Troubleshooting

### If registration still fails on Render:

1. **Check Render Logs**
   - Go to your Render dashboard
   - Click on your web service
   - View logs for error messages

2. **Verify Database Connection**
   - Ensure the PostgreSQL database was created
   - Check that DATABASE_URL is set in environment variables

3. **Manual Database Check**
   - In Render dashboard, go to your PostgreSQL database
   - Click "Connect" and use psql command to verify tables exist:
   ```sql
   \dt  -- List all tables
   SELECT * FROM users;  -- Check users table
   ```

### Common Issues:

**Database not created**: Re-deploy from Render dashboard

**Connection timeout**: Check if database is in same region as web service

**Import error for psycopg2**: Clear build cache and redeploy

## Benefits of This Setup

✅ **Persistent Data**: User registrations persist across deployments
✅ **Scalable**: PostgreSQL handles concurrent users better
✅ **Local Development**: Still uses simple SQLite locally
✅ **Zero Configuration**: Automatically detects environment
✅ **Free**: Render's PostgreSQL free tier is sufficient

## Next Steps

After successful deployment:
1. Test user registration on live site
2. Test user login
3. Create a few test bookings
4. Verify data persists after redeployment

## Support

If you encounter issues:
- Check Render logs for specific error messages
- Verify all files are committed and pushed
- Ensure render.yaml is in repository root
- Contact Render support if database provisioning fails
