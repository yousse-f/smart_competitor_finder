# 🤖 Automazione e Monitoring - Smart Competitor Finder

## 📋 Indice

1. [Backup Automatici](#backup-automatici)
2. [Monitoring e Alerting](#monitoring-e-alerting)
3. [Health Checks](#health-checks)
4. [Log Rotation](#log-rotation)
5. [Aggiornamenti Automatici](#aggiornamenti-automatici)
6. [Cron Jobs Setup](#cron-jobs-setup)

---

## 💾 Backup Automatici

### Setup Backup Giornaliero

```bash
# Rendi eseguibili gli script
chmod +x backup.sh restore.sh

# Aggiungi al crontab
crontab -e
```

**Aggiungi questa riga per backup giornaliero alle 3:00 AM:**

```bash
0 3 * * * cd /var/www/smart_competitor_finder && ./backup.sh >> /var/log/backup.log 2>&1
```

### Altre Frequenze

```bash
# Ogni 6 ore
0 */6 * * * cd /var/www/smart_competitor_finder && ./backup.sh

# Ogni domenica alle 4:00 AM
0 4 * * 0 cd /var/www/smart_competitor_finder && ./backup.sh

# Ogni giorno alle 2:00 AM E alle 14:00 PM
0 2,14 * * * cd /var/www/smart_competitor_finder && ./backup.sh
```

### Test Backup Manuale

```bash
# Test backup
cd /var/www/smart_competitor_finder
./backup.sh

# Verifica backup creato
ls -lh /var/backups/smart_competitor_finder/

# Test restore (ATTENZIONE: sovrascrive!)
./restore.sh /var/backups/smart_competitor_finder/backup_XXXXXXXX_XXXXXX.tar.gz
```

### Backup Remoto (S3-Compatible)

```bash
# Installa AWS CLI o rclone
apt install awscli -y

# Configura credenziali
aws configure

# Script per upload automatico
cat > /usr/local/bin/backup-to-s3.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/smart_competitor_finder"
LATEST_BACKUP=$(ls -t $BACKUP_DIR/backup_*.tar.gz | head -1)
aws s3 cp "$LATEST_BACKUP" s3://your-bucket/smart-competitor-finder/
EOF

chmod +x /usr/local/bin/backup-to-s3.sh

# Aggiungi al cron (dopo backup locale)
0 4 * * * /usr/local/bin/backup-to-s3.sh
```

---

## 📊 Monitoring e Alerting

### Uptime Robot (Gratis)

1. Registrati su [UptimeRobot.com](https://uptimerobot.com)
2. Crea monitor HTTP(S):
   - URL: `https://tuodominio.com/health`
   - Intervallo: 5 minuti
   - Alert via: Email, SMS, Telegram

### Telegram Notifications

```bash
# Crea bot Telegram:
# 1. Parla con @BotFather su Telegram
# 2. Crea nuovo bot con /newbot
# 3. Ottieni TOKEN
# 4. Aggiungi bot al tuo gruppo
# 5. Ottieni CHAT_ID visitando: https://api.telegram.org/botTOKEN/getUpdates

# Script notifica
cat > /usr/local/bin/telegram-notify.sh <<'EOF'
#!/bin/bash
TOKEN="YOUR_BOT_TOKEN"
CHAT_ID="YOUR_CHAT_ID"
MESSAGE="$1"

curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -d "chat_id=${CHAT_ID}" \
  -d "text=${MESSAGE}" \
  -d "parse_mode=HTML" > /dev/null
EOF

chmod +x /usr/local/bin/telegram-notify.sh

# Test
/usr/local/bin/telegram-notify.sh "🚀 Smart Competitor Finder is online!"
```

### Health Check Script

```bash
cat > /usr/local/bin/health-check.sh <<'EOF'
#!/bin/bash

PROJECT_DIR="/var/www/smart_competitor_finder"
cd $PROJECT_DIR

# Check containers
if ! docker-compose ps | grep -q "Up"; then
    /usr/local/bin/telegram-notify.sh "🚨 ALERT: Some containers are DOWN!"
    docker-compose up -d
    /usr/local/bin/telegram-notify.sh "♻️ Containers restarted automatically"
fi

# Check backend API
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    /usr/local/bin/telegram-notify.sh "🚨 ALERT: Backend API is not responding!"
    docker-compose restart backend
fi

# Check frontend
if ! curl -f http://localhost:3000 > /dev/null 2>&1; then
    /usr/local/bin/telegram-notify.sh "🚨 ALERT: Frontend is not responding!"
    docker-compose restart frontend
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    /usr/local/bin/telegram-notify.sh "⚠️ WARNING: Disk usage is ${DISK_USAGE}%"
fi

# Check memory
MEM_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ $MEM_USAGE -gt 90 ]; then
    /usr/local/bin/telegram-notify.sh "⚠️ WARNING: Memory usage is ${MEM_USAGE}%"
fi
EOF

chmod +x /usr/local/bin/health-check.sh

# Aggiungi al cron (ogni 5 minuti)
crontab -e
```

```bash
*/5 * * * * /usr/local/bin/health-check.sh
```

---

## 🩺 Health Checks

### Endpoint Personalizzato

Aggiungi al backend (`backend/main.py`):

```python
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    import psutil
    import time
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": time.time() - start_time,  # Definisci start_time all'avvio
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    }
```

### Check da Cron

```bash
# Script health check avanzato
cat > /usr/local/bin/advanced-health-check.sh <<'EOF'
#!/bin/bash

BACKEND_URL="http://localhost:8000/health"
FRONTEND_URL="http://localhost:3000"
DOMAIN_URL="https://tuodominio.com"

# Check backend
BACKEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL)
if [ "$BACKEND_RESPONSE" != "200" ]; then
    echo "Backend health check failed: HTTP $BACKEND_RESPONSE"
    /usr/local/bin/telegram-notify.sh "🚨 Backend health check failed: HTTP $BACKEND_RESPONSE"
fi

# Check frontend
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL)
if [ "$FRONTEND_RESPONSE" != "200" ]; then
    echo "Frontend health check failed: HTTP $FRONTEND_RESPONSE"
    /usr/local/bin/telegram-notify.sh "🚨 Frontend health check failed: HTTP $FRONTEND_RESPONSE"
fi

# Check domain (external access)
DOMAIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $DOMAIN_URL)
if [ "$DOMAIN_RESPONSE" != "200" ]; then
    echo "Domain check failed: HTTP $DOMAIN_RESPONSE"
    /usr/local/bin/telegram-notify.sh "🚨 Domain check failed: HTTP $DOMAIN_RESPONSE"
fi

# Check SSL certificate expiration
if command -v openssl &> /dev/null; then
    CERT_DAYS=$(echo | openssl s_client -servername tuodominio.com -connect tuodominio.com:443 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2 | xargs -I{} date -d {} +%s)
    NOW=$(date +%s)
    DAYS_LEFT=$(( ($CERT_DAYS - $NOW) / 86400 ))
    
    if [ $DAYS_LEFT -lt 30 ]; then
        /usr/local/bin/telegram-notify.sh "⚠️ SSL certificate expires in $DAYS_LEFT days!"
    fi
fi
EOF

chmod +x /usr/local/bin/advanced-health-check.sh

# Aggiungi al cron (ogni 15 minuti)
*/15 * * * * /usr/local/bin/advanced-health-check.sh
```

---

## 📝 Log Rotation

### Docker Logs

Già configurato in `deploy.sh` con:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### Custom Log Rotation

```bash
# Crea configurazione logrotate
cat > /etc/logrotate.d/smart-competitor-finder <<'EOF'
/var/log/smart-competitor-finder/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        docker-compose -f /var/www/smart_competitor_finder/docker-compose.yml restart nginx > /dev/null 2>&1 || true
    endscript
}
EOF

# Test logrotate
logrotate -d /etc/logrotate.d/smart-competitor-finder
```

### Export Logs Periodicamente

```bash
cat > /usr/local/bin/export-logs.sh <<'EOF'
#!/bin/bash
LOG_DIR="/var/www/smart_competitor_finder/exported-logs"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $LOG_DIR

cd /var/www/smart_competitor_finder

# Export Docker logs
docker-compose logs --since 24h --no-color > "$LOG_DIR/docker_${DATE}.log"

# Compress old logs
find $LOG_DIR -name "*.log" -mtime +7 -exec gzip {} \;

# Delete very old logs (>30 days)
find $LOG_DIR -name "*.log.gz" -mtime +30 -delete
EOF

chmod +x /usr/local/bin/export-logs.sh

# Esegui ogni giorno alle 23:00
0 23 * * * /usr/local/bin/export-logs.sh
```

---

## 🔄 Aggiornamenti Automatici

### Sistema Operativo

Già configurato in `security-setup.sh` con `unattended-upgrades`.

Verifica:

```bash
# Status
systemctl status unattended-upgrades

# Logs
tail -f /var/log/unattended-upgrades/unattended-upgrades.log
```

### Docker Images

```bash
cat > /usr/local/bin/update-docker-images.sh <<'EOF'
#!/bin/bash
cd /var/www/smart_competitor_finder

echo "Pulling latest images..."
docker-compose pull

echo "Rebuilding containers..."
docker-compose up -d --build

echo "Removing old images..."
docker image prune -f

/usr/local/bin/telegram-notify.sh "✅ Docker images updated successfully"
EOF

chmod +x /usr/local/bin/update-docker-images.sh

# Update settimanale (domenica alle 5:00 AM)
0 5 * * 0 /usr/local/bin/update-docker-images.sh
```

### Applicazione (Git Pull)

```bash
cat > /usr/local/bin/update-app.sh <<'EOF'
#!/bin/bash
cd /var/www/smart_competitor_finder

# Backup prima di aggiornare
./backup.sh

# Pull latest code
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ $LOCAL != $REMOTE ]; then
    echo "Updates available, pulling..."
    git pull origin main
    
    # Rebuild
    docker-compose down
    docker-compose up -d --build
    
    /usr/local/bin/telegram-notify.sh "✅ Application updated to latest version"
else
    echo "Already up to date"
fi
EOF

chmod +x /usr/local/bin/update-app.sh

# Check aggiornamenti giornaliero (5:30 AM)
30 5 * * * /usr/local/bin/update-app.sh
```

---

## ⏰ Cron Jobs Setup Completo

### File Crontab Completo

```bash
crontab -e
```

**Aggiungi:**

```bash
# Backup giornaliero alle 3:00 AM
0 3 * * * cd /var/www/smart_competitor_finder && ./backup.sh >> /var/log/backup.log 2>&1

# Health check ogni 5 minuti
*/5 * * * * /usr/local/bin/health-check.sh

# Advanced health check ogni 15 minuti
*/15 * * * * /usr/local/bin/advanced-health-check.sh

# Export logs giornaliero alle 23:00
0 23 * * * /usr/local/bin/export-logs.sh

# Update Docker images ogni domenica alle 5:00 AM
0 5 * * 0 /usr/local/bin/update-docker-images.sh

# Check app updates giornaliero alle 5:30 AM
30 5 * * * /usr/local/bin/update-app.sh

# SSL renewal ogni 2 mesi
0 0 1 */2 * certbot renew --quiet && docker-compose -f /var/www/smart_competitor_finder/docker-compose.yml restart nginx

# Cleanup disk space settimanale (sabato alle 4:00 AM)
0 4 * * 6 docker system prune -f

# Report settimanale (lunedì alle 9:00 AM)
0 9 * * 1 /usr/local/bin/weekly-report.sh
```

### Weekly Report Script

```bash
cat > /usr/local/bin/weekly-report.sh <<'EOF'
#!/bin/bash

REPORT=$(cat <<REPORT_END
📊 <b>Weekly Report - Smart Competitor Finder</b>

🖥️ <b>System Status:</b>
- Uptime: $(uptime -p)
- Disk Usage: $(df -h / | awk 'NR==2 {print $5}')
- Memory Usage: $(free | grep Mem | awk '{print int($3/$2 * 100)}')%

🐳 <b>Docker Containers:</b>
$(docker-compose -f /var/www/smart_competitor_finder/docker-compose.yml ps)

💾 <b>Backups:</b>
- Total: $(ls -1 /var/backups/smart_competitor_finder/backup_*.tar.gz | wc -l)
- Latest: $(ls -t /var/backups/smart_competitor_finder/backup_*.tar.gz | head -1 | xargs basename)
- Size: $(du -sh /var/backups/smart_competitor_finder | cut -f1)

📈 <b>Last 7 Days Stats:</b>
- Container Restarts: $(journalctl -u docker --since "7 days ago" | grep -c restart || echo 0)
- Failed Health Checks: $(grep -c "ALERT" /var/log/syslog 2>/dev/null || echo 0)

✅ All systems operational
REPORT_END
)

/usr/local/bin/telegram-notify.sh "$REPORT"
EOF

chmod +x /usr/local/bin/weekly-report.sh
```

---

## 📊 Monitoring Dashboard (Opzionale)

### Grafana + Prometheus (Advanced)

```bash
# Aggiungi a docker-compose.yml
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

Accesso Grafana: `http://tuodominio.com:3001`

---

## ✅ Verifica Setup

```bash
# Verifica cron jobs
crontab -l

# Test tutti gli script
/usr/local/bin/health-check.sh
/usr/local/bin/advanced-health-check.sh
/usr/local/bin/telegram-notify.sh "🧪 Test notification"
/usr/local/bin/weekly-report.sh

# Verifica logs cron
tail -f /var/log/syslog | grep CRON

# Verifica backup
ls -lh /var/backups/smart_competitor_finder/
```

---

## 🎯 Quick Commands

```bash
# Visualizza cron jobs
crontab -l

# Edit cron jobs
crontab -e

# Visualizza logs cron
grep CRON /var/log/syslog

# Test script manualmente
/usr/local/bin/health-check.sh

# Force backup ora
cd /var/www/smart_competitor_finder && ./backup.sh

# Lista tutti i backup
ls -lh /var/backups/smart_competitor_finder/
```

Tutto configurato per un sistema completamente automatizzato! 🚀
