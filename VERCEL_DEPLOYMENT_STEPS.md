# Vercel Deployment Configuration

## Current Status
✓ Repository: khattam/MirrorMind-AI connected
✓ Project Name: mirror-mind-ai

## Configuration Steps

### 1. Framework Preset
- Change from "Other" to **"Vite"**

### 2. Root Directory
- Click "Edit" button
- Set to: **`frontend`**

### 3. Build and Output Settings
Click "Build and Output Settings" to expand, then verify:
- **Build Command:** `npm run build` (should auto-populate)
- **Output Directory:** `dist` (should auto-populate)
- **Install Command:** `npm install` (should auto-populate)

### 4. Environment Variables
Click "Environment Variables" to expand, then add:
- **Key:** `VITE_API_URL`
- **Value:** `https://mirrormind-ai.onrender.com`
- **Environment:** All (Production, Preview, Development)

### 5. Deploy
Click the **"Deploy"** button at the bottom

## Expected Result
- Build time: ~2-3 minutes
- Your app will be live at: `https://mirror-mind-ai.vercel.app` (or similar)

## After Deployment
Test these URLs:
- Homepage: `https://your-app.vercel.app`
- Should connect to backend at: `https://mirrormind-ai.onrender.com`

## Troubleshooting
If build fails, check:
1. Root directory is set to `frontend`
2. Framework is set to `Vite`
3. Environment variable `VITE_API_URL` is set correctly
