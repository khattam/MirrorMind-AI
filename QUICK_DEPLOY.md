# ⚡ Quick Deploy Reference

**5-minute deployment guide for MirrorMind**

---

## 🎯 What You Need

1. **GitHub repo** with your code
2. **Groq API key** → [console.groq.com](https://console.groq.com)
3. **OpenAI API key** → [platform.openai.com](https://platform.openai.com/api-keys)
4. **Render account** → [render.com](https://render.com)
5. **Vercel account** → [vercel.com](https://vercel.com)

---

## 🚀 Deploy Backend (Render)

1. **Go to Render** → New Web Service
2. **Connect GitHub** → Select your repo
3. **Configure:**
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Add Environment Variables:**
   ```
   AI_PROVIDER=groq
   GROQ_API_KEY=your_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   OPENAI_API_KEY=your_key_here
   ```
5. **Deploy** → Copy your backend URL

---

## 🎨 Deploy Frontend (Vercel)

1. **Go to Vercel** → New Project
2. **Import GitHub** → Select your repo
3. **Configure:**
   - Root Directory: `frontend`
   - Framework: Vite
4. **Add Environment Variable:**
   ```
   VITE_API_URL=https://your-backend-url.onrender.com
   ```
5. **Deploy** → Done!

---

## ✅ Test It

Visit your Vercel URL and:
- Submit a dilemma
- Watch agents debate
- Create a custom agent

---

## 🐛 Issues?

**Backend not responding?**
- Check Render logs
- Verify API keys are set
- Wait for cold start (15-30 sec)

**Frontend can't connect?**
- Check `VITE_API_URL` is correct
- Verify backend is running
- Check browser console

**Need help?** See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide.

---

**Total Time:** ~10 minutes  
**Total Cost:** $0 (free tier)  
**Difficulty:** Easy 🟢
