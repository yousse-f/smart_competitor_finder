#!/bin/bash

# 🚀 Script per pushare modifiche su GitHub
# Uso: ./push-to-github.sh "messaggio del commit"

set -e  # Exit on error

# Colori per output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 Smart Competitor Finder - GitHub Push Script${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Verifica messaggio commit
if [ -z "$1" ]; then
    echo -e "${RED}❌ Errore: Devi fornire un messaggio di commit${NC}"
    echo -e "${YELLOW}Uso: ./push-to-github.sh \"tuo messaggio\"${NC}"
    echo ""
    echo -e "${YELLOW}Esempi:${NC}"
    echo -e "  ./push-to-github.sh \"fix: Risolto bug in scraping\""
    echo -e "  ./push-to-github.sh \"feat: Aggiunta nuova funzionalità\""
    exit 1
fi

COMMIT_MESSAGE="$1"

# 1. Verifica file modificati
echo -e "${BLUE}📋 Step 1: Verifica file modificati${NC}"
git status --short
echo ""

# 2. Rimuovi backend/.env se presente (per evitare push di secrets)
if git diff --cached --name-only | grep -q "backend/.env"; then
    echo -e "${YELLOW}⚠️  Rimuovo backend/.env dallo staging (contiene secrets)${NC}"
    git restore --staged backend/.env
fi

if git diff --name-only | grep -q "backend/.env"; then
    echo -e "${YELLOW}⚠️  backend/.env modificato ma non verrà committato${NC}"
fi

# 3. Aggiungi tutti i file (escluso .env)
echo -e "${BLUE}📦 Step 2: Aggiungo file allo staging${NC}"
git add backend/api/ backend/core/ backend/main.py backend/reports/ 2>/dev/null || true
git add frontend/ 2>/dev/null || true
git add *.md *.sh docker-compose.yml requirements.txt 2>/dev/null || true
echo -e "${GREEN}✅ File aggiunti allo staging${NC}"
echo ""

# 4. Mostra file da committare
echo -e "${BLUE}📝 Step 3: File da committare:${NC}"
git diff --cached --name-only | head -20
TOTAL_FILES=$(git diff --cached --name-only | wc -l | xargs)
if [ "$TOTAL_FILES" -gt 20 ]; then
    echo -e "${YELLOW}   ... e altri $(($TOTAL_FILES - 20)) file${NC}"
fi
echo ""

# 5. Conferma
echo -e "${YELLOW}📢 Commit message: ${NC}\"${COMMIT_MESSAGE}\""
echo ""
read -p "🤔 Vuoi procedere con commit e push? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Push annullato${NC}"
    exit 1
fi

# 6. Commit
echo ""
echo -e "${BLUE}💾 Step 4: Commit modifiche${NC}"
git commit -m "$COMMIT_MESSAGE"
echo -e "${GREEN}✅ Commit creato${NC}"
echo ""

# 7. Push
echo -e "${BLUE}🚀 Step 5: Push su GitHub${NC}"
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ Push completato con successo!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BLUE}🔄 Deploy automatici in corso:${NC}"
    echo -e "   • Railway (Backend):  https://railway.app/project/SMART_FINDER"
    echo -e "   • Vercel (Frontend):  https://vercel.com/dashboard"
    echo ""
    echo -e "${YELLOW}💡 Suggerimento:${NC} Aspetta 2-3 minuti per il deploy automatico"
else
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ Errore durante il push!${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}🔍 Possibili cause:${NC}"
    echo -e "   1. File .env committato (contiene secrets)"
    echo -e "   2. Conflitti con modifiche remote"
    echo -e "   3. Problemi di rete"
    echo ""
    echo -e "${YELLOW}💡 Soluzioni:${NC}"
    echo -e "   • Verifica errori sopra"
    echo -e "   • Esegui: git status"
    echo -e "   • Esegui: git pull origin main"
    exit 1
fi
