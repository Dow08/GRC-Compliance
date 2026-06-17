# GRC & AI Governance — SMSI Automatisé — TechShop SAS
### Portfolio Project | ISO 27001 · NIS2 · RGPD · EU AI Act · GRC Automation

**Auteur :** Dorian Poncelet — GRC Automation + AI Governance

> Déploiement complet d'un SMSI pour une PME e-commerce fictive (47 salariés, 3,2M€ CA)
> en utilisant CISO Assistant comme plateforme GRC open source centrale.
> L'objectif n'est pas de cocher des cases — c'est de montrer qu'on comprend pourquoi elles existent.

---

## Par où commencer ?

**Tu as 5 minutes →** [`docs/guide-demo.md`](docs/guide-demo.md) — script de démo recruteur, étape par étape.

**Tu veux lire un livrable →** [`livrables-pdf/`](livrables-pdf/) — 12 documents SMSI en PDF, prêts à l'emploi.

**Tu veux voir le code →** [`poc/api-automation/ciso_report.py`](poc/api-automation/ciso_report.py) — une commande génère un rapport de conformité depuis l'API.

**Tu cherches l'AI Governance →** [`smsi/09-ai-gouvernance/`](smsi/09-ai-gouvernance/) — inventaire IA, mapping EU AI Act, politique d'usage.

---

## Ce que ce projet démontre

| Compétence | Preuve concrète |
|---|---|
| Déployer une plateforme GRC | `docker/docker-compose.yml` — CISO Assistant en 3 commandes |
| ISO 27001:2022 — les 93 contrôles | `smsi/04-declaration-applicabilite/SoA-iso27001.md` — SoA complète avec justifications |
| Analyse de risques EBIOS RM | `smsi/03-analyse-risques/registre-risques.md` — 15 risques, cotation brute + résiduelle |
| NIS2 Article 21 — 10 mesures | `smsi/06-controles-nis2-rgpd/nis2-article21.md` — mapping + état de conformité |
| RGPD — registre des traitements | `smsi/06-controles-nis2-rgpd/rgpd-conformite.md` — 5 traitements + transferts hors UE |
| **EU AI Act — déployeur PME** | `smsi/09-ai-gouvernance/eu-ai-act-mapping.md` — analyse par article, plan de conformité |
| **Inventaire systèmes IA** | `smsi/09-ai-gouvernance/inventaire-systemes-ia.md` — 5 systèmes analysés (Stripe, HubSpot...) |
| Automatisation GRC (Python + API) | `poc/api-automation/ciso_report.py` — rapport conformité en 5 secondes |
| Tableau de bord CODIR | `smsi/07-indicateurs/kri-kpi-tableau-bord.md` — 8 KRI + 6 KPI avec seuils |

---

## Quick Start

```bash
# 1. Cloner le dépôt
git clone https://github.com/Dow08/CISO-GRC-automation-lab.git
cd CISO-GRC-automation-lab

# 2. Configurer l'environnement
cp docker/.env.example docker/.env
# Éditer docker/.env et remplacer les valeurs REMPLACER_PAR_...

# 3. Lancer CISO Assistant
./scripts/deploy.sh

# 4. Générer un rapport de conformité automatiquement
export CISO_PASSWORD="votre_mot_de_passe"
python poc/api-automation/ciso_report.py --output rapport-demo.md
```

Interface CISO Assistant : http://localhost:3000

---

## Frameworks couverts

| Référentiel | Couverture | Livrable principal |
|---|---|---|
| **ISO 27001:2022** | 93 contrôles Annex A | SoA + plan d'audit + KPI |
| **NIS2 (2022/2555)** | Article 21 complet | Mapping + 10 mesures évaluées |
| **RGPD (2016/679)** | Art. 5, 13, 28, 30, 32, 33, 46 | Registre traitements + transferts hors UE |
| **EBIOS RM (ANSSI 2018)** | Ateliers 1, 3, 5 | 15 risques + risque résiduel accepté DG |
| **EU AI Act (2024/1689)** | Obligations déployeur | Inventaire 5 systèmes IA + plan conformité |

---

## Chiffres clés

```
SMSI
  Actifs inventoriés     : 26   (4 types, 4 niveaux de classification)
  Risques EBIOS RM       : 15   (criticité brute + résiduelle + décision direction)
  Contrôles ISO 27001    : 93   (84 applicables, 9 exclus avec justification)
  Mesures plan traitement: 12   (budget estimé : 9 000 – 12 000 € / an)

AI GOVERNANCE
  Systèmes IA inventoriés: 5    (Stripe Radar, HubSpot, WooCommerce, GA4, GWorkspace)
  Systèmes à risque limité: 1   (Stripe — décision automatisée sur paiement)
  Conformité EU AI Act   : 40%  (obligations déployeur, actions Q3 2026)

AUTOMATION
  Scripts Python         : 8    (API, risques, audit, controls, CSF, PDF...)
  Rapport généré en      : 5s   (vs 30 min de clics dans l'interface)
  PDF livrables          : 12   (régénérables : python scripts/generate_pdfs.py)
```

