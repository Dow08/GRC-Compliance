#!/usr/bin/env python3
"""
risk_matrix.py — Générateur de matrice de risques TechShop SAS
Usage: python risk_matrix.py [--output rapport-risques.md] [--html]
"""

import argparse
from datetime import date

# Registre des risques TechShop SAS (EBIOS RM simplifié)
RISKS = [
    {"id": "R01", "actif": "Serveurs OVH (WooCommerce)", "menace": "Ransomware", "vraisemblance": 3, "impact": 4, "traitement": "Réduire", "controle": "A.8.13"},
    {"id": "R02", "actif": "Base données clients", "menace": "Fuite de données (breach RGPD)", "vraisemblance": 3, "impact": 4, "traitement": "Réduire", "controle": "A.8.11"},
    {"id": "R03", "actif": "Google Workspace Admin", "menace": "Compromission compte (MFA absent)", "vraisemblance": 4, "impact": 3, "traitement": "Réduire", "controle": "A.8.5"},
    {"id": "R04", "actif": "Stripe (paiement)", "menace": "Indisponibilité fournisseur critique", "vraisemblance": 2, "impact": 4, "traitement": "Transférer", "controle": "A.5.19"},
    {"id": "R05", "actif": "ERP Odoo", "menace": "Accès non autorisé (ex-employé)", "vraisemblance": 3, "impact": 3, "traitement": "Réduire", "controle": "A.5.18"},
    {"id": "R06", "actif": "Site WooCommerce", "menace": "Injection SQL", "vraisemblance": 3, "impact": 3, "traitement": "Réduire", "controle": "A.8.28"},
    {"id": "R07", "actif": "AWS S3 (backup)", "menace": "Non-conformité RGPD (transfert us-east-1)", "vraisemblance": 4, "impact": 3, "traitement": "Réduire", "controle": "A.5.33"},
    {"id": "R08", "actif": "Infrastructure OVH", "menace": "Panne matérielle majeure", "vraisemblance": 2, "impact": 3, "traitement": "Réduire", "controle": "A.8.14"},
    {"id": "R09", "actif": "Réseau interne", "menace": "Intrusion réseau (WiFi non segmenté)", "vraisemblance": 3, "impact": 2, "traitement": "Réduire", "controle": "A.8.20"},
    {"id": "R10", "actif": "Postes de travail", "menace": "Malware via phishing", "vraisemblance": 4, "impact": 2, "traitement": "Réduire", "controle": "A.8.7"},
    {"id": "R11", "actif": "Sauvegardes AWS S3", "menace": "Sauvegarde corrompue / non testée", "vraisemblance": 2, "impact": 4, "traitement": "Réduire", "controle": "A.8.13"},
    {"id": "R12", "actif": "Données RH", "menace": "Accès non autorisé aux données RH", "vraisemblance": 2, "impact": 3, "traitement": "Réduire", "controle": "A.5.34"},
    {"id": "R13", "actif": "VPN WireGuard", "menace": "Configuration VPN défaillante", "vraisemblance": 2, "impact": 3, "traitement": "Réduire", "controle": "A.8.20"},
    {"id": "R14", "actif": "Cloudflare WAF", "menace": "Contournement WAF (règles obsolètes)", "vraisemblance": 2, "impact": 3, "traitement": "Réduire", "controle": "A.8.22"},
    {"id": "R15", "actif": "Google Workspace", "menace": "Perte de données (suppression accidentelle)", "vraisemblance": 2, "impact": 2, "traitement": "Accepter", "controle": "A.8.13"},
    {"id": "R16", "actif": "HubSpot CRM", "menace": "Exfiltration données prospects", "vraisemblance": 2, "impact": 2, "traitement": "Surveiller", "controle": "A.5.19"},
    {"id": "R17", "actif": "Compte admin Odoo", "menace": "Élévation de privilèges", "vraisemblance": 2, "impact": 3, "traitement": "Réduire", "controle": "A.8.2"},
    {"id": "R18", "actif": "Site WooCommerce", "menace": "Défacement (plugin vulnérable)", "vraisemblance": 3, "impact": 2, "traitement": "Réduire", "controle": "A.8.8"},
]

