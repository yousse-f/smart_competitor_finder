#!/bin/bash

# 🔒 Security Setup Script for Smart Competitor Finder VPS
# Run this AFTER deployment to secure your VPS

set -e

echo "🔒 Starting VPS Security Configuration..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root${NC}" 
   exit 1
fi

echo -e "${GREEN}✓${NC} Running as root"

# 1. Configure UFW Firewall
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛡️  Step 1: Configuring UFW Firewall"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Install UFW if not present
if ! command -v ufw &> /dev/null; then
    echo "Installing UFW..."
    apt-get update
    apt-get install -y ufw
fi

# Reset UFW to default
echo "Resetting UFW to default settings..."
ufw --force reset

# Set default policies
echo "Setting default policies (deny incoming, allow outgoing)..."
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (IMPORTANT!)
echo "Allowing SSH (port 22)..."
ufw allow 22/tcp comment 'SSH'

# Allow HTTP and HTTPS
echo "Allowing HTTP (port 80)..."
ufw allow 80/tcp comment 'HTTP'

echo "Allowing HTTPS (port 443)..."
ufw allow 443/tcp comment 'HTTPS'

# Enable UFW
echo "Enabling UFW..."
ufw --force enable

echo -e "${GREEN}✓${NC} Firewall configured successfully"
ufw status verbose

# 2. Configure Fail2Ban
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚫 Step 2: Installing Fail2Ban"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Install Fail2Ban
if ! command -v fail2ban-client &> /dev/null; then
    echo "Installing Fail2Ban..."
    apt-get install -y fail2ban
fi

# Create custom jail configuration
cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
destemail = root@localhost
sendername = Fail2Ban

[sshd]
enabled = true
port = 22
logpath = %(sshd_log)s
backend = %(sshd_backend)s

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-botsearch]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
EOF

# Restart Fail2Ban
systemctl restart fail2ban
systemctl enable fail2ban

echo -e "${GREEN}✓${NC} Fail2Ban configured and running"
fail2ban-client status

# 3. Configure automatic security updates
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 Step 3: Enabling Automatic Security Updates"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Install unattended-upgrades
if ! dpkg -l | grep -q unattended-upgrades; then
    echo "Installing unattended-upgrades..."
    apt-get install -y unattended-upgrades
fi

# Configure automatic updates
cat > /etc/apt/apt.conf.d/50unattended-upgrades <<EOF
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}-security";
    "\${distro_id}ESMApps:\${distro_codename}-apps-security";
    "\${distro_id}ESM:\${distro_codename}-infra-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

cat > /etc/apt/apt.conf.d/20auto-upgrades <<EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOF

systemctl restart unattended-upgrades

echo -e "${GREEN}✓${NC} Automatic security updates enabled"

# 4. Disable root SSH login (optional but recommended)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔐 Step 4: SSH Security Hardening"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

read -p "Do you want to disable root SSH login? (recommended if you have sudo user) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Backup SSH config
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # Disable root login
    sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
    
    # Disable password authentication (force SSH keys)
    sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
    
    # Restart SSH
    systemctl restart sshd
    
    echo -e "${GREEN}✓${NC} Root SSH login disabled"
    echo -e "${YELLOW}⚠️  IMPORTANT: Make sure you have SSH key access and sudo user before logging out!${NC}"
else
    echo "Skipping root SSH login disable"
fi

# 5. Setup log rotation for Docker
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Step 5: Configuring Docker Log Rotation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Configure Docker daemon for log rotation
cat > /etc/docker/daemon.json <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# Restart Docker
systemctl restart docker

echo -e "${GREEN}✓${NC} Docker log rotation configured (max 10MB per file, 3 files)"

# 6. Setup Docker container restart policies
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "♻️  Step 6: Verifying Container Restart Policies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "docker-compose.yml" ]; then
    echo "Checking restart policies in docker-compose.yml..."
    if grep -q "restart: unless-stopped" docker-compose.yml; then
        echo -e "${GREEN}✓${NC} Restart policies already configured"
    else
        echo -e "${YELLOW}⚠️  Restart policies not found in docker-compose.yml${NC}"
        echo "Consider adding 'restart: unless-stopped' to all services"
    fi
else
    echo -e "${YELLOW}⚠️  docker-compose.yml not found in current directory${NC}"
fi

# 7. Rate limiting in Nginx (if nginx folder exists)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚦 Step 7: Checking Nginx Rate Limiting"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "nginx/nginx.conf" ]; then
    if grep -q "limit_req_zone" nginx/nginx.conf; then
        echo -e "${GREEN}✓${NC} Nginx rate limiting already configured"
    else
        echo -e "${YELLOW}⚠️  Consider adding rate limiting to nginx.conf${NC}"
        echo "Example:"
        echo "  limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;"
    fi
else
    echo -e "${YELLOW}⚠️  nginx/nginx.conf not found${NC}"
fi

# 8. Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Security Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Security measures applied:"
echo -e "${GREEN}✓${NC} UFW Firewall enabled (ports 22, 80, 443)"
echo -e "${GREEN}✓${NC} Fail2Ban installed and configured"
echo -e "${GREEN}✓${NC} Automatic security updates enabled"
echo -e "${GREEN}✓${NC} Docker log rotation configured"
echo ""
echo "Additional recommendations:"
echo "  • Create a sudo user and disable root login"
echo "  • Use SSH keys instead of passwords"
echo "  • Setup monitoring (Uptime Robot, Grafana, etc.)"
echo "  • Regular backups of /var/www/smart_competitor_finder"
echo "  • Monitor logs: journalctl -fu docker"
echo ""
echo "Useful commands:"
echo "  • Check firewall: ufw status"
echo "  • Check Fail2Ban: fail2ban-client status"
echo "  • Check banned IPs: fail2ban-client status sshd"
echo "  • View security logs: tail -f /var/log/fail2ban.log"
echo ""
echo -e "${GREEN}🔒 Your VPS is now more secure!${NC}"
