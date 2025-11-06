# 🚀 Deployment su VPS - smart_competitor.youssef-ben.com

## ✅ Configurazione DNS (FATTO)

Record DNS già configurato:
```
Tipo: A
Nome Host: smart_competitor
Valore: 217.160.0.149
```

**URL finale:** `http://smart_competitor.youssef-ben.com` (HTTP temporaneo)
**URL HTTPS:** `https://smart_competitor.youssef-ben.com` (dopo SSL)

---

## 🎯 Step di Deployment

### 1️⃣ SSH nel VPS

```bash
ssh root@217.160.0.149
# oppure se hai un utente specifico:
ssh tuoutente@217.160.0.149
```

### 2️⃣ Verifica Docker Installato

```bash
docker --version
docker compose version
```

**Se Docker NON è installato:**
```bash
curl -fsSL https://get.docker.com | sh
apt install docker-compose-plugin -y
```

### 3️⃣ Clone Repository

```bash
# Crea directory
mkdir -p /var/www
cd /var/www

# Clone (usa il tuo repository URL)
git clone https://github.com/tuoaccount/smart_competitor_finder.git
cd smart_competitor_finder

# Oppure se hai già n8n e vuoi una cartella separata:
cd /var/www
git clone https://github.com/tuoaccount/smart_competitor_finder.git smart_competitor
cd smart_competitor
```

### 4️⃣ Configura Environment

```bash
# Copia template
cp backend/.env.example backend/.env

# Modifica con le tue chiavi
nano backend/.env
```

**Configurazione MINIMA richiesta:**
```bash
OPENAI_API_KEY=sk-tua_chiave_openai

ALLOWED_ORIGINS=http://localhost:3000,http://smart_competitor.youssef-ben.com,https://smart_competitor.youssef-ben.com

SECRET_KEY=genera_una_chiave_casuale_lunga_almeno_32_caratteri
```

**Per generare SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Salva e esci:** `CTRL+X`, poi `Y`, poi `ENTER`

### 5️⃣ Verifica Configurazione Nginx

Il dominio è già configurato:
```bash
cat nginx/nginx.conf | grep server_name
```

Dovresti vedere: `smart_competitor.youssef-ben.com`

### 6️⃣ Deploy!

```bash
# Rendi eseguibile
chmod +x deploy.sh

# Deploy in production
./deploy.sh production
```

**Aspetta 2-3 minuti** per il download e build dei container...

### 7️⃣ Verifica Deployment

```bash
# Verifica container running
docker compose ps

# Dovresti vedere:
# ✅ backend - Up
# ✅ frontend - Up
# ✅ nginx - Up

# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000

# Logs
docker compose logs -f
```

### 8️⃣ Configura Firewall (Importante!)

```bash
# Install UFW se non presente
apt install ufw -y

# Configura porte
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS

# Abilita
ufw --force enable

# Verifica
ufw status
```

### 9️⃣ Test nel Browser

Apri nel browser:
```
http://smart_competitor.youssef-ben.com
```

✅ **Dovresti vedere la homepage di Smart Competitor Finder!**

---

## 🔒 Setup SSL/HTTPS (Opzionale ma Consigliato)

### Opzione 1: Cloudflare (FACILE - 5 minuti)

