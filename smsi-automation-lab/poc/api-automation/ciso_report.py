#!/usr/bin/env python3
"""
CISO Assistant — Générateur automatique de rapport de conformité
TechShop SAS | POC GRC Automation

Ce script interroge l'API CISO Assistant et génère un rapport
de conformité ISO 27001 prêt pour présentation au CODIR.

Usage:
    python ciso_report.py
    python ciso_report.py --output rapport-juin-2026.md

Auteur: Dorian Poncelet
Auteur: Dorian Poncelet — Consultant GRC
"""

import os
import requests
import json
import argparse
from datetime import datetime
from collections import defaultdict

# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "http://localhost:8000/api"
EMAIL = os.environ.get("CISO_EMAIL", "admin@techshop.fr")
PASSWORD = os.environ.get("CISO_PASSWORD", "")
AUDIT_NAME = "Audit ISO 27001:2022 — TechShop SAS"

if not PASSWORD:
    import sys
    print("[ERREUR] Variable d'environnement CISO_PASSWORD non definie.")
    print("  Export: export CISO_PASSWORD='votre_mot_de_passe'")
    sys.exit(1)


# ============================================================
# AUTHENTIFICATION
# ============================================================

def get_token(base_url, email, password):
    """
    Récupère un token d'authentification via l'API CISO Assistant.

    Pourquoi un token ?
    L'API utilise l'authentification par token (Token-based Auth).
    Chaque requête doit inclure le header : Authorization: Token <token>
    C'est plus sécurisé que d'envoyer email/mdp à chaque requête.
    """
    response = requests.post(
        f"{base_url}/iam/login/",
        json={"username": email, "password": password},
        timeout=10
    )
    if response.status_code == 200:
        token = response.json().get("token")
        print(f"[OK] Authentification reussie")
        return token
    else:
        raise Exception(f"❌ Echec authentification: {response.status_code}")


def get_headers(token):
    """Retourne les headers HTTP avec le token d'auth."""
    return {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }


# ============================================================
# RÉCUPÉRATION DES DONNÉES
# ============================================================

def get_audit(base_url, headers, audit_name):
    """
    Récupère l'audit ISO 27001 de TechShop SAS.

    L'API retourne une liste paginée d'audits.
    On filtre par nom pour trouver le bon.
    """
    response = requests.get(
        f"{base_url}/compliance-assessments/?limit=50",
        headers=headers,
        timeout=10
    )
    audits = response.json().get("results", [])

    for audit in audits:
        if audit_name in audit.get("name", ""):
            print(f"[OK] Audit trouve: {audit['name']}")
            return audit

    raise Exception(f"❌ Audit '{audit_name}' non trouvé")


def get_requirement_assessments(base_url, headers, audit_id):
    """
    Récupère tous les contrôles évalués de l'audit.

    Chaque RequirementAssessment = 1 contrôle ISO 27001 évalué.
    On récupère jusqu'à 200 résultats (il y en a 140 pour ISO 27001).
    """
    response = requests.get(
        f"{base_url}/requirement-assessments/?compliance_assessment={audit_id}&limit=200",
        headers=headers,
        timeout=15
    )
    results = response.json().get("results", [])
    print(f"[OK] {len(results)} controles recuperes")
    return results


def get_applied_controls(base_url, headers):
    """
    Récupère les mesures du plan d'action TechShop SAS.
    Permet de calculer le budget et les priorités.
    """
    response = requests.get(
        f"{base_url}/applied-controls/?limit=200",
        headers=headers,
        timeout=15
    )
    results = response.json().get("results", [])
    print(f"[OK] {len(results)} mesures du plan d'action recuperees")
    return results


# ============================================================
# ANALYSE DES DONNÉES
# ============================================================

