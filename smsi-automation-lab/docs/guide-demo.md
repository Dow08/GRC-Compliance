# Guide de prise en main — TechShop SAS SMSI
**Version :** 2.0
**Date :** Juin 2026
**Auteur :** Dorian Poncelet (Consultant GRC)
**Statut :** Validé

---

## Vue d'ensemble du projet

Ce projet déploie un SMSI complet pour une PME e-commerce fictive (TechShop SAS) en utilisant
CISO Assistant comme plateforme GRC centrale. Il couvre ISO 27001:2022, NIS2, RGPD, EBIOS RM
et EU AI Act — avec une approche d'automatisation : les livrables sont générés par des scripts,
pas produits à la main.

---

## Lancer l'environnement

### Prérequis
- Docker Desktop installé et démarré
- Python 3.10+
- Git

### Démarrage en 3 commandes

```bash
# 1. Cloner le dépôt
git clone https://github.com/Dow08/CISO-GRC-automation-lab.git
cd CISO-GRC-automation-lab

# 2. Configurer l'environnement
cp docker/.env.example docker/.env
# Éditer docker/.env — remplacer toutes les valeurs REMPLACER_PAR_...

# 3. Lancer CISO Assistant
./scripts/deploy.sh
```

Interface : http://localhost:3000
API : http://localhost:8000/api/schema/

### Vérification de l'état des services

```bash
./scripts/check-health.sh
```

---

## Structure des livrables

### SMSI — Documents sources (Markdown)

| Dossier | Contenu |
|---|---|
| `smsi/01-politique/` | Politique de sécurité + Charte informatique |
| `smsi/02-perimetre/` | Déclaration du périmètre SMSI |
| `smsi/03-analyse-risques/` | Inventaire des actifs + Registre EBIOS RM (15 risques) |
| `smsi/04-declaration-applicabilite/` | SoA ISO 27001:2022 (93 contrôles) |
| `smsi/05-plan-traitement/` | Plan de traitement des risques + Procédure incidents |
| `smsi/06-controles-nis2-rgpd/` | Mapping NIS2 Article 21 + Tableau de bord RGPD |
| `smsi/07-indicateurs/` | KRI/KPI — Tableau de bord sécurité |
| `smsi/08-audit-interne/` | Programme d'audit interne sur 12 mois |
| `smsi/09-ai-gouvernance/` | Inventaire IA, mapping EU AI Act, politique usage IA |

### Livrables PDF

Les 15 documents SMSI sont disponibles en PDF dans `livrables-pdf/`.
Pour régénérer après modification des sources :

```bash
pip install reportlab pypdf
python scripts/generate_pdfs.py
```

---

## Scripts d'automatisation

### Rapport de conformité ISO 27001 (API CISO Assistant)

Interroge l'API CISO Assistant et génère un rapport Markdown complet :

```bash
export CISO_PASSWORD="votre_mot_de_passe"
python poc/api-automation/ciso_report.py --output rapport.md
```

Sortie :
```
[1/5] Connexion CISO Assistant...
[OK] Authentification reussie
[2/5] Recuperation des donnees...
[OK] 140 controles recuperes
[3/5] Analyse...
[OK] Score de conformite : 26.3%
[4/5] Generation du rapport...
[5/5] Sauvegarde...
[OK] Rapport genere : rapport.md
```

### Matrice de risques EBIOS RM

Génère heatmap ASCII + tableau des 18 risques + statistiques :

```bash
python poc/risk-matrix/risk_matrix.py --output matrice.md
```

### Alimentation CISO Assistant (scripts Django ORM)

Ces scripts s'exécutent à l'intérieur du container backend :

```bash
# Copier dans le container
docker cp scripts/fill_audit.py ciso_backend:/code/
docker cp scripts/fill_applied_controls.py ciso_backend:/code/
docker cp scripts/link_controls.py ciso_backend:/code/
docker cp scripts/remap_nist_csf.py ciso_backend:/code/

# Exécuter
docker exec ciso_backend sh -c "cd /code && .venv/bin/python fill_audit.py"
docker exec ciso_backend sh -c "cd /code && .venv/bin/python fill_applied_controls.py"
docker exec ciso_backend sh -c "cd /code && .venv/bin/python link_controls.py"
docker exec ciso_backend sh -c "cd /code && .venv/bin/python remap_nist_csf.py"
```

---

## POC d'automatisation

| POC | Dossier | Ce qu'il fait |
|---|---|---|
| Rapport conformité API | `poc/api-automation/` | Interroge CISO Assistant, génère rapport Markdown |
| Matrice de risques | `poc/risk-matrix/` | Génère heatmap + tableau EBIOS RM |
| Notification CNIL | `poc/cnil/` | Template procédure notification Art. 33 RGPD |
| Audit WPScan | `poc/wpscan/` | Rapport d'audit vulnérabilités WordPress |

---

## Frameworks et correspondances

### ISO 27001 ↔ EBIOS RM

Chaque risque du registre EBIOS RM (`smsi/03-analyse-risques/registre-risques.md`) référence
le ou les contrôles ISO 27001:2022 qui l'adressent. La SoA (`smsi/04-declaration-applicabilite/SoA-iso27001.md`)
référence en retour les risques couverts par chaque contrôle.

### ISO 27001 ↔ NIS2

Le mapping NIS2 Article 21 (`smsi/06-controles-nis2-rgpd/nis2-article21.md`) montre la
correspondance entre les 10 mesures NIS2 et les contrôles ISO 27001. Implémenter ISO 27001
couvre ~85% des obligations NIS2 pour TechShop.

### ISO 27001 ↔ EU AI Act

L'inventaire des systèmes IA (`smsi/09-ai-gouvernance/inventaire-systemes-ia.md`) et le
mapping EU AI Act (`smsi/09-ai-gouvernance/eu-ai-act-mapping.md`) montrent que les obligations
AI Act pour un déployeur PME s'intègrent naturellement dans le SMSI existant.

---

## Architecture de sécurité

Voir [`docs/architecture.md`](architecture.md) pour le détail complet :
- Architecture 5 couches (Cloudflare → Firewall → DMZ → Applicatif → Données)
- Segmentation VLAN (DMZ / Applicatif / Administration / Données / WiFi invités)
- Hub and Spoke VPN pour l'administration
- Matrice de flux et état du chiffrement par flux

---

## Contexte TechShop SAS

Voir [`organisation/contexte-pme.md`](../organisation/contexte-pme.md) pour le détail complet
de l'organisation fictive : infrastructure, données traitées, enjeux de conformité.

---

*Projet portfolio GRC Automation — Juin 2026*
