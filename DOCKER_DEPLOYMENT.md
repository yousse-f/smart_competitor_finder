# 🐳 Docker Deployment Guide - Smart Competitor Finder

## 📋 Indice

1. [Requisiti](#requisiti)
2. [Setup Iniziale](#setup-iniziale)
3. [Configurazione](#configurazione)
4. [Deployment Locale](#deployment-locale)
5. [Deployment su VPS](#deployment-su-vps)
6. [SSL/HTTPS](#sslhttps)
7. [Manutenzione](#manutenzione)
8. [Troubleshooting](#troubleshooting)

---

## 🛠️ Requisiti

### Hardware Minimo (VPS)
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 40GB SSD
- **Network**: 100 Mbps

### Software
- Docker 20.10+
- Docker Compose 2.0+
- Git
- (Opzionale) Nginx sul host per SSL

---

## 🚀 Setup Iniziale

### 1. Clona il repository

```bash
git clone https://github.com/tuoaccount/smart_competitor_finder.git
cd smart_competitor_finder
```

### 2. Crea file .env

```bash
# Backend
cp backend/.env.example backend/.env
nano backend/.env  # Configura le tue chiavi
```

**Variabili OBBLIGATORIE:**
- `OPENAI_API_KEY`: La tua chiave API OpenAI

### 3. Rendi eseguibile lo script di deploy

```bash
chmod +x deploy.sh
```

---

## ⚙️ Configurazione

### Backend (.env)

```bash
# OpenAI (OBBLIGATORIO)
OPENAI_API_KEY=sk-...

# ScraperAPI (Opzionale)
SCRAPERAPI_KEY=...

# Security
SECRET_KEY=genera_una_chiave_casuale_molto_lunga

# CORS (aggiungi il tuo dominio)
ALLOWED_ORIGINS=http://localhost:3000,https://tuodominio.com
```

### Nginx

Modifica `nginx/nginx.conf`:

```nginx
# Cambia yourdomain.com con il tuo dominio reale
server_name yourdomain.com www.yourdomain.com;
```

---

## 💻 Deployment Locale (Test)

### 1. Build e avvia i container

```bash
./deploy.sh development
```

### 2. Verifica lo stato

```bash
docker-compose ps
```

### 3. Accedi all'applicazione

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 4. Visualizza i logs

```bash
# Tutti i servizi
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo frontend
docker-compose logs -f frontend
```

---

## 🌐 Deployment su VPS

### Step 1: Prepara il VPS

```bash
# Connettiti al VPS
ssh root@tuoserver

# Aggiorna il sistema
apt update && apt upgrade -y

# Installa Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Installa Docker Compose
apt install docker-compose-plugin -y

# Verifica installazione
docker --version
docker compose version
```

### Step 2: Clona e configura

```bash
# Crea directory
mkdir -p /var/www
cd /var/www

# Clona repository
git clone https://github.com/tuoaccount/smart_competitor_finder.git
cd smart_competitor_finder

# Configura environment
cp backend/.env.example backend/.env
nano backend/.env  # Inserisci le tue chiavi

# Configura Nginx
nano nginx/nginx.conf  # Cambia yourdomain.com

# Rendi eseguibile script deploy
chmod +x deploy.sh
```

### Step 3: Deploy

```bash
./deploy.sh production
```

### Step 4: Configura DNS

Punta il tuo dominio al VPS:

```
A Record: @ → IP_DEL_TUO_VPS
A Record: www → IP_DEL_TUO_VPS
```

---

## 🔒 SSL/HTTPS

### Opzione 1: Certbot (Raccomandato)

```bash
# Installa Certbot
apt install certbot python3-certbot-nginx -y

# Ferma temporaneamente Nginx del container
docker-compose stop nginx

# Genera certificato
certbot certonly --standalone -d tuodominio.com -d www.tuodominio.com

# Copia certificati nella cartella nginx
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/tuodominio.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/tuodominio.com/privkey.pem nginx/ssl/

# Decomenta la sezione HTTPS in nginx.conf
nano nginx/nginx.conf

# Riavvia tutto
docker-compose up -d
```

### Opzione 2: Cloudflare (Semplice)

1. Aggiungi il dominio a Cloudflare
2. Cambia i nameserver
3. Abilita "Full SSL" in Cloudflare
4. Nessun certificato necessario sul server!

### Auto-rinnovo certificati

```bash
# Aggiungi cron job
crontab -e

# Aggiungi questa riga (rinnova ogni 2 mesi)
0 0 1 */2 * certbot renew --quiet && docker-compose restart nginx
```

---

## 🔧 Manutenzione

### Aggiornare l'applicazione

```bash
cd /var/www/smart_competitor_finder

# Backup prima di aggiornare
./deploy.sh production  # Crea backup automatico

# Pull nuove modifiche
git pull origin main

# Rebuild e restart
docker-compose down
docker-compose up -d --build
```

### Visualizzare logs

```bash
# Logs in tempo reale
docker-compose logs -f

# Ultimi 100 logs
docker-compose logs --tail=100

# Logs di un servizio specifico
docker-compose logs -f backend
```

### Restart servizi

```bash
# Restart tutti
docker-compose restart

# Restart singolo servizio
docker-compose restart backend
docker-compose restart frontend
docker-compose restart nginx
```

### Backup manuale

```bash
# Backup reports
tar -czf backup-$(date +%Y%m%d).tar.gz backend/reports/

# Backup .env
cp backend/.env backend/.env.backup
```

### Pulizia spazio disco

```bash
# Rimuovi container fermi
docker container prune -f

# Rimuovi immagini non usate
docker image prune -a -f

# Rimuovi volumi non usati
docker volume prune -f

# Pulizia completa
docker system prune -a -f
```

---

## 🐛 Troubleshooting

### Container non si avvia

```bash
# Verifica logs
docker-compose logs backend

# Verifica risorse
docker stats

# Verifica porte
netstat -tulpn | grep -E '3000|8000|80|443'
```

### Errore "port already in use"

```bash
# Trova processo che usa la porta
lsof -i :8000
lsof -i :3000

# Killalo
kill -9 PID
```

### Backend non raggiungibile

```bash
# Verifica che sia up
docker-compose ps

# Entra nel container
docker-compose exec backend bash

# Testa internamente
curl http://localhost:8000/health
```

### Frontend timeout

```bash
# Verifica variabili ambiente
docker-compose exec frontend env | grep NEXT_PUBLIC

# Rebuild senza cache
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Playwright non funziona

```bash
# Entra nel container backend
docker-compose exec backend bash

# Reinstalla browsers
playwright install chromium
playwright install-deps
```

### Out of Memory

```bash
# Aumenta RAM in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G  # Aumenta questo

# Restart
docker-compose up -d
```

### SSL non funziona

```bash
# Verifica certificati
ls -la nginx/ssl/

# Verifica configurazione nginx
docker-compose exec nginx nginx -t

# Ricarica nginx
docker-compose restart nginx
```

---

## 📊 Monitoring

### Health checks

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Nginx
curl http://localhost/health
```

### Statistiche container

```bash
# CPU, RAM, Network
docker stats

# Spazio disco
docker system df
```

### Performance

```bash
# Response time backend
time curl http://localhost:8000/api/analyze-site

# Logs di accesso nginx
docker-compose exec nginx tail -f /var/log/nginx/access.log
```

---

## 🎯 Quick Commands

```bash
# Deploy
./deploy.sh production

# Stop tutto
docker-compose down

# Restart tutto
docker-compose restart

# Logs
docker-compose logs -f

# Shell backend
docker-compose exec backend bash

# Shell frontend
docker-compose exec frontend sh

# Rebuild tutto
docker-compose up -d --build

# Pulizia
docker system prune -a -f
```

---

## 📞 Supporto

Per problemi o domande:

1. Controlla i logs: `docker-compose logs -f`
2. Verifica la configurazione: `docker-compose config`
3. Consulta questa guida
4. Crea un issue su GitHub

---

## 🚀 Prossimi Passi

Dopo il deployment:

1. ✅ Configura monitoraggio (Uptime Robot, Pingdom)
2. ✅ Setup backup automatici
3. ✅ Configura firewall (UFW)
4. ✅ Abilita rate limiting
5. ✅ Configura analytics

Buon deployment! 🎉