CRITICITE_LABELS = {
    (1, 4): "Faible", (2, 3): "Faible", (3, 2): "Faible", (4, 1): "Faible",
    (1, 1): "Faible", (1, 2): "Faible", (2, 1): "Faible", (2, 2): "Faible",
}

def get_criticite_level(score):
    if score <= 4:
        return "FAIBLE", "🟢"
    elif score <= 8:
        return "MODÉRÉ", "🟡"
    elif score <= 12:
        return "ÉLEVÉ", "🟠"
    else:
        return "CRITIQUE", "🔴"

def build_heatmap_ascii():
    """Génère la heatmap ASCII 4x4."""
    grid = [[[] for _ in range(4)] for _ in range(4)]
    for r in RISKS:
        v = r["vraisemblance"] - 1
        i = r["impact"] - 1
        grid[3 - i][v].append(r["id"])

    lines = []
    lines.append("```")
    lines.append("MATRICE DE RISQUES — TechShop SAS (Vraisemblance × Impact)")
    lines.append("")
    lines.append("IMPACT         │  V=1 Très faible  │  V=2 Faible  │  V=3 Élevée  │  V=4 Très élevée  │")
    lines.append("───────────────┼───────────────────┼──────────────┼──────────────┼───────────────────┤")

    impact_labels = ["I=4 Critique  ", "I=3 Grave     ", "I=2 Significatif", "I=1 Faible    "]
    zone_colors = {
        (3, 0): "🟠", (3, 1): "🔴", (3, 2): "🔴", (3, 3): "🔴",
        (2, 0): "🟡", (2, 1): "🟠", (2, 2): "🔴", (2, 3): "🔴",
        (1, 0): "🟢", (1, 1): "🟡", (1, 2): "🟠", (1, 3): "🟠",
        (0, 0): "🟢", (0, 1): "🟢", (0, 2): "🟡", (0, 3): "🟡",
    }

    for row_idx in range(4):
        impact_row = 3 - row_idx
        label = impact_labels[row_idx]
        cells = []
        for col_idx in range(4):
            ids = grid[row_idx][col_idx]
            zone = zone_colors.get((impact_row, col_idx), "⬜")
            cell_content = zone + " " + ",".join(ids) if ids else zone + "      "
            cells.append(f" {cell_content:<16}")
        lines.append(f" {label} │{'│'.join(cells)}│")
        lines.append("───────────────┼───────────────────┼──────────────┼──────────────┼───────────────────┤")

    lines.append("```")
    lines.append("")
    lines.append("**Légende :** 🔴 Critique (>12) | 🟠 Élevé (9-12) | 🟡 Modéré (5-8) | 🟢 Faible (1-4)")
    return "\n".join(lines)

def build_risk_table():
    """Génère le tableau détaillé des risques."""
    lines = []
    lines.append("| ID | Actif | Menace | V | I | **Score** | Niveau | Traitement | Contrôle ISO |")
    lines.append("|---|---|---|:---:|:---:|:---:|---|---|---|")
    for r in RISKS:
        score = r["vraisemblance"] * r["impact"]
        level, emoji = get_criticite_level(score)
        lines.append(f"| {r['id']} | {r['actif']} | {r['menace']} | {r['vraisemblance']} | {r['impact']} | **{score}** | {emoji} {level} | {r['traitement']} | {r['controle']} |")
    return "\n".join(lines)

