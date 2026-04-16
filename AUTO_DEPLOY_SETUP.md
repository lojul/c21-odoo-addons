# Auto-Deploy Setup Guide

## ✅ What I Just Did

1. **Deployed your latest changes** (with merged image views) - Building now
2. **Created GitHub Actions workflow** - Will auto-deploy on every push to main

---

## 🔧 One-Time Setup (Required for Auto-Deploy)

To enable auto-deploy from GitHub, you need to add your Railway token to GitHub:

### Step 1: Get Railway Token

1. Go to https://railway.app/account/tokens
2. Click **"Create Token"**
3. Name it: **"GitHub Actions Deploy"**
4. Copy the token (starts with `railway_...`)

### Step 2: Add Token to GitHub

1. Go to https://github.com/lojul/c21-odoo-addons/settings/secrets/actions
2. Click **"New repository secret"**
3. Name: `RAILWAY_TOKEN`
4. Value: Paste the token you copied
5. Click **"Add secret"**

### Step 3: Test Auto-Deploy

Make a small change and push:
```bash
# Make any small change, like adding a comment
echo "# Test auto-deploy" >> README.md
git add README.md
git commit -m "Test auto-deploy"
git push origin main
```

Go to: https://github.com/lojul/c21-odoo-addons/actions

You should see the workflow running! ✅

---

## 📋 How It Works

**Before (Manual):**
```
git push → Nothing happens → You run `railway up` manually
```

**After (Automatic):**
```
git push → GitHub Actions → Automatically runs `railway up` → Deploys! 🎉
```

---

## 🚀 Current Deployment Status

**Right now**, I just manually deployed your latest changes (merged image views).

**In ~5 minutes:**
1. Railway build will complete
2. Go to Odoo → Apps → "Update Apps List"
3. Search "C21" → Click "Upgrade"
4. Check Images tab → You should see image upload fields!

---

## 🔮 Future Pushes

After you complete the setup above, **every** `git push` will automatically deploy to Railway!

No more manual `railway up` commands needed. ✨

---

## 🐛 Troubleshooting

**GitHub Actions fails with "RAILWAY_TOKEN not found"**
- You need to complete Step 2 above

**Deployment successful but changes not in Odoo**
- Remember to upgrade the module in Odoo after deployment
- Apps → Update Apps List → Search "C21" → Upgrade

**Want to disable auto-deploy?**
- Delete or rename `.github/workflows/auto-deploy.yml`

---

**Created:** April 16, 2026
**Status:** ⏳ Awaiting RAILWAY_TOKEN setup in GitHub