def analyze_compliance(requirements):
    """
    Analyse les résultats de conformité.

    Les résultats possibles dans CISO Assistant :
    - compliant         → Conforme
    - partially_compliant → Partiellement conforme
    - non_compliant     → Non conforme
    - not_assessed      → Non évalué
    """
    stats = {
        "total": 0,
        "compliant": 0,
        "partially_compliant": 0,
        "non_compliant": 0,
        "not_assessed": 0,
        "by_theme": defaultdict(lambda: {
            "compliant": 0,
            "partially_compliant": 0,
            "non_compliant": 0,
            "not_assessed": 0,
            "total": 0
        })
    }

    critical_nonconformities = []

    for req in requirements:
        # On ne compte que les contrôles feuilles (pas les sections parentes)
        requirement = req.get("requirement")
        if not requirement or not requirement.get("ref_id"):
            continue

        ref_id = requirement.get("ref_id", "")
        result = req.get("result", "not_assessed")
        extended = req.get("extended_result", "")

        # Déterminer le thème (A.5, A.6, A.7, A.8)
        theme = "Clauses"
        if ref_id.startswith("A.5"):
            theme = "A.5 - Organisationnels"
        elif ref_id.startswith("A.6"):
            theme = "A.6 - Personnes"
        elif ref_id.startswith("A.7"):
            theme = "A.7 - Physiques"
        elif ref_id.startswith("A.8"):
            theme = "A.8 - Technologiques"

        # Comptage global
        stats["total"] += 1
        stats[result] = stats.get(result, 0) + 1

        # Comptage par thème
        stats["by_theme"][theme]["total"] += 1
        stats["by_theme"][theme][result] = \
            stats["by_theme"][theme].get(result, 0) + 1

        # Identifier les non-conformités majeures
        if extended == "major_non_conformity":
            critical_nonconformities.append({
                "ref_id": ref_id,
                "name": requirement.get("name", ""),
                "observation": req.get("observation", "")
            })

    # Calcul du score global
    if stats["total"] > 0:
        evaluated = stats["total"] - stats.get("not_assessed", 0)
        if evaluated > 0:
            score = (
                stats["compliant"] * 100 +
                stats["partially_compliant"] * 50
            ) / (evaluated * 100) * 100
        else:
            score = 0
    else:
        score = 0

    stats["score"] = round(score, 1)
    stats["critical_nonconformities"] = critical_nonconformities

    return stats


def analyze_budget(controls):
    """
    Analyse le budget du plan d'action.

    Calcule le budget total et par priorité
    à partir des mesures appliquées.

    Structure du champ cost dans CISO Assistant :
    {
      "build": {"fixed_cost": 500, "people_days": 3},
      "run":   {"fixed_cost": 600, "people_days": 2},
      "amortization_period": 3
    }
    """
    budget = {
        "total_build": 0,
        "total_run": 0,
        "by_priority": {1: 0, 2: 0, 3: 0, 4: 0},
        "p1_count": 0,
        "p2_count": 0,
        "p3_count": 0,
        "p4_count": 0,
        "in_progress": 0,
        "to_do": 0,
        "done": 0
    }

    for control in controls:
        cost_data = control.get("cost") or {}
        if isinstance(cost_data, dict):
            build_cost = cost_data.get("build", {}).get("fixed_cost", 0) or 0
            run_cost = cost_data.get("run", {}).get("fixed_cost", 0) or 0
        else:
            build_cost = 0
            run_cost = 0

        cost = build_cost
        priority = control.get("priority") or 4
        status = control.get("status", "to_do")

        budget["total_run"] += run_cost

        budget["total_build"] += cost

        if priority in budget["by_priority"]:
            budget["by_priority"][priority] += cost

        budget[f"p{priority}_count"] = budget.get(f"p{priority}_count", 0) + 1

        if status == "in_progress":
            budget["in_progress"] += 1
        elif status == "to_do":
            budget["to_do"] += 1
        elif status in ["active", "ok"]:
            budget["done"] += 1

    return budget


# ============================================================
# GÉNÉRATION DU RAPPORT
# ============================================================

