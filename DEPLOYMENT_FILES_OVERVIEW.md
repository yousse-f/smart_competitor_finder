# 📦 Docker Deployment Package - Files Overview

Questa cartella contiene tutti i file necessari per deployare **Smart Competitor Finder** in produzione con Docker.

## 📁 File Creati

### 🐳 Docker & Orchestrazione

| File | Descrizione | Uso |
|------|-------------|-----|
| `backend/Dockerfile` | Container Python 3.11 con Playwright | Build automatico backend |
| `frontend/Dockerfile` | Container Node 20 Alpine con Next.js standalone | Build automatico frontend |
| `docker-compose.yml` | Orchestrazione 3 servizi (backend, frontend, nginx) | `docker-compose up -d` |
| `backend/.dockerignore` | Esclusione file non necessari dal build context | Ottimizzazione build |
| `frontend/.dockerignore` | Esclusione file non necessari dal build context | Ottimizzazione build |

### 🌐 Nginx & Reverse Proxy

| File | Descrizione | Uso |
|------|-------------|-----|
| `nginx/nginx.conf` | Configurazione reverse proxy con SSL | Routing API + Frontend |

### 🚀 Deployment Scripts

| File | Descrizione | Uso |
|------|-------------|-----|
| `deploy.sh` | **Script principale deployment** | `./deploy.sh production` |
| `security-setup.sh` | Setup firewall, Fail2Ban, auto-updates | `./security-setup.sh` |
| `backup.sh` | Backup automatico config + reports + SSL | `./backup.sh` |
| `restore.sh` | Restore da backup archive | `./restore.sh backup.tar.gz` |

### 📚 Documentazione

| File | Descrizione | Target Audience |
|------|-------------|-----------------|
| `README.md` | **Overview principale progetto** | Tutti |
| `DEPLOYMENT_QUICK_START.md` | Deploy rapido in 5 minuti | DevOps / Beginner |
| `DOCKER_DEPLOYMENT.md` | Guida completa deployment Docker | DevOps / Advanced |
| `AUTOMATION_MONITORING.md` | Setup backup/monitoring/cron jobs | SysAdmin |

### ⚙️ Configuration

| File | Descrizione | Uso |
|------|-------------|-----|
| `backend/.env.example` | Template variabili ambiente backend | Copia in `.env` |
| `frontend/next.config.ts` | Config Next.js con standalone output | Build Docker |

---

## 🎯 Quick Start Workflow

### 1️⃣ Setup Iniziale (Locale)

```bash
# Clone repository
git clone https://github.com/tuoaccount/smart_competitor_finder.git
cd smart_competitor_finder

# Configura environment
cp backend/.env.example backend/.env
nano backend/.env  # OPENAI_API_KEY

# Rendi eseguibili script
chmod +x deploy.sh backup.sh restore.sh security-setup.sh
```

### 2️⃣ Test Locale

```bash
# Deploy ambiente development
./deploy.sh development

# Verifica
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:3000

# Stop
docker-compose down
```

### 3️⃣ Deploy Produzione su VPS

```bash
# SSH nel VPS
ssh root@YOUR_VPS_IP

# Setup Docker
curl -fsSL https://get.docker.com | sh
apt install docker-compose-plugin -y

# Clone e configura
mkdir -p /var/www && cd /var/www
git clone YOUR_REPO smart_competitor_finder
cd smart_competitor_finder

# Environment
cp backend/.env.example backend/.env
nano backend/.env  # Configura OPENAI_API_KEY

# Configura dominio
nano nginx/nginx.conf  # Cambia yourdomain.com

# Deploy
chmod +x deploy.sh
./deploy.sh production

# Configura DNS
# A Record: @ → VPS_IP
# A Record: www → VPS_IP
```

### 4️⃣ Security Hardening

```bash
# Nel VPS
./security-setup.sh

# Setup SSL
certbot certonly --standalone -d tuodominio.com
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/tuodominio.com/*.pem nginx/ssl/
docker-compose restart nginx
```

### 5️⃣ Backup & Monitoring

