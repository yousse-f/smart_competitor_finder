# 🚀 Quick Start Deployment Guide

## In 5 minuti da zero a produzione

### Pre-requisiti
- [ ] Dominio registrato (es: tuosito.com)
- [ ] VPS Ubuntu 22.04 con IP pubblico
- [ ] Chiave API OpenAI

---

## 🎯 Deployment in 3 Step

### 1️⃣ Setup VPS (2 minuti)

```bash
# SSH nel VPS
ssh root@YOUR_VPS_IP

# Installa Docker
curl -fsSL https://get.docker.com | sh

# Installa Docker Compose
apt install docker-compose-plugin -y

# Crea directory
mkdir -p /var/www && cd /var/www
```

### 2️⃣ Clona e Configura (2 minuti)

```bash
# Clona repository
git clone YOUR_REPO_URL smart_competitor_finder
cd smart_competitor_finder

# Copia template environment
cp backend/.env.example backend/.env

# IMPORTANTE: Modifica con le TUE chiavi
nano backend/.env
```

**Modifica SOLO queste righe:**
```bash
OPENAI_API_KEY=sk-tua_chiave_openai_qui
ALLOWED_ORIGINS=https://tuodominio.com,http://tuodominio.com
```

**Salva e esci:** `CTRL+X`, poi `Y`, poi `ENTER`

```bash
# Configura dominio in Nginx
nano nginx/nginx.conf
```

**Cambia solo questa riga:**
```nginx
server_name tuodominio.com www.tuodominio.com;
```

**Salva e esci:** `CTRL+X`, poi `Y`, poi `ENTER`

### 3️⃣ Deploy! (1 minuto)

```bash
# Rendi eseguibile
chmod +x deploy.sh

# DEPLOY!
./deploy.sh production
```

**Aspetta 2-3 minuti** mentre Docker scarica e costruisce tutto...

---

## 🌐 Configura DNS

Mentre Docker lavora, configura il DNS del tuo dominio:

**Aggiungi questi 2 record:**
```
Type: A    | Name: @    | Value: YOUR_VPS_IP
Type: A    | Name: www  | Value: YOUR_VPS_IP
```

💡 Propagazione DNS: 5-30 minuti

---

## 🔒 Abilita HTTPS (Opzionale ma consigliato)

### Opzione A: Cloudflare (FACILE - 2 minuti)

1. Vai su [Cloudflare](https://cloudflare.com)
2. Aggiungi il tuo dominio
3. Cambia i nameserver del dominio
4. Abilita "Full SSL" nel pannello Cloudflare
5. ✅ **FATTO! SSL automatico**

### Opzione B: Let's Encrypt (5 minuti)

```bash
# Installa Certbot
apt install certbot -y

# Ferma Nginx temporaneamente
docker-compose stop nginx

# Genera certificato
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
# Decommenta le righe della sezione HTTPS (rimuovi i #)

# Riavvia
docker-compose up -d
```

**Auto-rinnovo:**
```bash
# Aggiungi al cron
echo "0 0 1 */2 * certbot renew --quiet && docker-compose restart nginx" | crontab -
```

---

## ✅ Verifica che funzioni

### 1. Controlla stato container

```bash
docker-compose ps
```

**Dovresti vedere 3 container UP:**
- ✅ backend
- ✅ frontend  
- ✅ nginx

### 2. Testa nel browser

**HTTP:**
```
http://tuodominio.com
```

**HTTPS (se configurato):**
```
https://tuodominio.com
```

### 3. Testa funzionalità

1. Vai alla pagina "Analyze"
2. Inserisci URL: `https://www.apple.com`
3. Clicca "Analizza Sito"
4. Dovresti vedere la summary generata ✅

---

## 🎛️ Comandi Utili

### Visualizza logs

```bash
# Tutti i servizi
docker-compose logs -f

# Solo errori backend
docker-compose logs -f backend | grep ERROR
```

### Restart

```bash
# Restart tutto
docker-compose restart

# Restart solo backend
docker-compose restart backend
```

### Aggiornare codice

```bash
cd /var/www/smart_competitor_finder
git pull
docker-compose up -d --build
```

### Stop tutto

```bash
docker-compose down
```

---

## 🐛 Problemi Comuni

### "Container non si avvia"

```bash
# Controlla logs
docker-compose logs backend

# Verifica .env
cat backend/.env | grep OPENAI_API_KEY
```

### "Sito non raggiungibile"

```bash
# Verifica DNS propagato
nslookup tuodominio.com

# Verifica container up
docker-compose ps

# Verifica porte aperte
netstat -tulpn | grep -E '80|443'
```

### "Errore OpenAI"

```bash
# Verifica chiave API
docker-compose exec backend bash
echo $OPENAI_API_KEY

# Se vuota, modifica .env e restart
nano backend/.env
docker-compose restart backend
```

### "Porta già in uso"

```bash
# Trova processo
lsof -i :80
lsof -i :443

# Killalo
kill -9 PID_DEL_PROCESSO
```

---

## 📊 Monitoring (Opzionale)

### Setup Uptime Robot (Gratis)

1. Vai su [UptimeRobot.com](https://uptimerobot.com)
2. Crea account gratuito
3. Aggiungi monitor HTTP(S): `https://tuodominio.com`
4. Ricevi notifiche via email se il sito va down

### Logs persistenti

```bash
# Salva logs in file
docker-compose logs --no-color > logs.txt

# Logs ultimi 7 giorni
docker-compose logs --since 7d > logs-week.txt
```

---

## 🎯 Checklist Finale

- [ ] VPS configurato con Docker
- [ ] Repository clonato
- [ ] `.env` configurato con OPENAI_API_KEY
- [ ] DNS puntato al VPS
- [ ] `./deploy.sh production` eseguito con successo
- [ ] Container up: `docker-compose ps`
- [ ] Sito raggiungibile nel browser
- [ ] HTTPS configurato (Cloudflare o Let's Encrypt)
- [ ] Test funzionalità: analisi URL funziona
- [ ] Monitoring configurato (Uptime Robot)

---

## 🚀 Sei Live!

Il tuo Smart Competitor Finder è ora in produzione! 🎉

**URL Backend API:** https://tuodominio.com/api/docs
**URL Frontend:** https://tuodominio.com

---

## 📞 Supporto

Problemi? Controlla la [documentazione completa](DOCKER_DEPLOYMENT.md)

**Comandi di emergenza:**

```bash
# Logs completi
docker-compose logs -f

# Restart totale
docker-compose restart

# Rebuild completo
docker-compose down
docker-compose up -d --build

# Verifica salute
curl http://localhost:8000/health
```

Buon lavoro! 💪
