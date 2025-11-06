# Smart Competitor Finder - Frontend Deployment (Vercel)

## 🚀 Vercel Deployment Guide

### Prerequisites
1. Account Vercel (gratuito)
2. Backend già deployato su Railway (✅ fatto!)
3. Repository GitHub aggiornato

---

## 📋 Step-by-Step Deployment

### 1. Importa Progetto su Vercel

**Vai su**: https://vercel.com/new

**Opzioni**:
- **Repository**: `yousse-f/smart_competitor_finder`
- **Framework Preset**: `Next.js` (auto-detected)
- **Root Directory**: `frontend` ← **IMPORTANTE!**
- **Build Command**: `npm run build` (auto)
- **Output Directory**: `.next` (auto)
- **Install Command**: `npm install` (auto)

---

### 2. Environment Variables (CRITICAL!)

Nel dashboard Vercel, vai su **Settings → Environment Variables** e aggiungi:

```bash
# Backend Railway URL (REQUIRED)
NEXT_PUBLIC_API_URL=https://backend-production-cfae.up.railway.app

# Node.js Version (OPTIONAL - recommended)
NODE_VERSION=20.x
```

**⚠️ ATTENZIONE**: 
- `NEXT_PUBLIC_API_URL` **NON** deve avere trailing slash (`/`)
- Deve puntare al tuo backend Railway già deployato
- Questa variabile è **pubblica** (viene bundled nel frontend)

---

### 3. Deploy

Clicca **Deploy** e aspetta ~2-3 minuti.

**Vercel farà**:
1. Clone del repo
2. `npm install` delle dipendenze
3. `npm run build` (Next.js build)
4. Deploy su CDN globale

---

### 4. Verifica Deployment

**URL Vercel**: `https://your-project.vercel.app`

**Test checklist**:
1. ✅ Homepage carica correttamente
2. ✅ Console browser: nessun errore CORS
3. ✅ Test `/analyze`: Inserisci URL e verifica API call
4. ✅ Backend status indicator (dovrebbe essere verde)

**Console browser expected**:
```
🚀 API Request: POST /api/analyze-site
✅ API Response: 200 /api/analyze-site
```

---

## 🔧 Configuration Files

### `next.config.ts`
```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  reactStrictMode: true,
  swcMinify: true,
};

export default nextConfig;
```

### `package.json` scripts
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint"
  }
}
```

---

## 🐛 Troubleshooting

### Problema: Build Fails with "Module not found"
**Soluzione**: Verifica che `package.json` abbia tutte le dipendenze
```bash
cd frontend
npm install
npm run build  # Test locale
```

### Problema: API calls fail con CORS error
**Causa**: Backend Railway non ha configurato CORS per frontend Vercel

**Fix backend** (`backend/main.py`):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-vercel-app.vercel.app",  # ← Aggiungi questo
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Poi redeploy backend su Railway.

### Problema: Environment variable not working
**Sintomi**: 
- Console mostra `http://localhost:8000` invece del Railway URL
- API calls fail con "Network Error"

**Fix**:
1. Vercel Dashboard → Settings → Environment Variables
2. Aggiungi `NEXT_PUBLIC_API_URL=https://backend-production-cfae.up.railway.app`
3. Redeploy (Vercel → Deployments → tre puntini → Redeploy)

### Problema: 404 on refresh
**Causa**: Vercel routing issue (dovrebbe essere risolto automaticamente con Next.js App Router)

**Verifica**: `next.config.ts` non ha `trailingSlash: true`

---

## 📊 Performance Optimization

Vercel include automaticamente:
- ✅ CDN globale (Edge Network)
- ✅ Automatic HTTPS
- ✅ Image Optimization (Next.js Image component)
- ✅ Incremental Static Regeneration (ISR)
- ✅ Server-Side Rendering (SSR) on-demand

**Monitoring**: Vercel Analytics (free tier: 100k pageviews/month)

---

## 🔄 CI/CD (Auto-Deploy)

**Vercel auto-deploya su**:
- Push a `main` branch → Production deploy
- Pull requests → Preview deploy (URL temporaneo)

**Disable auto-deploy**: 
Vercel Dashboard → Settings → Git → Auto-deploy (toggle off)

---

## 💰 Pricing

**Vercel Hobby (Free)**:
- ✅ 100 GB bandwidth/month
- ✅ 100 build hours/month
- ✅ Serverless Functions (100k invocations/month)
- ✅ Edge Functions (1M invocations/month)
- ✅ 1 team member
- ❌ No custom domain SSL (usi `*.vercel.app`)

**Pro ($20/month)** - Necessario se:
- Custom domain con SSL
- Team collaboration
- Advanced analytics

---

## 🎯 Post-Deployment Checklist

- [ ] URL Vercel funziona (homepage carica)
- [ ] Backend Railway raggiungibile da Vercel
- [ ] Test `/analyze` con URL reale
- [ ] Test `/upload` con Excel file
- [ ] Test download report
- [ ] Console browser: nessun errore
- [ ] Mobile responsive (test su smartphone)
- [ ] Backend CORS configurato con Vercel URL

---

## 🔗 URLs

| Servizio | URL | Status |
|----------|-----|--------|
| **Backend Railway** | `https://backend-production-cfae.up.railway.app` | ✅ Running |
| **Frontend Vercel** | `https://your-app.vercel.app` | 🔄 Da deployare |
| **GitHub Repo** | `https://github.com/yousse-f/smart_competitor_finder` | ✅ Aggiornato |

---

## 📚 Resources

- [Vercel Docs](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Environment Variables](https://vercel.com/docs/environment-variables)
