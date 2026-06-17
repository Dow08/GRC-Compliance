#!/usr/bin/env bash
# =============================================================
# check-health.sh — Vérification de l'état de CISO Assistant
# =============================================================
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[✓]${NC} $1"; }
fail() { echo -e "${RED}[✗]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║     CISO Assistant — Vérification de l'état         ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

ERRORS=0

# ── Containers ────────────────────────────────────────────────
echo "── Containers Docker ─────────────────────────────────"

for name in ciso_db ciso_backend ciso_frontend; do
    status=$(docker inspect --format='{{.State.Status}}' "$name" 2>/dev/null || echo "absent")
    if [ "$status" = "running" ]; then
        ok "$name → running"
    else
        fail "$name → $status"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "── Connectivité HTTP ─────────────────────────────────"

# Backend
if curl -sf --max-time 5 http://localhost:8000/api/schema/ &>/dev/null; then
    ok "Backend API     → http://localhost:8000/api/schema/"
else
    fail "Backend API     → non accessible"
    ERRORS=$((ERRORS + 1))
fi

# Frontend
if curl -sf --max-time 5 http://localhost:3000 &>/dev/null; then
    ok "Frontend        → http://localhost:3000"
else
    fail "Frontend        → non accessible"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "──────────────────────────────────────────────────────"
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}Tous les services sont opérationnels.${NC}"
    echo "Interface : http://localhost:3000"
else
    echo -e "${RED}$ERRORS service(s) en erreur. Consultez : docker compose logs${NC}"
fi
echo ""
