# Railway Deployment Guide

This guide will help you deploy the E-Commerce Product Extraction Pipeline to Railway.

## ✅ Why Railway Works

Railway supports:
- ✅ Long-running processes (perfect for `main.py`)
- ✅ Docker containers (can install Chrome/Chromium)
- ✅ Environment variables
- ✅ Persistent processes (won't stop like Vercel)

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Push your code to GitHub
3. **Environment Variables**: You'll need:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - Google API credentials (already in code)

## 🚀 Deployment Steps

### Option 1: Using Docker (Recommended)

Railway will automatically detect and use the `Dockerfile`:

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Add Railway deployment configuration"
   git push origin main
   ```

2. **Deploy on Railway**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect the Dockerfile

3. **Set Environment Variables**:
   - Go to your project → Variables
   - Add:
     - `SUPABASE_URL` = `https://whfjofihihlhctizchmj.supabase.co`
     - `SUPABASE_KEY` = `your-anon-key`

4. **Deploy**:
   - Railway will build the Docker image (installs Chrome automatically)
   - Deploy and start `main.py`

### Option 2: Using Nixpacks

1. **Deploy on Railway**:
   - Same as Option 1, but Railway will use `nixpacks.toml` instead

2. **Build Configuration**:
   - The `nixpacks.toml` automatically installs Chromium
   - Installs all Python dependencies
   - Runs `main.py` on start

## 🔧 Railway Configuration

### Environment Variables Required

```
SUPABASE_URL=https://whfjofihihlhctizchmj.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

### Start Command

Railway will automatically use:
- `python main.py` (from Dockerfile CMD)

## ✅ What Railway Will Do

1. **Install Chrome/Chromium**: Via Dockerfile or nixpacks
2. **Install Dependencies**: All Python packages from `requirements.txt`
3. **Setup Selenium**: `webdriver-manager` automatically downloads ChromeDriver
4. **Run Pipelines**: Starts `main.py` which runs both pipelines continuously
5. **Auto-restart**: If the process crashes, Railway restarts it

## 🐛 Troubleshooting

### Selenium/Chrome Issues

If you see ChromeDriver errors:
- ✅ The Dockerfile installs Chrome automatically
- ✅ `webdriver-manager` handles ChromeDriver installation
- ✅ If issues persist, check Railway logs

### Check Logs

```bash
# In Railway dashboard:
# Go to your deployment → Logs tab
# You'll see real-time logs from main.py
```

### Common Issues

1. **Chrome not found**:
   - ✅ Dockerfile installs it - should work automatically
   - Check Railway build logs to confirm Chrome installation

2. **Out of memory**:
   - Upgrade Railway plan if needed
   - Selenium can be memory-intensive

3. **Process stopped**:
   - Railway auto-restarts crashed processes
   - Check logs for error messages

## 📊 Monitoring

Railway provides:
- **Real-time logs**: See what your pipelines are doing
- **Metrics**: CPU, memory usage
- **Deployments**: Track deployment history

## 🔄 Updating Deployment

1. **Push changes to GitHub**
2. **Railway auto-deploys** (if auto-deploy is enabled)
3. **Or manually deploy** from Railway dashboard

## 💰 Costs

Railway pricing:
- **Free tier**: $5 credit/month (good for testing)
- **Pro**: Pay-as-you-go for production

For continuous running:
- ~$5-10/month for small deployments
- Depends on resource usage

## ✅ Post-Deployment

After deployment:

1. **Verify pipelines are running**:
   - Check Railway logs
   - Should see: `[✓] Category Search Pipeline thread started`
   - Should see: `[✓] Product Extraction Pipeline thread started`

2. **Test with input data**:
   - Use `inputDataHandler.py` locally or create a Railway service for it
   - Add categories/products to database

3. **Monitor**:
   - Watch logs for successful operations
   - Check Supabase for new data

## 🎉 Success!

Once deployed, your pipelines will:
- ✅ Run continuously
- ✅ Discover e-commerce sites
- ✅ Extract products automatically
- ✅ Save to Supabase database

No manual intervention needed!