---

## L'automatisation en action

```bash
# Rapport de conformité ISO 27001 depuis l'API CISO Assistant
python poc/api-automation/ciso_report.py --output rapport-lundi.md
# → 5 secondes. Score global, répartition par thème, budget. Prêt CODIR.

# Matrice de risques EBIOS RM
python poc/risk-matrix/risk_matrix.py --output matrice-juin.md
# → 18 risques analysés. Heatmap. Stats. Aucune saisie manuelle.

# Régénérer les 12 livrables PDF
python scripts/generate_pdfs.py
# → 12 PDF en quelques secondes depuis les sources Markdown.
```

---

## Livrables PDF

12 documents SMSI disponibles dans [`livrables-pdf/`](livrables-pdf/) :

| # | Document | Pages |
|---|---|:---:|
| 01 | Politique de sécurité de l'information | 5 |
| 02 | Charte informatique utilisateur | 4 |
| 03 | Déclaration du périmètre SMSI | 5 |
| 04 | Inventaire des actifs informationnels | 6 |
| 05 | Registre des risques EBIOS RM | 16 |
| 06 | Statement of Applicability ISO 27001:2022 | 14 |
| 07 | Plan de traitement des risques | 10 |
| 08 | Procédure de gestion des incidents | 7 |
| 09 | Mapping NIS2 Article 21 | 8 |
| 10 | Tableau de bord RGPD | 9 |
| 11 | KRI/KPI — Tableau de bord sécurité | 9 |
| 12 | Plan d'audit interne | 9 |
| 13 | Inventaire des systèmes IA | 6 |
| 14 | Mapping EU AI Act | 8 |
| 15 | Politique IA responsable | 5 |

---

## Structure du projet

```
labs-ciso-grc/
├── docker/              Infrastructure CISO Assistant (docker-compose, .env)
├── scripts/             Automatisation (deploy, audit, controls, PDF, CSF...)
├── smsi/                15 documents SMSI
│   ├── 01-politique/    Politique sécurité + Charte informatique
│   ├── 02-perimetre/    Déclaration périmètre ISO 27001
│   ├── 03-analyse-risques/  Inventaire actifs + Registre EBIOS RM
│   ├── 04-declaration-applicabilite/  SoA ISO 27001 (93 contrôles)
│   ├── 05-plan-traitement/  PTR + Procédure incidents
│   ├── 06-controles-nis2-rgpd/  NIS2 + RGPD
│   ├── 07-indicateurs/  KRI/KPI
│   ├── 08-audit-interne/ Programme audit
│   └── 09-ai-gouvernance/  EU AI Act + Inventaire IA + Politique IA  ← nouveau
├── livrables-pdf/       12 livrables PDF professionnels
├── poc/                 4 POC GRC Automation (API, CNIL, risques, WPScan)
├── organisation/        Fiche TechShop SAS
├── docs/                Architecture + Guide démo 5 min
└── screenshots/         13 captures CISO Assistant en action
```

---

## Screenshots CISO Assistant

| Capture | Ce qu'elle montre |
|---|---|
| `01-dashboard-synthese-radar-nist.png` | Dashboard principal + radar NIST CSF |
| `02-distribution-mesures-nist-csf.png` | Distribution Govern/Protect/Recover/Identify |
| `03-statistiques-gouvernance-4-referentiels.png` | 4 référentiels, 130 mesures |
| `04-conformite-globale-iso27001-techshop.png` | Score 24.4% / 36.6% / 37.4% |
| `05-poc-risk-matrix-18-risques-terminal.png` | Automatisation matrice risques |
| `06-poc-ciso-report-api-automation-terminal.png` | Rapport API en 5 étapes |

---

## Auteur

**Dorian Poncelet**
Ancien dirigeant d'entreprise —  cybersécurité

Spécialisation visée : **GRC Automation · AI Governance · ISO 27001 · EU AI Act**

- LinkedIn : [linkedin.com/in/dorian-p-1807612b5](https://www.linkedin.com/in/dorian-p-1807612b5)

---

*Projet perso — Juin 2026 — Organisation fictive à des fins pédagogiques*
*Ce projet démontre une méthode, pas un déploiement en production.*