```bash
# Setup backup automatico
crontab -e
# Aggiungi: 0 3 * * * cd /var/www/smart_competitor_finder && ./backup.sh

# Setup monitoring
crontab -e
# Aggiungi: */5 * * * * /usr/local/bin/health-check.sh

# Setup Uptime Robot
# Vai su uptimerobot.com
# Monitor: https://tuodominio.com/health
```

---

## 📊 Struttura Deployment

```
VPS Production
├── /var/www/smart_competitor_finder/    ← Project root
│   ├── backend/
│   │   ├── Dockerfile                   ← Backend container
│   │   ├── .env                         ← OPENAI_API_KEY qui!
│   │   └── reports/                     ← Report generati
│   ├── frontend/
│   │   └── Dockerfile                   ← Frontend container
│   ├── nginx/
│   │   ├── nginx.conf                   ← Reverse proxy config
│   │   └── ssl/                         ← Certificati SSL
│   ├── docker-compose.yml               ← Orchestrazione
│   ├── deploy.sh                        ← Main deployment script
│   ├── backup.sh                        ← Backup script
│   └── restore.sh                       ← Restore script
│
├── /var/backups/smart_competitor_finder/ ← Backup storage
│   ├── backup_20240115_030000.tar.gz
│   ├── backup_20240116_030000.tar.gz
│   └── ...
│
└── /usr/local/bin/                      ← System scripts
    ├── health-check.sh                  ← Health monitoring
    ├── telegram-notify.sh               ← Notifiche Telegram
    └── backup-to-s3.sh                  ← Backup remoto
```

---

## 🔧 Script Details

### deploy.sh

**Funzioni:**
- ✅ Valida environment variables
- ✅ Crea directory necessarie
- ✅ Build Docker images
- ✅ Setup logging
- ✅ Health checks automatici
- ✅ Rollback su errore

**Uso:**
```bash
./deploy.sh [development|staging|production]
```

### backup.sh

**Backup Include:**
- ✅ `.env` file
- ✅ `docker-compose.yml`
- ✅ `nginx.conf`
- ✅ Generated reports
- ✅ SSL certificates
- ✅ Docker logs (7 giorni)

**Storage:**
- Location: `/var/backups/smart_competitor_finder/`
- Retention: Ultimi 7 backup
- Formato: `backup_YYYYMMDD_HHMMSS.tar.gz`

**Automazione:**
```bash
0 3 * * * cd /var/www/smart_competitor_finder && ./backup.sh
```

### restore.sh

**Funzioni:**
- ✅ Verifica integrità backup
- ✅ Pre-restore backup automatico
- ✅ Stop containers
- ✅ Restore files
- ✅ Restart containers
- ✅ Health check post-restore

**Uso:**
```bash
./restore.sh /var/backups/smart_competitor_finder/backup_20240115_030000.tar.gz
```

### security-setup.sh

**Configura:**
- ✅ UFW Firewall (22, 80, 443)
- ✅ Fail2Ban (SSH + Nginx)
- ✅ Unattended upgrades
- ✅ Docker log rotation
- ✅ SSH hardening (opzionale)

**Uso:**
```bash
./security-setup.sh
```

---

## 📈 Monitoring Setup

### Health Checks (ogni 5 minuti)

```bash
cat > /usr/local/bin/health-check.sh <<'EOF'
#!/bin/bash
PROJECT_DIR="/var/www/smart_competitor_finder"
cd $PROJECT_DIR

# Check containers
if ! docker-compose ps | grep -q "Up"; then
    docker-compose up -d
fi

# Check backend
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    docker-compose restart backend
fi

# Check frontend
if ! curl -f http://localhost:3000 > /dev/null 2>&1; then
    docker-compose restart frontend
fi
EOF

chmod +x /usr/local/bin/health-check.sh
```

**Cron:**
```bash
*/5 * * * * /usr/local/bin/health-check.sh
```

### Uptime Robot (Gratis)