1. Vai su [cloudflare.com](https://cloudflare.com)
2. Aggiungi dominio `youssef-ben.com`
3. Cambia i nameserver del dominio
4. Nel dashboard Cloudflare:
   - SSL/TLS → Encryption mode → **Full**
   - SSL/TLS → Edge Certificates → **Always Use HTTPS** ON
5. ✅ **FATTO! Cloudflare gestisce tutto automaticamente**

**Vantaggi Cloudflare:**
- ✅ SSL automatico
- ✅ CDN gratis
- ✅ DDoS protection
- ✅ Caching automatico
- ✅ Zero configurazione server

### Opzione 2: Let's Encrypt (Manuale)

```bash
# Installa Certbot
apt install certbot -y

# Stop Nginx temporaneamente
docker compose stop nginx

# Genera certificati
certbot certonly --standalone \
  -d smart_competitor.youssef-ben.com \
  --email tua@email.com \
  --agree-tos

# Copia certificati
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/smart_competitor.youssef-ben.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/smart_competitor.youssef-ben.com/privkey.pem nginx/ssl/

# Modifica nginx.conf per abilitare HTTPS
nano nginx/nginx.conf
# Decommenta la sezione HTTPS (rimuovi i # all'inizio)

# Restart
docker compose up -d

# Auto-rinnovo ogni 2 mesi
echo "0 0 1 */2 * certbot renew --quiet && docker compose restart nginx" | crontab -
```

---

## 🔧 Comandi Utili

### Visualizza Logs

```bash
# Tutti i servizi
docker compose logs -f

# Solo backend
docker compose logs -f backend

# Solo frontend
docker compose logs -f frontend

# Ultimi 100 logs
docker compose logs --tail=100
```

### Restart Servizi

```bash
# Restart tutto
docker compose restart

# Restart singolo servizio
docker compose restart backend
docker compose restart frontend
docker compose restart nginx
```

### Stop/Start

```bash
# Stop tutto
docker compose down

# Start tutto
docker compose up -d

# Rebuild e restart
docker compose up -d --build
```

### Aggiorna Codice

```bash
cd /var/www/smart_competitor_finder
git pull origin main
docker compose up -d --build
```

---

## 📊 Setup Backup Automatico

```bash
# Setup backup giornaliero alle 3:00 AM
crontab -e

# Aggiungi questa riga:
0 3 * * * cd /var/www/smart_competitor_finder && ./backup.sh >> /var/log/scf-backup.log 2>&1
```

**Verifica backup:**
```bash
# Esegui backup manuale
cd /var/www/smart_competitor_finder
./backup.sh

# Lista backup
ls -lh /var/backups/smart_competitor_finder/
```

---

## 🚨 Troubleshooting

### Container non si avvia

```bash
docker compose logs backend
docker compose logs frontend
```

### Porta 80 già in uso (se hai n8n)

**Problema:** Se n8n usa già la porta 80, cambiale:

```bash
nano docker-compose.yml
```

Modifica:
```yaml
nginx:
  ports:
    - "8080:80"  # Usa porta 8080 invece di 80
    - "8443:443"
```

Poi accedi su: `http://smart_competitor.youssef-ben.com:8080`

### Backend non risponde

```bash
# Verifica .env configurato
docker compose exec backend env | grep OPENAI_API_KEY

# Se vuoto, configura .env e restart
nano backend/.env
docker compose restart backend
```

### Verifica IP e porte

```bash
# Verifica IP server
ip addr show

# Verifica porte in uso
netstat -tulpn | grep -E '80|443|8000|3000'

# Verifica container
docker compose ps
```

---

## ✅ Checklist Finale

- [ ] DNS Record A configurato: `smart_competitor → 217.160.0.149`
- [ ] SSH nel VPS funzionante
- [ ] Docker + Docker Compose installati
- [ ] Repository clonato in `/var/www/smart_competitor_finder`
- [ ] `.env` configurato con `OPENAI_API_KEY`
- [ ] `./deploy.sh production` eseguito con successo
- [ ] Firewall configurato (porte 22, 80, 443)
- [ ] Container up: `docker compose ps` mostra tutto UP
- [ ] Backend healthy: `curl http://localhost:8000/health`
- [ ] Sito raggiungibile: `http://smart_competitor.youssef-ben.com`
- [ ] SSL/HTTPS configurato (Cloudflare o Let's Encrypt)
- [ ] Backup automatico configurato
- [ ] Test completo: Analizza sito → Upload Excel → Download Report

---

## 🎉 Deploy Completato!

Il tuo Smart Competitor Finder è online su:
- **HTTP:** `http://smart_competitor.youssef-ben.com`
- **HTTPS:** `https://smart_competitor.youssef-ben.com` (dopo SSL)

**Backend API Docs:** `http://smart_competitor.youssef-ben.com/api/docs`

---

## 📞 Support

Se hai problemi:

1. **Verifica logs:** `docker compose logs -f`
2. **Verifica .env:** `cat backend/.env`
3. **Verifica DNS:** `nslookup smart_competitor.youssef-ben.com`
4. **Test backend:** `curl http://localhost:8000/health`

**Comandi di emergenza:**
```bash
# Restart totale
docker compose restart

# Rebuild completo
docker compose down
docker compose up -d --build

# Pulizia
docker system prune -f
```

Buon lavoro! 🚀
