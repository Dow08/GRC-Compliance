#!/bin/bash
# =============================================================
# init-ciso.sh — Initialisation complète de CISO Assistant
# pour TechShop SAS
#
# Ce script s'assure que :
#   1. Le superuser admin existe avec le bon mot de passe
#   2. Le domaine TechShop SAS existe
#   3. Le user a les droits Admin sur Global ET TechShop SAS
#
# Usage : bash scripts/init-ciso.sh
# A relancer si tu recrées les containers depuis zéro.
# =============================================================

set -e

COMPOSE_FILE="$(dirname "$0")/../docker/docker-compose.yml"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   CISO Assistant — Init TechShop SAS         ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Vérifier que le backend tourne
if ! docker compose -f "$COMPOSE_FILE" ps | grep -q "ciso_backend.*healthy"; then
  echo "[ERREUR] Le backend n'est pas démarré ou pas healthy."
  echo "Lance d'abord : bash scripts/deploy.sh"
  exit 1
fi

echo "[1/3] Création/vérification du superuser..."
docker exec ciso_backend sh -c "poetry run python manage.py shell -c \"
from iam.models import Folder, User, RoleAssignment, Role

# Récupérer le dossier Global
global_folder = Folder.objects.filter(content_type='GL').first()
if not global_folder:
    print('  ERREUR: dossier Global introuvable')
    exit(1)

# Créer ou mettre à jour le superuser
email = 'admin@techshop.fr'
pwd = 'changeme_motdepasse_admin'
u, created = User.objects.get_or_create(
    email=email,
    defaults={
        'is_superuser': True,
        'is_active': True,
        'folder': global_folder
    }
)
u.set_password(pwd)
u.is_superuser = True
u.is_active = True
u.save()
print('  Superuser ' + email + ': ' + ('cree' if created else 'mis a jour'))
\"" 2>&1 | grep -v "objects imported"

echo "[2/3] Création/vérification du domaine TechShop SAS..."
docker exec ciso_backend sh -c "poetry run python manage.py shell -c \"
from iam.models import Folder

global_folder = Folder.objects.filter(content_type='GL').first()
domain, created = Folder.objects.get_or_create(
    name='TechShop SAS',
    defaults={
        'content_type': 'DO',
        'parent_folder': global_folder,
        'description': 'PME e-commerce gaming et electronique - Toulouse. CA 3.2M EUR, 47 salaries, 15000 clients.'
    }
)
print('  Domaine TechShop SAS (id=' + str(domain.id) + '): ' + ('cree' if created else 'existait deja'))
\"" 2>&1 | grep -v "objects imported"

echo "[3/3] Attribution des permissions Admin..."
docker exec ciso_backend sh -c "poetry run python manage.py shell -c \"
from iam.models import Folder, User, RoleAssignment, Role

user = User.objects.get(email='admin@techshop.fr')
admin_role = Role.objects.get(name='BI-RL-ADM')
folders = Folder.objects.all()

for folder in folders:
    ra, created = RoleAssignment.objects.get_or_create(
        user=user,
        role=admin_role,
        folder=folder,
        defaults={'is_recursive': True}
    )
    if not ra.is_recursive:
        ra.is_recursive = True
        ra.save()
    status = 'cree' if created else 'existait'
    print(f'  Admin sur [{folder.name}] ({folder.content_type}): {status}')
\"" 2>&1 | grep -v "objects imported"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   Initialisation terminee !                  ║"
echo "║                                              ║"
echo "║   URL     : http://localhost:3000            ║"
echo "║   Email   : admin@techshop.fr               ║"
echo "║   Mdp     : changeme_motdepasse_admin        ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "IMPORTANT : Change le mot de passe en production !"
echo ""
