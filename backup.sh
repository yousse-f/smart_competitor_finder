#!/bin/bash

# 💾 Automated Backup Script for Smart Competitor Finder
# Run this script periodically via cron for automated backups

set -e

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Project directory
PROJECT_DIR="/var/www/smart_competitor_finder"

# Backup directory
BACKUP_DIR="/var/backups/smart_competitor_finder"

# Number of backups to keep (older backups will be deleted)
KEEP_BACKUPS=7

# Date format for backup files
DATE=$(date +%Y%m%d_%H%M%S)

# Backup filename
BACKUP_FILE="backup_${DATE}.tar.gz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PRE-FLIGHT CHECKS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log "Starting backup process..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root"
   exit 1
fi

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    error "Project directory not found: $PROJECT_DIR"
    exit 1
fi

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    log "Creating backup directory: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BACKUP PROCESS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cd "$PROJECT_DIR"

log "Creating backup archive..."

# Create temporary directory for backup staging
TEMP_DIR=$(mktemp -d)
BACKUP_STAGING="$TEMP_DIR/smart_competitor_finder"
mkdir -p "$BACKUP_STAGING"

# 1. Backup configuration files
log "Backing up configuration files..."
mkdir -p "$BACKUP_STAGING/config"
cp backend/.env "$BACKUP_STAGING/config/.env" 2>/dev/null || warning ".env file not found"
cp docker-compose.yml "$BACKUP_STAGING/config/" 2>/dev/null || warning "docker-compose.yml not found"
cp nginx/nginx.conf "$BACKUP_STAGING/config/" 2>/dev/null || warning "nginx.conf not found"
success "Configuration files backed up"

# 2. Backup reports
log "Backing up reports..."
if [ -d "backend/reports" ]; then
    mkdir -p "$BACKUP_STAGING/reports"
    cp -r backend/reports/* "$BACKUP_STAGING/reports/" 2>/dev/null || warning "No reports found"
    REPORT_COUNT=$(find backend/reports -type f | wc -l)
    success "Reports backed up ($REPORT_COUNT files)"
else
    warning "Reports directory not found"
fi

# 3. Backup SSL certificates
log "Backing up SSL certificates..."
if [ -d "nginx/ssl" ]; then
    mkdir -p "$BACKUP_STAGING/ssl"
    cp -r nginx/ssl/* "$BACKUP_STAGING/ssl/" 2>/dev/null || warning "No SSL certificates found"
    success "SSL certificates backed up"
else
    warning "SSL directory not found"
fi

# 4. Backup logs (last 7 days only)
log "Backing up recent logs..."
mkdir -p "$BACKUP_STAGING/logs"
docker-compose logs --since 7d --no-color > "$BACKUP_STAGING/logs/docker-compose.log" 2>/dev/null || warning "Could not export Docker logs"
success "Logs backed up"

# 5. Create metadata file
log "Creating backup metadata..."
cat > "$BACKUP_STAGING/backup_info.txt" <<EOF
Smart Competitor Finder - Backup Information
=============================================

Backup Date: $(date)
Backup File: $BACKUP_FILE
Hostname: $(hostname)

Project Directory: $PROJECT_DIR

Docker Containers Status:
$(docker-compose ps 2>/dev/null || echo "Could not retrieve container status")

Disk Usage:
$(df -h "$PROJECT_DIR" 2>/dev/null || echo "Could not retrieve disk usage")

Included in this backup:
- Configuration files (.env, docker-compose.yml, nginx.conf)
- Generated reports
- SSL certificates
- Docker logs (last 7 days)

To restore this backup:
1. Stop containers: docker-compose down
2. Extract archive: tar -xzf $BACKUP_FILE
3. Copy files back to project directory
4. Restart containers: docker-compose up -d
EOF
success "Metadata created"

# 6. Create compressed archive
log "Compressing backup archive..."
cd "$TEMP_DIR"
tar -czf "$BACKUP_DIR/$BACKUP_FILE" smart_competitor_finder/

# Calculate archive size
BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
success "Backup archive created: $BACKUP_FILE ($BACKUP_SIZE)"

# Clean up temporary directory
rm -rf "$TEMP_DIR"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLEANUP OLD BACKUPS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log "Cleaning up old backups (keeping last $KEEP_BACKUPS)..."

cd "$BACKUP_DIR"
BACKUP_COUNT=$(ls -1 backup_*.tar.gz 2>/dev/null | wc -l)

if [ "$BACKUP_COUNT" -gt "$KEEP_BACKUPS" ]; then
    # Delete oldest backups
    ls -1t backup_*.tar.gz | tail -n +$((KEEP_BACKUPS + 1)) | xargs rm -f
    DELETED_COUNT=$((BACKUP_COUNT - KEEP_BACKUPS))
    success "Deleted $DELETED_COUNT old backup(s)"
else
    log "No old backups to delete"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VERIFICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log "Verifying backup integrity..."

if tar -tzf "$BACKUP_DIR/$BACKUP_FILE" > /dev/null 2>&1; then
    success "Backup archive is valid"
else
    error "Backup archive is corrupted!"
    exit 1
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SUMMARY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Backup Completed Successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Backup Details:"
echo "  • File: $BACKUP_FILE"
echo "  • Size: $BACKUP_SIZE"
echo "  • Location: $BACKUP_DIR"
echo "  • Total backups: $BACKUP_COUNT"
echo ""
echo "Backup includes:"
echo "  ✓ Configuration files"
echo "  ✓ Generated reports"
echo "  ✓ SSL certificates"
echo "  ✓ Recent logs (7 days)"
echo ""
echo "To restore this backup:"
echo "  cd $BACKUP_DIR"
echo "  tar -xzf $BACKUP_FILE"
echo "  # Then copy files back to project directory"
echo ""
success "Backup process completed at $(date)"

# Optional: Send notification (uncomment and configure)
# curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
#   -d "chat_id=<YOUR_CHAT_ID>" \
#   -d "text=✅ Backup completed: $BACKUP_FILE ($BACKUP_SIZE)" \
#   > /dev/null 2>&1

exit 0
