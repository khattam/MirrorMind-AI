# 🚀 Pre-Deployment Checklist

Use this checklist before deploying to production.

## 📋 Backend Checklist

- [ ] All environment variables documented in `.env.example`
- [ ] `requirements.txt` is up to date
- [ ] No hardcoded API keys in code
- [ ] CORS origins configured properly
- [ ] Health check endpoint works (`/`)
- [ ] All API endpoints tested locally
- [ ] Error handling in place
- [ ] Logging configured

## 📋 Frontend Checklist

- [ ] `VITE_API_URL` uses environment variable
- [ ] No hardcoded backend URLs
- [ ] Build command works (`npm run build`)
- [ ] Production build tested locally (`npm run preview`)
- [ ] All API calls handle errors gracefully
- [ ] Loading states implemented
- [ ] Mobile responsive design tested

## 📋 API Keys Required

- [ ] **Groq API Key** - Get from [console.groq.com](https://console.groq.com)
- [ ] **OpenAI API Key** - Get from [platform.openai.com](https://platform.openai.com/api-keys)

## 📋 Deployment Steps

### Render (Backend)

1. - [ ] Push code to GitHub
2. - [ ] Create new Web Service on Render
3. - [ ] Connect GitHub repository
4. - [ ] Configure build/start commands
5. - [ ] Add environment variables
6. - [ ] Deploy and test
7. - [ ] Copy backend URL

### Vercel (Frontend)

1. - [ ] Import project from GitHub
2. - [ ] Set root directory to `frontend`
3. - [ ] Add `VITE_API_URL` environment variable
4. - [ ] Deploy and test
5. - [ ] Verify API connection works

## 📋 Post-Deployment

- [ ] Test all major features
- [ ] Check browser console for errors
- [ ] Verify agent creation works
- [ ] Test debate flow end-to-end
- [ ] Check mobile responsiveness
- [ ] Update README with live demo link
- [ ] Monitor Render logs for errors
- [ ] Set up error tracking (optional)

## 🎯 Quick Test Script

After deployment, test these features:

1. **Homepage loads** ✓
2. **Submit a dilemma** ✓
3. **Agents generate arguments** ✓
4. **Continue debate** ✓
5. **Judge provides verdict** ✓
6. **Open Agent Builder** ✓
7. **Create custom agent** ✓
8. **View agent library** ✓
9. **View debate history** ✓
10. **Delete debate** ✓

## 🐛 Common Issues

### Backend won't start
- Check Python version (3.11+)
- Verify all dependencies installed
- Check environment variables

### Frontend can't connect
- Verify `VITE_API_URL` is correct
- Check CORS settings
- Ensure backend is running

### Agents not responding
- Check Groq API key
- Verify API credits available
- Check backend logs

---

**Ready to deploy?** Follow the [DEPLOYMENT.md](../DEPLOYMENT.md) guide!
