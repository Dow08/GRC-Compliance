#!/usr/bin/env bash
# =============================================================
# deploy.sh — Déploiement automatisé de CISO Assistant
# Projet : grc-smsi-automatise-demo / TechShop SAS
# =============================================================
set -e

DOCKER_DIR="$(cd "$(dirname "$0")/../docker" && pwd)"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; exit 1; }

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║     CISO Assistant — Déploiement TechShop SAS       ║"
echo "║     Projet GRC Portfolio — Dorian Poncelet           ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Vérification Docker
command -v docker &>/dev/null || err "Docker non trouvé. Installez Docker Desktop ou Docker Engine."
docker info &>/dev/null          || err "Docker daemon non démarré. Lancez Docker Desktop."
log "Docker disponible"

# Vérification Docker Compose
docker compose version &>/dev/null || err "Docker Compose plugin non trouvé."
log "Docker Compose disponible"

# Fichier .env
cd "$DOCKER_DIR"
if [ ! -f ".env" ]; then
    warn "Fichier .env introuvable → copie depuis .env.example"
    cp .env.example .env
    warn "IMPORTANT : éditez docker/.env et changez les mots de passe avant de continuer."
    warn "Relancez ce script après modification."
    exit 0
fi
log "Fichier .env trouvé"

# Vérification que les valeurs par défaut ont été changées
if grep -qE "REMPLACER_PAR|changeme_" "$DOCKER_DIR/.env" 2>/dev/null; then
    err "Le fichier docker/.env contient encore des valeurs par défaut non modifiées.\nÉditez docker/.env et remplacez toutes les valeurs REMPLACER_PAR_... avant de continuer."
fi

# Démarrage des services
log "Démarrage des containers..."
docker compose up -d --pull always

# Attente de la disponibilité du backend
log "Attente du backend (max 60s)..."
for i in $(seq 1 12); do
    if curl -sf http://localhost:8000/api/schema/ &>/dev/null; then
        log "Backend prêt"
        break
    fi
    [ "$i" -eq 12 ] && err "Backend non disponible après 60s. Vérifiez avec : docker compose logs backend"
    sleep 5
done

# Attente du frontend
log "Attente du frontend (max 30s)..."
for i in $(seq 1 6); do
    if curl -sf http://localhost:3000 &>/dev/null; then
        log "Frontend prêt"
        break
    fi
    [ "$i" -eq 6 ] && err "Frontend non disponible après 30s. Vérifiez avec : docker compose logs frontend"
    sleep 5
done

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   CISO Assistant démarré avec succès !               ║"
echo "║                                                      ║"
echo "║   Interface :  http://localhost:3000                 ║"
echo "║   API :        http://localhost:8000/api/schema/     ║"
echo "║                                                      ║"
echo "║   Login : voir docker/.env (SUPERUSER_EMAIL)         ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
