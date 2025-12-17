# 🚀 Deploy to Vercel + Railway (100% Free, No Credit Card)

Quick guide to deploy your World Cup Predictor for free using Vercel (frontend) and Railway (backend).

---

## Part 1: Deploy Backend on Railway

### Step 1: Sign Up for Railway
1. Go to **https://railway.app**
2. Click **"Login"** → **"Login with GitHub"**
3. Authorize Railway to access your GitHub

### Step 2: Deploy Backend
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose **`Parman-Sangha/2026-World-Cup-Predictor`**
4. Railway will detect it's a Python project
5. Click **"Add variables"** and set:
   - **Root Directory**: `backend`
6. Click **"Deploy"**
7. Wait ~2 minutes for deployment

### Step 3: Get Backend URL
1. Go to your project → **Settings** → **Networking**
2. Click **"Generate Domain"**
3. **Copy the URL** (e.g., `https://your-app.up.railway.app`)

---

## Part 2: Deploy Frontend on Vercel

### Step 1: Sign Up for Vercel
1. Go to **https://vercel.com/signup**
2. Click **"Continue with GitHub"**
3. Authorize Vercel

### Step 2: Deploy Frontend
1. Click **"Add New..."** → **"Project"**
2. Import **`Parman-Sangha/2026-World-Cup-Predictor`**
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: Leave as `./` (Vercel will use `vercel.json`)
4. **Add Environment Variable**:
   - **Name**: `VITE_API_URL`
   - **Value**: (paste your Railway backend URL from Part 1, Step 3)
5. Click **"Deploy"**
6. Wait ~1 minute

---

## Part 3: Test Your Live App! 🎉

1. Vercel will give you a URL like: `https://your-app.vercel.app`
2. Open it in your browser
3. Test:
   - ✅ Select teams from dropdowns
   - ✅ Run match predictions
   - ✅ Run tournament simulation

---

## Important Notes

### Railway Free Tier
- **$5 credit/month** (resets monthly)
- Enough for ~500 hours of runtime
- **No credit card required**
- App stays active as long as you have credit

### Vercel Free Tier
- **Unlimited** bandwidth
- **100 GB** bandwidth/month
- **No credit card required**
- Always-on static hosting

### First Load Delay
- Railway may take 30-60 seconds on first request if inactive
- Subsequent requests are instant

---

## Troubleshooting

**Frontend can't connect to backend:**
1. Check `VITE_API_URL` is set correctly in Vercel
2. Make sure Railway backend is running
3. Check Railway logs for errors

**Teams not loading:**
1. Verify `backend/data/` folder has CSV files
2. Check Railway deployment logs

**Railway deployment failed:**
1. Make sure `backend/requirements.txt` exists
2. Check Railway build logs for Python errors

---

## Your Live URLs

After deployment:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-app.up.railway.app`

Share your frontend URL with anyone! 🌍⚽
