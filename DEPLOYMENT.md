# 🚀 Deploying Your World Cup Predictor to Render

This guide will help you deploy your app for **free** on Render.com.

## Prerequisites

- GitHub account
- Render account (free) - Sign up at [render.com](https://render.com)

---

## Step 1: Push Your Code to GitHub

If you haven't already, create a GitHub repository and push your code:

```bash
cd /Users/parmansangha/2026-World-Cup-Predictor

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/2026-World-Cup-Predictor.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy to Render

### Option A: One-Click Deploy with Blueprint (Recommended)

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New" → "Blueprint"**
3. **Connect your GitHub repository**
4. **Select the repository**: `2026-World-Cup-Predictor`
5. Render will automatically detect the `render.yaml` file
6. **Click "Apply"** to deploy both services

### Option B: Manual Deploy

If the blueprint doesn't work, deploy manually:

#### Deploy Backend:
1. Click **"New +" → "Web Service"**
2. Connect your GitHub repo
3. Configure:
   - **Name**: `worldcup-predictor-api`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
4. Click **"Create Web Service"**
5. **Copy the backend URL** (e.g., `https://worldcup-predictor-api.onrender.com`)

#### Deploy Frontend:
1. Click **"New +" → "Static Site"**
2. Connect your GitHub repo
3. Configure:
   - **Name**: `worldcup-predictor-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
4. **Add Environment Variable**:
   - Key: `VITE_API_URL`
   - Value: `https://worldcup-predictor-api.onrender.com` (your backend URL from step 5)
5. Click **"Create Static Site"**

---

## Step 3: Wait for Deployment

- Backend: ~2-3 minutes
- Frontend: ~1-2 minutes

You'll see build logs in real-time. Once complete, you'll get URLs like:
- **Backend**: `https://worldcup-predictor-api.onrender.com`
- **Frontend**: `https://worldcup-predictor-frontend.onrender.com`

---

## Step 4: Test Your Deployed App

1. Open your frontend URL
2. Try selecting teams and running predictions
3. Try running a tournament simulation

---

## Important Notes

### Free Tier Limitations
- **Backend**: Spins down after 15 minutes of inactivity
  - First request after inactivity may take 30-60 seconds to wake up
  - Subsequent requests will be fast
- **Frontend**: Always available (static site)

### Custom Domain (Optional)
You can add a custom domain in Render's settings for free!

---

## Troubleshooting

### Frontend can't connect to backend
1. Check that `VITE_API_URL` environment variable is set correctly in frontend settings
2. Make sure backend is deployed and running
3. Check backend logs for errors

### Backend won't start
1. Check build logs for Python dependency errors
2. Verify `requirements.txt` is correct
3. Make sure data files are included in the repository

### Teams not loading
- The backend needs the CSV data files in `backend/data/`
- Make sure these files are committed to your GitHub repository

---

## Your Deployed URLs

After deployment, your app will be live at:
- **Frontend**: `https://worldcup-predictor-frontend.onrender.com`
- **Backend API**: `https://worldcup-predictor-api.onrender.com`

Share the frontend URL with anyone to let them use your World Cup Predictor! 🎉