def generate_report(audit, stats, budget):
    """
    Génère le rapport Markdown de conformité.

    Ce rapport est conçu pour être présenté au CODIR de TechShop SAS.
    Il doit être compréhensible par Marie Laurent (DG) qui n'est
    pas technique — pas de jargon, des chiffres clairs, des actions.
    """

    now = datetime.now().strftime("%d/%m/%Y à %Hh%M")
    score = stats["score"]

    # Indicateur visuel du score
    if score >= 80:
        score_indicator = "🟢"
        score_label = "BON"
    elif score >= 50:
        score_indicator = "🟡"
        score_label = "À AMÉLIORER"
    else:
        score_indicator = "🔴"
        score_label = "INSUFFISANT"

    report = f"""# Tableau de Bord Conformité ISO 27001:2022
## TechShop SAS — Rapport automatisé
**Généré le :** {now}
**Source :** CISO Assistant API
**Audit :** {audit.get('name', 'N/A')}
**Périmètre :** SMSI TechShop SAS

---

## 🎯 Score Global de Conformité

```
{score_indicator} {score}% — {score_label}
{"█" * int(score // 5)}{"░" * (20 - int(score // 5))} {score}%
```

> **Objectif certification ISO 27001 :** 80% d'ici décembre 2026
> **Écart actuel :** {max(0, 80 - score):.1f} points à gagner

---

## 📊 Répartition des {stats['total']} contrôles évalués

| Statut | Nombre | Pourcentage | Signification |
|---|---|---|---|
| ✅ Conformes | {stats.get('compliant', 0)} | {stats.get('compliant', 0) / max(stats['total'], 1) * 100:.1f}% | Contrôle pleinement appliqué |
| 🟡 Partiellement conformes | {stats.get('partially_compliant', 0)} | {stats.get('partially_compliant', 0) / max(stats['total'], 1) * 100:.1f}% | En cours d'implémentation |
| 🔴 Non conformes | {stats.get('non_compliant', 0)} | {stats.get('non_compliant', 0) / max(stats['total'], 1) * 100:.1f}% | Action requise |
| ⬜ Non évalués | {stats.get('not_assessed', 0)} | {stats.get('not_assessed', 0) / max(stats['total'], 1) * 100:.1f}% | À évaluer |

---

## 📋 Conformité par thème ISO 27001

"""

    theme_labels = {
        "A.5 - Organisationnels": "37 contrôles — Politiques, processus, gouvernance",
        "A.6 - Personnes": "8 contrôles — RH, formation, sensibilisation",
        "A.7 - Physiques": "14 contrôles — Locaux, matériels, accès physiques",
        "A.8 - Technologiques": "34 contrôles — SI, réseau, chiffrement, développement"
    }

    for theme, data in stats["by_theme"].items():
        if theme == "Clauses":
            continue
        total = data.get("total", 0)
        if total == 0:
            continue

        compliant = data.get("compliant", 0)
        partial = data.get("partially_compliant", 0)
        non_c = data.get("non_compliant", 0)

        theme_score = (compliant * 100 + partial * 50) / (total * 100) * 100
        bar = "█" * int(theme_score // 10) + "░" * (10 - int(theme_score // 10))

        desc = theme_labels.get(theme, "")
        report += f"""### {theme}
> {desc}

| Conformes | Partiels | Non conformes | Score |
|---|---|---|---|
| {compliant} | {partial} | {non_c} | {theme_score:.1f}% |

`{bar}` {theme_score:.1f}%

"""

    # Non-conformités majeures
    report += "---\n\n## 🚨 Non-conformités majeures (action immédiate requise)\n\n"

    if stats["critical_nonconformities"]:
        for nc in stats["critical_nonconformities"]:
            report += f"### ❌ {nc['ref_id']} — {nc['name']}\n"
            if nc['observation']:
                report += f"> {nc['observation'][:200]}...\n\n"
    else:
        report += "> ✅ Aucune non-conformité majeure identifiée.\n\n"

    # Budget
    report += f"""---

## 💰 Budget Plan d'Action

| Priorité | Actions | Budget estimé | Délai recommandé |
|---|---|---|---|
| 🔴 P1 — Critique | {budget.get('p1_count', 0)} actions | {budget['by_priority'].get(1, 0):,}€ | < 1 mois |
| 🟠 P2 — Haute | {budget.get('p2_count', 0)} actions | {budget['by_priority'].get(2, 0):,}€ | < 3 mois |
| 🟡 P3 — Moyenne | {budget.get('p3_count', 0)} actions | {budget['by_priority'].get(3, 0):,}€ | < 6 mois |
| 🔵 P4 — Faible | {budget.get('p4_count', 0)} actions | {budget['by_priority'].get(4, 0):,}€ | < 12 mois |
| **TOTAL** | **{budget.get('p1_count',0) + budget.get('p2_count',0) + budget.get('p3_count',0) + budget.get('p4_count',0)} actions** | **{budget['total_build']:,}€** | **12 mois** |

### Avancement du plan d'action

| Statut | Nombre |
|---|---|
| ✅ Terminées | {budget.get('done', 0)} |
| 🔄 En cours | {budget.get('in_progress', 0)} |
| ⏳ À faire | {budget.get('to_do', 0)} |

---

## 📅 Prochaines étapes recommandées

1. **Semaine 1** → Activer MFA sur tous les comptes admin (0€ — 1 jour)
2. **Semaine 2** → Désactiver XML-RPC + mettre à jour WooCommerce (400€)
3. **Mois 1** → Former les 47 employés à la sécurité (1 500€)
4. **Mois 2** → Déployer Bitwarden gestionnaire de mots de passe (300€)
5. **Mois 3** → Mettre en place le plan de réponse aux incidents (0€)

---

## ℹ️ À propos de ce rapport

Ce rapport est généré automatiquement via l'API CISO Assistant.
Il est mis à jour en temps réel à chaque exécution du script.

**Pour régénérer ce rapport :**
```bash
python ciso_report.py --output rapport-$(date +%Y-%m-%d).md
```

*Rapport généré par le script d'automatisation GRC — TechShop SAS*
*Source des données : CISO Assistant Community Edition*
"""

    return report


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Générateur de rapport de conformité ISO 27001 — TechShop SAS"
    )
    parser.add_argument(
        "--output",
        default=f"rapport-conformite-{datetime.now().strftime('%Y-%m-%d')}.md",
        help="Fichier de sortie (défaut: rapport-conformite-YYYY-MM-DD.md)"
    )
    parser.add_argument(
        "--url",
        default=BASE_URL,
        help=f"URL de l'API CISO Assistant (défaut: {BASE_URL})"
    )
    args = parser.parse_args()

    print("\n" + "="*50)
    print("  CISO Assistant - Rapport de Conformite")
    print("  TechShop SAS | ISO 27001:2022")
    print("="*50 + "\n")

    # Etape 1 : Authentification
    print("[1/5] Connexion a CISO Assistant...")
    token = get_token(args.url, EMAIL, PASSWORD)
    headers = get_headers(token)

    # Etape 2 : Recuperation des donnees
    print("\n[2/5] Recuperation des donnees...")
    audit = get_audit(args.url, headers, AUDIT_NAME)
    requirements = get_requirement_assessments(args.url, headers, audit["id"])
    controls = get_applied_controls(args.url, headers)

    # Etape 3 : Analyse
    print("\n[3/5] Analyse des resultats...")
    stats = analyze_compliance(requirements)
    budget = analyze_budget(controls)

    print(f"\n[OK] Score de conformite : {stats['score']}%")
    print(f"     Conformes : {stats.get('compliant', 0)}")
    print(f"     Partiels  : {stats.get('partially_compliant', 0)}")
    print(f"     Non conf. : {stats.get('non_compliant', 0)}")
    print(f"     Budget build total : {budget['total_build']:,} EUR")
    print(f"     Budget run annuel  : {budget['total_run']:,} EUR/an")

    # Etape 4 : Generation du rapport
    print(f"\n[4/5] Generation du rapport...")
    report = generate_report(audit, stats, budget)

    # Etape 5 : Sauvegarde
    print(f"\n[5/5] Sauvegarde...")
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n[OK] Rapport genere : {args.output}")
    print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    main()
