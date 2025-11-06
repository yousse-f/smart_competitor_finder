#!/bin/bash

# 🔄 Restore Script for Smart Competitor Finder Backups
# Use this to restore from a backup archive

set -e

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

show_usage() {
    echo "Usage: $0 <backup_file>"
    echo ""
    echo "Example:"
    echo "  $0 /var/backups/smart_competitor_finder/backup_20240115_120000.tar.gz"
    echo ""
    echo "Available backups:"
    if [ -d "/var/backups/smart_competitor_finder" ]; then
        ls -lh /var/backups/smart_competitor_finder/backup_*.tar.gz 2>/dev/null || echo "  No backups found"
    else
        echo "  Backup directory not found"
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PRE-FLIGHT CHECKS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Check if backup file provided
if [ $# -eq 0 ]; then
    error "No backup file specified"
    echo ""
    show_usage
    exit 1
fi

BACKUP_FILE=$1

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root"
   exit 1
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Verify backup integrity
log "Verifying backup integrity..."
if ! tar -tzf "$BACKUP_FILE" > /dev/null 2>&1; then
    error "Backup file is corrupted or invalid"
    exit 1
fi
success "Backup file is valid"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SHOW BACKUP INFO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Backup Information"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "File: $BACKUP_FILE"
echo "Size: $(du -h "$BACKUP_FILE" | cut -f1)"
echo "Date: $(stat -c %y "$BACKUP_FILE" 2>/dev/null || stat -f "%Sm" "$BACKUP_FILE" 2>/dev/null)"
echo ""

# Extract and show backup_info.txt if available
TEMP_INFO=$(mktemp)
tar -xzf "$BACKUP_FILE" -O smart_competitor_finder/backup_info.txt > "$TEMP_INFO" 2>/dev/null || true

if [ -s "$TEMP_INFO" ]; then
    cat "$TEMP_INFO"
    rm "$TEMP_INFO"
else
    warning "No backup info available"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIRMATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

warning "This will restore the backup and OVERWRITE existing files!"
warning "Current configuration and reports will be backed up first."
echo ""
read -p "Do you want to continue? [y/N]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log "Restore cancelled by user"
    exit 0
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PRE-RESTORE BACKUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT_DIR="/var/www/smart_competitor_finder"
PRE_RESTORE_BACKUP="/var/backups/smart_competitor_finder/pre_restore_$(date +%Y%m%d_%H%M%S).tar.gz"

if [ -d "$PROJECT_DIR" ]; then
    log "Creating pre-restore backup of current state..."
    mkdir -p /var/backups/smart_competitor_finder
    tar -czf "$PRE_RESTORE_BACKUP" -C "$PROJECT_DIR" . 2>/dev/null || warning "Could not create pre-restore backup"
    success "Pre-restore backup saved: $PRE_RESTORE_BACKUP"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STOP CONTAINERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log "Stopping Docker containers..."
cd "$PROJECT_DIR"
docker-compose down 2>/dev/null || warning "Could not stop containers (may not be running)"
success "Containers stopped"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RESTORE PROCESS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log "Extracting backup archive..."
TEMP_DIR=$(mktemp -d)
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

EXTRACT_DIR="$TEMP_DIR/smart_competitor_finder"

# 1. Restore configuration files
log "Restoring configuration files..."
if [ -f "$EXTRACT_DIR/config/.env" ]; then
    cp "$EXTRACT_DIR/config/.env" "$PROJECT_DIR/backend/.env"
    success "Restored .env"
else
    warning ".env not found in backup"
fi

if [ -f "$EXTRACT_DIR/config/docker-compose.yml" ]; then
    cp "$EXTRACT_DIR/config/docker-compose.yml" "$PROJECT_DIR/docker-compose.yml"
    success "Restored docker-compose.yml"
else
    warning "docker-compose.yml not found in backup"
fi

if [ -f "$EXTRACT_DIR/config/nginx.conf" ]; then
    mkdir -p "$PROJECT_DIR/nginx"
    cp "$EXTRACT_DIR/config/nginx.conf" "$PROJECT_DIR/nginx/nginx.conf"
    success "Restored nginx.conf"
else
    warning "nginx.conf not found in backup"
fi

# 2. Restore reports
log "Restoring reports..."
if [ -d "$EXTRACT_DIR/reports" ]; then
    mkdir -p "$PROJECT_DIR/backend/reports"
    cp -r "$EXTRACT_DIR/reports/"* "$PROJECT_DIR/backend/reports/" 2>/dev/null || true
    REPORT_COUNT=$(find "$EXTRACT_DIR/reports" -type f | wc -l)
    success "Restored $REPORT_COUNT report(s)"
else
    warning "Reports not found in backup"
fi

# 3. Restore SSL certificates
log "Restoring SSL certificates..."
if [ -d "$EXTRACT_DIR/ssl" ]; then
    mkdir -p "$PROJECT_DIR/nginx/ssl"
    cp -r "$EXTRACT_DIR/ssl/"* "$PROJECT_DIR/nginx/ssl/" 2>/dev/null || true
    success "Restored SSL certificates"
else
    warning "SSL certificates not found in backup"
fi

# Clean up temporary directory
rm -rf "$TEMP_DIR"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RESTART CONTAINERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log "Restarting Docker containers..."
cd "$PROJECT_DIR"
docker-compose up -d

# Wait for containers to be healthy
log "Waiting for containers to be healthy..."
sleep 5

# Check container status
if docker-compose ps | grep -q "Up"; then
    success "Containers restarted successfully"
else
    warning "Some containers may not be running properly"
    echo ""
    docker-compose ps
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VERIFICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log "Verifying restore..."
sleep 3

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    success "Backend is healthy"
else
    warning "Backend health check failed"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    success "Frontend is responding"
else
    warning "Frontend health check failed"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SUMMARY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Restore Completed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Restored from: $(basename "$BACKUP_FILE")"
echo "Pre-restore backup: $PRE_RESTORE_BACKUP"
echo ""
echo "Restored items:"
echo "  ✓ Configuration files"
echo "  ✓ Generated reports"
echo "  ✓ SSL certificates"
echo ""
echo "Container status:"
docker-compose ps
echo ""
echo "Next steps:"
echo "  • Check logs: docker-compose logs -f"
echo "  • Test application: http://localhost:3000"
echo "  • Verify API: http://localhost:8000/docs"
echo ""
success "Restore completed at $(date)"

exit 0
