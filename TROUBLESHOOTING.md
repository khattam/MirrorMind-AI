# 🔧 Troubleshooting Guide

Common issues and solutions for MirrorMind deployment.

---

## 🚨 Backend Issues (Render)

### Issue: "Application failed to respond"

**Symptoms:**
- Render shows "Application failed to respond"
- Health check fails
- Service keeps restarting

**Solutions:**

1. **Check Render Logs:**
   - Go to your service → Logs tab
   - Look for Python errors or missing dependencies

2. **Verify Environment Variables:**
   ```
   AI_PROVIDER=groq
   GROQ_API_KEY=gsk_...
   GROQ_MODEL=llama-3.3-70b-versatile
   OPENAI_API_KEY=sk-...
   ```

3. **Check Start Command:**
   - Should be: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - NOT: `uvicorn main:app --port 8000` (hardcoded port won't work)

4. **Verify Python Version:**
   - Add environment variable: `PYTHON_VERSION=3.11.0`

---

### Issue: "ModuleNotFoundError"

**Symptoms:**
- Import errors in logs
- Missing package errors

**Solutions:**

1. **Update requirements.txt:**
   ```bash
   cd backend
   pip freeze > requirements.txt
   ```

2. **Verify all dependencies are listed:**
   ```
   fastapi==0.104.1
   uvicorn==0.24.0
   requests==2.31.0
   python-dotenv==1.0.0
   pydantic==2.5.0
   openai==1.3.0
   groq==0.4.0
   ```

3. **Redeploy on Render**

---

### Issue: "Groq API Error"

**Symptoms:**
- Agents not responding
- "Groq API error" in logs
- Debates fail to start

**Solutions:**

1. **Verify API Key:**
   - Go to [console.groq.com](https://console.groq.com)
   - Check if key is valid
   - Regenerate if needed

2. **Check API Limits:**
   - Free tier: 14,400 requests/day
   - Check if you've hit the limit

3. **Test API Key Locally:**
   ```bash
   curl https://api.groq.com/openai/v1/models \
     -H "Authorization: Bearer YOUR_KEY"
   ```

4. **Fallback to Ollama (Local Only):**
   - Change `AI_PROVIDER=ollama`
   - Note: Won't work on Render free tier

---

### Issue: "OpenAI API Error"

**Symptoms:**
- Agent enhancement fails
- "OpenAI API error" in logs
- Can't create custom agents

**Solutions:**

1. **Verify API Key:**
   - Go to [platform.openai.com](https://platform.openai.com/api-keys)
   - Check if key is valid
   - Check if you have credits

2. **Check Billing:**
   - OpenAI requires payment method
   - Add credits to your account

3. **Test API Key:**
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_KEY"
   ```

---

### Issue: "Cold Start Delays"

**Symptoms:**
- First request takes 15-30 seconds
- Service "wakes up" slowly

**Solutions:**

1. **This is normal on Render free tier**
   - Services sleep after 15 min inactivity
   - First request wakes them up

2. **Upgrade to Starter Plan ($7/month):**
   - No cold starts
   - Always-on service

3. **Keep Service Warm (Workaround):**
   - Use a service like [UptimeRobot](https://uptimerobot.com)
   - Ping your backend every 10 minutes
   - Free tier allows this

---

## 🎨 Frontend Issues (Vercel)

### Issue: "Failed to fetch" / Network Errors

**Symptoms:**
- Frontend loads but can't connect to backend
- "Failed to fetch" errors in console
- Agents don't respond

**Solutions:**

1. **Check VITE_API_URL:**
   - Go to Vercel → Your Project → Settings → Environment Variables
   - Should be: `https://your-backend.onrender.com`
   - NO trailing slash!

2. **Verify Backend is Running:**
   - Visit your backend URL directly
   - Should see: `{"message": "MirrorMinds backend is running!"}`

3. **Check CORS Settings:**
   - Update `backend/main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://your-app.vercel.app",
           "http://localhost:5173"
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
   - Redeploy backend on Render

4. **Check Browser Console:**
   - Open DevTools (F12)
   - Look for CORS errors
   - Look for 404/500 errors

---

### Issue: "Build Failed" on Vercel

**Symptoms:**
- Deployment fails
- Build errors in Vercel logs

**Solutions:**

1. **Check Build Command:**
   - Should be: `npm run build`
   - Root directory: `frontend`

2. **Verify package.json:**
   ```json
   {
     "scripts": {
       "build": "vite build"
     }
   }
   ```

3. **Check Node Version:**
   - Vercel uses Node 18 by default
   - Should work fine

4. **Test Build Locally:**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

---

### Issue: "Page Not Found" (404)

**Symptoms:**
- Homepage loads but other routes show 404
- Refresh breaks the app

**Solutions:**

1. **Check vercel.json:**
   ```json
   {
     "rewrites": [
       {
         "source": "/(.*)",
         "destination": "/index.html"
       }
     ]
   }
   ```

2. **Redeploy on Vercel**

---

## 🗄️ Data Persistence Issues

### Issue: "Agents disappear after redeploy"

**Symptoms:**
- Custom agents lost after Render redeploy
- Debate history resets

**Solutions:**

1. **Add Persistent Disk on Render:**
   - Go to your service → Environment → Disks
   - Add disk:
     - Name: `data`
     - Mount Path: `/opt/render/project/src/backend/data`
     - Size: 1 GB

2. **Or Use External Database:**
   - PostgreSQL on Render
   - Supabase (free tier)
   - MongoDB Atlas (free tier)

---

## 🔐 Security Issues

### Issue: "API Keys Exposed"

**Symptoms:**
- API keys visible in frontend code
- Keys in GitHub repository

**Solutions:**

1. **Never commit .env files:**
   - Check `.gitignore` includes `.env`
   - Remove from git history if committed:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch backend/.env" \
     --prune-empty --tag-name-filter cat -- --all
   ```

2. **Rotate Compromised Keys:**
   - Regenerate on Groq/OpenAI
   - Update on Render

3. **Use Environment Variables:**
   - Backend: Use Render environment variables
   - Frontend: Use Vercel environment variables
   - Never hardcode keys

---

## 📦 Dependency & Build Issues

### Issue: "Failed building wheel for pydantic-core"

**Symptoms:**
- Build fails with Rust compilation errors
- `TypeError: ForwardRef._evaluate()` errors
- Python version incompatibility

**Solutions:**

1. **Pin Python Version:**
   - Create `backend/runtime.txt`:
   ```
   python-3.11.9
   ```
   - Update `render.yaml`:
   ```yaml
   envVars:
     - key: PYTHON_VERSION
       value: 3.11.0
   ```

2. **Use Compatible Versions:**
   ```
   fastapi==0.115.0
   uvicorn==0.32.0
   pydantic==2.10.0
   groq==0.9.0
   openai==1.54.0
   ```

3. **Upgrade Build Tools:**
   - Update `render.yaml` buildCommand:
   ```yaml
   buildCommand: pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
   ```

---

### Issue: "TypeError: Client.__init__() got unexpected keyword argument 'proxies'"

**Symptoms:**
- Build succeeds but deployment fails
- Groq client initialization error
- httpx version conflict

**Solutions:**

1. **Downgrade groq:**
   ```
   groq==0.9.0
   ```
   (Version 0.11.0 has httpx compatibility issues)

2. **Test Locally First:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -c "from groq import Groq; print('OK')"
   ```

---

### Best Practices for Dependencies

1. **Always Test Locally Before Deploying:**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Pin Exact Versions:**
   - Use `==` not `>=` in requirements.txt
   - Prevents unexpected breaking changes

3. **Document Python Version:**
   - Add `runtime.txt` to specify Python version
   - Prevents platform from using incompatible versions

4. **Keep Dependencies Minimal:**
   - Only include what you actually use
   - Reduces build time and potential conflicts

5. **Test After Updates:**
   ```bash
   # Update a package
   pip install package==new.version
   
   # Test it works
   python -m pytest  # or run your app
   
   # Update requirements
   pip freeze > requirements.txt
   ```

---

## 🐛 General Debugging

### Check Render Logs

```bash
# View live logs
# Go to: Render Dashboard → Your Service → Logs
```

### Check Vercel Logs

```bash
# View deployment logs
# Go to: Vercel Dashboard → Your Project → Deployments → View Function Logs
```

### Test Backend Locally

```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn main:app --reload
```

### Test Frontend Locally

```bash
cd frontend
npm run dev
```

### Test Production Build Locally

```bash
cd frontend
npm run build
npm run preview
```

---

## 📞 Still Stuck?

1. **Check Render Status:** [status.render.com](https://status.render.com)
2. **Check Vercel Status:** [vercel-status.com](https://www.vercel-status.com)
3. **Search GitHub Issues:** [github.com/khattam/MirrorMind/issues](https://github.com/khattam/MirrorMind/issues)
4. **Open New Issue:** Include:
   - Error messages
   - Logs from Render/Vercel
   - Steps to reproduce
   - What you've tried

---

## 🎯 Quick Diagnostic Commands

**Test Backend Health:**
```bash
curl https://your-backend.onrender.com/
```

**Test Agents API:**
```bash
curl https://your-backend.onrender.com/api/agents
```

**Test Frontend:**
```bash
curl https://your-app.vercel.app
```

**Test CORS:**
```bash
curl -H "Origin: https://your-app.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://your-backend.onrender.com/api/agents
```

---

**Good luck! 🚀**