def build_stats():
    """Calcule les statistiques du registre."""
    scores = [r["vraisemblance"] * r["impact"] for r in RISKS]
    critique = sum(1 for s in scores if s > 12)
    eleve = sum(1 for s in scores if 9 <= s <= 12)
    modere = sum(1 for s in scores if 5 <= s <= 8)
    faible = sum(1 for s in scores if s <= 4)

    traitements = {}
    for r in RISKS:
        t = r["traitement"]
        traitements[t] = traitements.get(t, 0) + 1

    lines = []
    lines.append("| Niveau | Nombre | % | Action |")
    lines.append("|---|:---:|:---:|---|")
    total = len(RISKS)
    lines.append(f"| 🔴 Critique (>12) | {critique} | {critique/total*100:.0f}% | Traitement immédiat |")
    lines.append(f"| 🟠 Élevé (9-12) | {eleve} | {eleve/total*100:.0f}% | Plan de traitement prioritaire |")
    lines.append(f"| 🟡 Modéré (5-8) | {modere} | {modere/total*100:.0f}% | Surveillance renforcée |")
    lines.append(f"| 🟢 Faible (1-4) | {faible} | {faible/total*100:.0f}% | Acceptation / surveillance |")
    lines.append("")
    lines.append("**Répartition par traitement :**")
    lines.append("")
    lines.append("| Stratégie | Nombre |")
    lines.append("|---|:---:|")
    for t, n in sorted(traitements.items()):
        lines.append(f"| {t} | {n} |")
    return "\n".join(lines)

def generate_report(output_path):
    today = date.today().strftime("%d/%m/%Y")
    scores = [r["vraisemblance"] * r["impact"] for r in RISKS]
    critique = sum(1 for s in scores if s > 12)
    eleve = sum(1 for s in scores if 9 <= s <= 12)
    score_moyen = sum(scores) / len(scores)
    top_risks = sorted(RISKS, key=lambda r: r["vraisemblance"] * r["impact"], reverse=True)[:3]

    content = f"""# Matrice de Risques — TechShop SAS
**Version :** 2.0
**Date :** {today}
**Méthode :** EBIOS RM simplifié — ISO 27005
**Auteur :** Dorian Poncelet (Consultant GRC)
**Généré par :** risk_matrix.py

---

## Synthèse exécutive

> **TechShop SAS présente {critique} risques critiques et {eleve} risques élevés** nécessitant un plan de traitement
> prioritaire. Le score de risque moyen est de **{score_moyen:.1f}/16**. Les vecteurs d'attaque
> les plus probables sont : ransomware sur l'infrastructure OVH, fuite de données RGPD,
> et compromission des comptes d'administration Google Workspace.

### Top 3 des risques prioritaires

| # | Risque | Score | Priorité |
|---|---|:---:|---|
"""
    for i, r in enumerate(top_risks, 1):
        score = r["vraisemblance"] * r["impact"]
        _, emoji = get_criticite_level(score)
        content += f"| {i} | {r['menace']} ({r['actif']}) | {emoji} **{score}/16** | IMMÉDIATE |\n"

    content += f"""
---

## Matrice visuelle (Heatmap)

{build_heatmap_ascii()}

---

## Registre détaillé des risques ({len(RISKS)} risques)

{build_risk_table()}

---

## Statistiques du portefeuille de risques

{build_stats()}

---

## Prochaines étapes

1. **Immédiat (0-30 jours)** — Activer MFA sur tous les comptes Google Workspace (R03)
2. **Court terme (1-3 mois)** — Tester le plan de reprise ransomware + restauration S3 (R01, R11)
3. **Moyen terme (3-6 mois)** — Migration backup AWS eu-west-3 pour conformité RGPD (R07)
4. **Planifié (6-12 mois)** — Revue complète des accès Odoo + désactivation ex-employés (R05)

---

*Rapport généré automatiquement par risk_matrix.py — TechShop SAS SMSI v2.0*
*Prochaine revue : {date.today().replace(year=date.today().year + 1).strftime("%d/%m/%Y")}*
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Rapport genere : {output_path}")
    print(f"   {len(RISKS)} risques analyses")
    scores = [r["vraisemblance"] * r["impact"] for r in RISKS]
    critique = sum(1 for s in scores if s > 12)
    eleve = sum(1 for s in scores if 9 <= s <= 12)
    print(f"   CRITIQUE: {critique} | ELEVE: {eleve} | Score moyen : {sum(scores)/len(scores):.1f}/16")

def main():
    parser = argparse.ArgumentParser(description="Générateur de matrice de risques TechShop SAS")
    parser.add_argument("--output", default="rapport-risques.md", help="Fichier de sortie (défaut: rapport-risques.md)")
    args = parser.parse_args()
    generate_report(args.output)

if __name__ == "__main__":
    main()
