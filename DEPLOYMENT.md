# 🚀 MirrorMind Deployment Guide

Complete guide for deploying MirrorMind on Render (Backend) + Vercel (Frontend).

---

## 📋 Prerequisites

Before deploying, make sure you have:

- ✅ GitHub account with your MirrorMind repository
- ✅ [Render account](https://render.com) (free tier works!)
- ✅ [Vercel account](https://vercel.com) (free tier works!)
- ✅ [Groq API key](https://console.groq.com) (free tier available)
- ✅ [OpenAI API key](https://platform.openai.com/api-keys) (required for agent enhancement)

---

## 🎯 Part 1: Deploy Backend on Render

### Step 1: Push Your Code to GitHub

```bash
git add .
git commit -m "Add deployment configuration"
git push origin main
```

### Step 2: Create New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select **"khattam/MirrorMind-AI"** (or your repo name)

### Step 3: Configure the Service

Render should auto-detect the `render.yaml` file, but verify these settings:

**Basic Settings:**
- **Name:** `mirrormind-backend` (or your choice)
- **Region:** Oregon (or closest to you)
- **Branch:** `main`
- **Root Directory:** `backend`
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Environment Variables:**

Click **"Advanced"** → **"Add Environment Variable"** and add:

| Key | Value | Notes |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.11.0` | Python version |
| `AI_PROVIDER` | `groq` | Use Groq for debates |
| `GROQ_API_KEY` | `gsk_...` | Your Groq API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Model name |
| `OPENAI_API_KEY` | `sk-...` | Your OpenAI key |

### Step 4: Deploy!

1. Click **"Create Web Service"**
2. Wait 3-5 minutes for deployment
3. Once deployed, you'll get a URL like: `https://mirrormind-backend.onrender.com`

### Step 5: Test Your Backend

Visit: `https://your-backend-url.onrender.com`

You should see:
```json
{"message": "MirrorMinds backend is running!"}
```

✅ **Backend is live!** Copy your backend URL for the next step.

---

## 🎨 Part 2: Deploy Frontend on Vercel

### Step 1: Go to Vercel Dashboard

1. Visit [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository

### Step 2: Configure the Project

**Framework Preset:** Vite (should auto-detect)

**Root Directory:** `frontend`

**Build Settings:**
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

### Step 3: Add Environment Variables

Click **"Environment Variables"** and add:

| Key | Value | Environment |
|-----|-------|-------------|
| `VITE_API_URL` | `https://your-backend-url.onrender.com` | Production |

⚠️ **Important:** Replace `your-backend-url.onrender.com` with your actual Render backend URL from Part 1!

### Step 4: Deploy!

1. Click **"Deploy"**
2. Wait 2-3 minutes for build
3. You'll get a URL like: `https://mirrormind.vercel.app`

### Step 5: Test Your Frontend

1. Visit your Vercel URL
2. Try creating a debate
3. Check if agents respond properly

✅ **Frontend is live!**

---

## 🔧 Post-Deployment Configuration

### Update CORS Settings (if needed)

If you get CORS errors, update `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-vercel-app.vercel.app",
        "http://localhost:5173"  # Keep for local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy on Render.

### Enable Persistent Storage on Render

By default, Render's free tier has ephemeral storage. Your agent data will reset on each deploy.

**To persist data:**

1. Go to your Render service
2. Click **"Environment"** → **"Disks"**
3. Add a disk:
   - **Name:** `data`
   - **Mount Path:** `/opt/render/project/src/backend/data`
   - **Size:** 1 GB (free tier limit)

---

## 🎯 Verification Checklist

After deployment, verify:

- [ ] Backend health check returns success
- [ ] Frontend loads without errors
- [ ] Can submit a dilemma
- [ ] Agents generate opening arguments
- [ ] Counter-arguments work
- [ ] Judge provides verdict
- [ ] Agent builder works (enhancement)
- [ ] Custom agents can be created
- [ ] Debate history is saved

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** "Application failed to respond"
- Check Render logs for errors
- Verify all environment variables are set
- Ensure `PORT` is not hardcoded (use `$PORT`)

**Problem:** "Groq API error"
- Verify your Groq API key is valid
- Check if you have API credits
- Try switching to `AI_PROVIDER=ollama` (but won't work on Render free tier)

**Problem:** "OpenAI API error"
- Verify your OpenAI API key
- Check if you have credits
- Agent enhancement won't work without valid OpenAI key

### Frontend Issues

**Problem:** "Failed to fetch"
- Check if `VITE_API_URL` is set correctly
- Verify backend is running
- Check browser console for CORS errors

**Problem:** "Agents not responding"
- Check backend logs on Render
- Verify Groq API is working
- Test backend endpoint directly

### Data Persistence Issues

**Problem:** "Agents disappear after redeploy"
- Add persistent disk on Render (see above)
- Or use a database (requires paid plan or external service)

---

## 💰 Cost Breakdown

### Free Tier Limits

**Render Free Tier:**
- ✅ 750 hours/month (enough for 1 service)
- ✅ Automatic sleep after 15 min inactivity
- ✅ 512 MB RAM
- ⚠️ Cold starts (15-30 seconds)
- ⚠️ Ephemeral storage (resets on deploy)

**Vercel Free Tier:**
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Global CDN

**Groq Free Tier:**
- ✅ 14,400 requests/day
- ✅ Fast inference
- ✅ Multiple models

**OpenAI:**
- 💰 Pay-as-you-go
- ~$0.01-0.03 per agent enhancement
- GPT-4o-mini recommended for cost savings

---

## 🚀 Going to Production

### Recommended Upgrades

1. **Render Starter Plan ($7/month)**
   - No cold starts
   - Persistent storage
   - Better performance

2. **Database Integration**
   - PostgreSQL on Render
   - Or Supabase (free tier available)
   - Replaces JSON file storage

3. **Custom Domain**
   - Add to Vercel (free)
   - Add to Render ($0)

4. **Monitoring**
   - Render built-in metrics
   - Sentry for error tracking
   - LogRocket for session replay

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)

---

## 🎉 Success!

Your MirrorMind app is now live! Share your deployment:

- Backend: `https://your-backend.onrender.com`
- Frontend: `https://your-app.vercel.app`

Update your README.md with the live demo link! 🚀

---

## 🆘 Need Help?

If you run into issues:

1. Check Render logs: Dashboard → Your Service → Logs
2. Check Vercel logs: Dashboard → Your Project → Deployments → View Function Logs
3. Check browser console for frontend errors
4. Open an issue on GitHub

Good luck! 🌟