1. **Sign up:** [uptimerobot.com](https://uptimerobot.com)
2. **Add monitor:**
   - Type: HTTP(S)
   - URL: `https://tuodominio.com/health`
   - Interval: 5 minutes
3. **Alerts:** Email, SMS, Telegram

---

## 🔒 SSL/HTTPS Setup

### Opzione 1: Cloudflare (Semplice)

1. Aggiungi dominio a Cloudflare
2. Cambia nameserver del dominio
3. Abilita "Full SSL" in Cloudflare dashboard
4. ✅ **Done! Zero config sul server**

### Opzione 2: Let's Encrypt (Tradizionale)

```bash
# Installa Certbot
apt install certbot -y

# Stop Nginx temporaneamente
docker-compose stop nginx

# Genera certificati
certbot certonly --standalone \
  -d tuodominio.com \
  -d www.tuodominio.com \
  --email tua@email.com \
  --agree-tos

# Copia certificati
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/tuodominio.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/tuodominio.com/privkey.pem nginx/ssl/

# Abilita HTTPS in nginx.conf
nano nginx/nginx.conf
# Decommenta sezione HTTPS (rimuovi #)

# Restart
docker-compose up -d

# Auto-rinnovo
echo "0 0 1 */2 * certbot renew --quiet && docker-compose restart nginx" | crontab -
```

---

## 🎯 Checklist Deployment

### Pre-Deployment

- [ ] VPS Ubuntu 22.04 (2 CPU, 4GB RAM, 40GB SSD)
- [ ] Dominio registrato
- [ ] Chiave OpenAI API
- [ ] Git repository accessibile

### Durante Deployment

- [ ] Docker + Docker Compose installati
- [ ] Repository clonato in `/var/www/`
- [ ] `.env` configurato con `OPENAI_API_KEY`
- [ ] `nginx.conf` con dominio corretto
- [ ] `./deploy.sh production` eseguito con successo
- [ ] DNS A record puntato al VPS IP

### Post-Deployment

- [ ] Containers up: `docker-compose ps`
- [ ] Backend healthy: `curl http://localhost:8000/health`
- [ ] Frontend responding: `curl http://localhost:3000`
- [ ] Dominio raggiungibile nel browser
- [ ] SSL/HTTPS configurato e funzionante
- [ ] Firewall + Fail2Ban attivi
- [ ] Backup automatico configurato (cron)
- [ ] Monitoring attivo (Uptime Robot)
- [ ] Test completo workflow: analisi + upload + report

---

## 🚨 Troubleshooting Quick Reference

| Problema | Soluzione |
|----------|-----------|
| Container non si avvia | `docker-compose logs -f backend` |
| Porta già in uso | `lsof -i :8000` → `kill -9 PID` |
| Out of memory | Aumenta RAM in docker-compose.yml |
| SSL non funziona | Verifica `nginx/ssl/` e nginx.conf |
| Frontend timeout | Timeout aumentato a 90s in api.ts |
| Playwright errors | `docker-compose exec backend bash` → `playwright install` |
| Backend non risponde | `docker-compose restart backend` |
| Disk space pieno | `docker system prune -a -f` |

**Logs:**
```bash
# Tutti i servizi
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Ultimi 100 logs
docker-compose logs --tail=100

# Salva logs in file
docker-compose logs --no-color > logs.txt
```

---

## 📞 Support Channels

1. **Documentation:** Leggi [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
2. **Logs:** `docker-compose logs -f`
3. **Health Check:** `curl http://localhost:8000/health`
4. **GitHub Issues:** Crea issue sul repository
5. **Email:** support@tuodominio.com

---

## ⭐ Next Steps

Dopo il deployment completo:

1. **Testing:**
   - Test workflow completo (analizza → upload → report)
   - Verifica performance sotto carico
   - Test failover e recovery

2. **Monitoring:**
   - Setup Uptime Robot
   - Configura Telegram notifications
   - Review logs periodicamente

3. **Maintenance:**
   - Backup settimanale manuale test
   - Update mensile Docker images
   - Review security logs

4. **Scaling:**
   - Considera load balancer se necessario
   - Setup replica database se alta disponibilità richiesta
   - CDN per static assets (Cloudflare)

---

## 🎉 Deployment Completed!

Tutte le infrastrutture sono pronte. Segui il **[DEPLOYMENT_QUICK_START.md](DEPLOYMENT_QUICK_START.md)** per il deploy passo-passo.

**Buon deployment! 🚀**
