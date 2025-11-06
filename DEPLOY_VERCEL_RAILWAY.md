# 🚀 Deploy Smart Competitor Finder su Vercel + Railway

## 📊 Architettura Finale

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  smart_competitor.youssef-ben.com (IONOS DNS)              │
│                        │                                    │
│                        ▼                                    │
│            ┌───────────────────────┐                        │
│            │   Vercel CDN + SSL    │                        │
│            │   (Frontend Next.js)  │                        │
│            └───────────┬───────────┘                        │
│                        │ HTTPS                              │
│                        ▼                                    │
│            ┌───────────────────────┐                        │
│            │   Railway + SSL       │                        │
│            │   (Backend FastAPI)   │                        │
│            │   + Playwright        │                        │
│            └───────────────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Prerequisiti

Prima di iniziare, assicurati di avere:

- ✅ Repository GitHub con il progetto
- ✅ Account [Vercel](https://vercel.com) (gratuito)
- ✅ Account [Railway](https://railway.app) (€5/mese)
- ✅ Dominio su IONOS: `youssef-ben.com`
- ✅ Chiave API OpenAI valida

---

## 📦 Parte 1: Preparazione Repository GitHub

### 1️⃣ Crea Repository su GitHub

```bash
cd /Users/youbenmo/projects/smart_competiot_finder

# Inizializza git (se non l'hai già fatto)
git init
git add .
git commit -m "Initial commit - Smart Competitor Finder"

# Crea repository su GitHub.com e poi:
git remote add origin https://github.com/TUOUSERNAME/smart_competitor_finder.git
git branch -M main
git push -u origin main
```

### 2️⃣ Verifica Struttura Repository

Assicurati che il repository abbia questa struttura:

```
smart_competitor_finder/
├── backend/
│   ├── Dockerfile          ✅
│   ├── requirements.txt    ✅
│   ├── main.py            ✅
│   ├── .env.example       ✅
│   └── ...
├── frontend/
│   ├── package.json       ✅
│   ├── next.config.ts     ✅
│   ├── Dockerfile         ✅
│   └── ...
├── docker-compose.yml     ✅
└── README.md             ✅
```

---

## 🐍 Parte 2: Deploy Backend su Railway

### 1️⃣ Crea Progetto Railway

1. Vai su [railway.app/new](https://railway.app/new)
2. Clicca **"Deploy from GitHub repo"**
3. Autorizza Railway ad accedere al tuo GitHub
4. Seleziona il repository `smart_competitor_finder`

### 2️⃣ Configura Root Directory

Railway di default cerca nella root, ma il nostro backend è in `backend/`:

1. Vai su **Settings** → **General**
2. In **Root Directory** inserisci: `backend`
3. Clicca **Save**

Railway rileverà automaticamente il `Dockerfile` nella cartella `backend/`

### 3️⃣ Configura Variabili Ambiente

Vai su **Variables** e aggiungi:

| Nome | Valore | Descrizione |
|------|--------|-------------|
| `OPENAI_API_KEY` | `sk-proj-...` | La tua chiave OpenAI (OBBLIGATORIO) |
| `SECRET_KEY` | `genera_stringa_random_32_caratteri` | Per sicurezza sessioni |
| `ALLOWED_ORIGINS` | `https://smart-competitor.vercel.app,https://smart_competitor.youssef-ben.com` | CORS (aggiorna dopo deploy Vercel) |
| `APP_ENV` | `production` | Ambiente |
| `DEBUG` | `False` | No debug in produzione |
| `LOG_LEVEL` | `INFO` | Livello logging |
| `MAX_REQUESTS_PER_MINUTE` | `60` | Rate limiting |

**Per generare SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4️⃣ Deploy e Verifica

1. Railway inizierà il deploy automaticamente
2. Aspetta 3-5 minuti per il build (Playwright è pesante)
3. Quando è pronto, vedrai **"Active"** con un dominio tipo:
   ```
   https://smart-competitor-production.up.railway.app
   ```

4. **Testa il backend:**
   ```bash
   curl https://smart-competitor-production.up.railway.app/health
   ```
   
   Dovresti vedere:
   ```json
   {"status":"healthy"}
   ```

5. **Testa API Docs:**
   Apri nel browser:
   ```
   https://smart-competitor-production.up.railway.app/docs
   ```

### 5️⃣ Configura Dominio Custom (Opzionale)

Se vuoi usare `api.smart_competitor.youssef-ben.com`:

1. In Railway → **Settings** → **Networking**
2. Clicca **Add Custom Domain**
3. Inserisci: `api.smart_competitor.youssef-ben.com`
4. Railway ti mostrerà un **CNAME record**
5. Aggiungi in IONOS:
   ```
   Tipo: CNAME
   Nome: api.smart_competitor
   Valore: <valore-fornito-da-railway>
   ```

---

## ⚛️ Parte 3: Deploy Frontend su Vercel

### 1️⃣ Importa Progetto da GitHub

1. Vai su [vercel.com/new](https://vercel.com/new)
2. Clicca **"Import Git Repository"**
3. Seleziona `smart_competitor_finder`
4. Clicca **Import**

### 2️⃣ Configura Root Directory

Vercel cerca nella root, ma il nostro frontend è in `frontend/`:

1. In **Root Directory** inserisci: `frontend`
2. Framework Preset: **Next.js** (rilevato automaticamente)

### 3️⃣ Configura Variabili Ambiente

Clicca su **Environment Variables** e aggiungi:

| Nome | Valore |
|------|--------|
| `NEXT_PUBLIC_API_URL` | URL del backend Railway (es: `https://smart-competitor-production.up.railway.app`) |

**IMPORTANTE:** Usa l'URL esatto che Railway ti ha fornito!

### 4️⃣ Deploy

1. Clicca **Deploy**
2. Aspetta 2-3 minuti per il build
3. Vercel ti fornirà un URL tipo:
   ```
   https://smart-competitor-finder.vercel.app
   ```

4. **Testa il frontend:**
   Apri l'URL nel browser e verifica che:
   - ✅ La homepage carica
   - ✅ Puoi navigare tra le pagine
   - ✅ Le chiamate API funzionano (test con "Analyze")

### 5️⃣ Aggiorna CORS sul Backend

Ora che hai l'URL Vercel, devi aggiornare il CORS:

1. Torna su **Railway** → **Variables**
2. Modifica `ALLOWED_ORIGINS`:
   ```
   https://smart-competitor-finder.vercel.app,https://smart_competitor.youssef-ben.com
   ```
3. Railway farà restart automaticamente

---

## 🌐 Parte 4: Collegamento Dominio IONOS

### 1️⃣ Configura Dominio su Vercel

1. In Vercel → **Settings** → **Domains**
2. Clicca **Add Domain**
3. Inserisci: `smart_competitor.youssef-ben.com`
4. Clicca **Add**

### 2️⃣ Configura DNS su IONOS

Vercel ti mostrerà il record DNS da aggiungere. Di solito è un **CNAME**:

1. Vai su [IONOS DNS Manager](https://my.ionos.com)
2. Seleziona il dominio `youssef-ben.com`
3. **Elimina** il record A esistente per `smart_competitor`
4. **Aggiungi** nuovo record:
   ```
   Tipo: CNAME
   Nome: smart_competitor
   Valore: cname.vercel-dns.com
   TTL: Auto
   ```

### 3️⃣ Verifica e SSL

1. Aspetta 5-30 minuti per propagazione DNS
2. Vercel verificherà automaticamente il dominio
3. SSL verrà attivato automaticamente (HTTPS)
4. Vedrai ✅ accanto al dominio in Vercel

### 4️⃣ Test Finale

Apri nel browser:
```
https://smart_competitor.youssef-ben.com
```

✅ Dovresti vedere il tuo Smart Competitor Finder con HTTPS!

---

## 🔧 Parte 5: Configurazioni Finali

### 1️⃣ Aggiorna CORS Definitivo

Sul backend Railway, aggiorna `ALLOWED_ORIGINS` con ENTRAMBI gli URL:

```
https://smart-competitor-finder.vercel.app,https://smart_competitor.youssef-ben.com
```

### 2️⃣ Testa Workflow Completo

1. **Vai su:** https://smart_competitor.youssef-ben.com
2. **Step 1:** Analizza un sito (es: https://www.apple.com)
3. **Step 2:** Verifica che la summary AI venga generata
4. **Step 3:** Upload Excel con competitor
5. **Step 4:** Download report

✅ Se tutto funziona → **DEPLOYMENT COMPLETATO!**

---

## 🔄 Parte 6: Deploy Automatico (CI/CD)

### Configurazione Automatica

Ora ogni volta che fai `git push`, entrambi i servizi si aggiorneranno automaticamente:

```bash
# Fai modifiche al codice
git add .
git commit -m "feat: nuova funzionalità"
git push origin main

# 🎉 Vercel e Railway deployano automaticamente!
```

**Railway:**
- Rileva push su `main`
- Build Dockerfile
- Deploy automatico
- Zero downtime

**Vercel:**
- Rileva push su `main`
- Build Next.js
- Deploy automatico
- Deploy preview per ogni branch/PR

---

## 🐛 Troubleshooting

### Backend Railway non risponde

```bash
# Controlla logs
# In Railway dashboard → Deployments → View Logs

# Verifica variabili ambiente
# Variables → check OPENAI_API_KEY presente

# Test health check
curl https://tuobackend.railway.app/health
```

### Frontend Vercel errore CORS

```bash
# Verifica ALLOWED_ORIGINS su Railway
# Deve includere l'URL Vercel esatto

# Verifica NEXT_PUBLIC_API_URL su Vercel
# Deve puntare al backend Railway esatto
```

### Dominio non funziona

```bash
# Verifica DNS propagato
nslookup smart_competitor.youssef-ben.com

# Dovrebbe mostrare CNAME verso Vercel
# Se vedi ancora 217.160.0.149, DNS non ancora propagato

# Attendi 30 minuti e riprova
```

### Playwright errors sul backend

```bash
# Railway dovrebbe installare automaticamente Chromium
# Se ci sono errori, verifica nel Dockerfile:

# Assicurati che ci siano questi comandi:
RUN playwright install chromium
RUN playwright install-deps
```

### Timeout errors

```bash
# Se le analisi vanno in timeout:

# 1. Aumenta timeout frontend (già 90s in api.ts)
# 2. Railway ha timeout 30min di default (dovrebbe bastare)
# 3. Verifica OPENAI_API_KEY valida e con credito
```

---

## 💰 Costi Mensili

| Servizio | Piano | Costo |
|----------|-------|-------|
| **Vercel** | Hobby (Free) | **€0/mese** |
| **Railway** | Developer | **~€5/mese** |
| **IONOS DNS** | Incluso dominio | **€0/mese** |
| **OpenAI API** | Pay-as-you-go | **Variabile** |
| **TOTALE** | | **~€5/mese** |

### Limiti Piano Gratuito Vercel:
- ✅ 100GB bandwidth/mese
- ✅ Deploy illimitati
- ✅ SSL automatico
- ✅ CDN globale
- ✅ Preview automatici

### Railway Developer:
- ✅ $5 di credito/mese incluso
- ✅ ~500 ore/mese di runtime
- ✅ Deploy illimitati
- ✅ SSL automatico
- ✅ Logs e monitoring

---

## 📊 Monitoring e Logs

### Logs Backend (Railway)

```bash
# Dashboard Railway → Deployments → View Logs
# Oppure installa CLI:
npm i -g @railway/cli
railway login
railway logs
```

### Logs Frontend (Vercel)

```bash
# Dashboard Vercel → Deployments → Logs
# Oppure installa CLI:
npm i -g vercel
vercel logs
```

### Monitoring Uptime

Setup gratuito con **Uptime Robot**:

1. Vai su [uptimerobot.com](https://uptimerobot.com)
2. Aggiungi monitor:
   - **Frontend:** https://smart_competitor.youssef-ben.com
   - **Backend:** https://tuobackend.railway.app/health
3. Ricevi notifiche via email se down

---

## 🎉 Checklist Finale

- [ ] Repository GitHub creato e pushato
- [ ] Backend Railway deployato e funzionante
- [ ] Frontend Vercel deployato e funzionante
- [ ] Variabili ambiente configurate (OPENAI_API_KEY, etc)
- [ ] CORS configurato correttamente
- [ ] Dominio custom collegato su Vercel
- [ ] DNS IONOS configurato (CNAME)
- [ ] SSL attivo (HTTPS) su entrambi
- [ ] Workflow completo testato (analyze → upload → report)
- [ ] Deploy automatico funzionante (git push → auto deploy)
- [ ] Monitoring configurato (Uptime Robot)

---

## 🚀 Sei Live!

Il tuo **Smart Competitor Finder** è ora in produzione! 🎉

**URL Pubblici:**
- 🌐 Frontend: https://smart_competitor.youssef-ben.com
- 🔧 Backend API: https://tuobackend.railway.app
- 📚 API Docs: https://tuobackend.railway.app/docs

**Dashboard:**
- ⚡ Vercel: https://vercel.com/dashboard
- 🚂 Railway: https://railway.app/dashboard

**Comandi Utili:**
```bash
# Deploy automatico
git push origin main

# Verifica status
curl https://tuobackend.railway.app/health
curl https://smart_competitor.youssef-ben.com

# Logs
railway logs  # Backend
vercel logs   # Frontend
```

Buon lavoro! 💪
