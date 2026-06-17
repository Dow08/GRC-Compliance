#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import sys
from collections import defaultdict
from datetime import datetime

# Cartographie des fonctions NIST CSF 2.0
FUNCTIONS = {
    "GV": "Gouverner (Govern)",
    "ID": "Identifier (Identify)",
    "PR": "Protéger (Protect)",
    "DE": "Détecter (Detect)",
    "RS": "Répondre (Respond)",
    "RC": "Récupérer (Recover)"
}

def load_evaluation(csv_path):
    data = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append({
                    "fonction": row["fonction"].strip(),
                    "categorie": row["categorie"].strip(),
                    "sous_categorie": row["sous_categorie"].strip(),
                    "nom": row["nom"].strip(),
                    "score_actuel": float(row["score_actuel"]),
                    "score_cible": float(row["score_cible"]),
                    "justification": row["justification"].strip()
                })
    except Exception as e:
        print(f"Erreur lors du chargement du fichier CSV : {e}")
        sys.exit(1)
    return data

def calculate_metrics(data):
    by_fn = defaultdict(lambda: {"actuel_sum": 0.0, "cible_sum": 0.0, "count": 0, "items": []})
    for item in data:
        fn = item["fonction"]
        by_fn[fn]["actuel_sum"] += item["score_actuel"]
        by_fn[fn]["cible_sum"] += item["score_cible"]
        by_fn[fn]["count"] += 1
        by_fn[fn]["items"].append(item)
    return by_fn

def draw_ascii_chart(metrics):
    print("\n" + "="*60)
    print("      PROFIL DE MATURITE NIST CSF 2.0 : ACTUEL VS CIBLE")
    print("="*60)
    for fn, name in FUNCTIONS.items():
        m = metrics[fn]
        avg_actuel = m["actuel_sum"] / m["count"] if m["count"] else 0.0
        avg_cible = m["cible_sum"] / m["count"] if m["count"] else 0.0
        
        # Dessiner les barres
        bar_actuel = "█" * int(round(avg_actuel * 5)) + "░" * (20 - int(round(avg_actuel * 5)))
        bar_cible = "█" * int(round(avg_cible * 5)) + "░" * (20 - int(round(avg_cible * 5)))
        
        print(f"\n{fn} - {name.upper()}:")
        print(f"  Actuel: [{bar_actuel}] {avg_actuel:.2f} / 4.0")
        print(f"  Cible:  [{bar_cible}] {avg_cible:.2f} / 4.0")
        print(f"  Écart:  {avg_cible - avg_actuel:+.2f}")
    print("="*60 + "\n")

def generate_report(data, metrics, output_path):
    lines = []
    lines.append("# Rapport d'Évaluation de Maturité NIST CSF 2.0")
    lines.append(f"**Date :** {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("**Organisation :** Syntaris Group")
    lines.append("**Auditeur :** Cabinet d'Audit et de Conseil Cybersécurité\n")
    
    lines.append("## 1. Synthèse Exécutive")
    lines.append("Ce rapport présente l'état de la maturité en cybersécurité de Syntaris Group évalué par rapport au référentiel international NIST CSF 2.0. Les activités de Syntaris en tant que fintech (traitement de paiements et vérification d'identité KYC biométrique) imposent des contrôles de protection et de résilience cyber extrêmement rigoureux. Actuellement, Syntaris présente des caractéristiques de niveau de maturité Tier 1 (Partiel) / Tier 2 (Informé du risque), avec un objectif d'atteindre le niveau Tier 3 (Répétable) / Tier 4 (Adaptatif) pour rassurer ses clients bancaires et s'assurer de sa conformité réglementaire transatlantique (RGPD / PCI-DSS).\n")
    
    lines.append("## 2. Résumé de la Maturité par Fonction NIST\n")
    lines.append("| Fonction NIST | Code | Score Actuel | Score Cible | Écart (Gap) | Niveau Cible Visé |")
    lines.append("|---|---|---|---|---|---|")
    
    total_actuel = 0.0
    total_cible = 0.0
    total_count = 0
    
    for fn, name in FUNCTIONS.items():
        m = metrics[fn]
        avg_actuel = m["actuel_sum"] / m["count"] if m["count"] else 0.0
        avg_cible = m["cible_sum"] / m["count"] if m["count"] else 0.0
        gap = avg_cible - avg_actuel
        
        total_actuel += m["actuel_sum"]
        total_cible += m["cible_sum"]
        total_count += m["count"]
        
        tier = "Tier 3 (Répétable)" if avg_cible >= 3.0 else "Tier 4 (Adaptatif)"
        if avg_cible >= 3.8:
            tier = "Tier 4 (Adaptatif)"
            
        lines.append(f"| {name} | {fn} | {avg_actuel:.2f} / 4.0 | {avg_cible:.2f} / 4.0 | {gap:+.2f} | {tier} |")
        
    global_actuel = total_actuel / total_count if total_count else 0.0
    global_cible = total_cible / total_count if total_count else 0.0
    lines.append(f"| **GLOBAL** | **TOTAL** | **{global_actuel:.2f} / 4.0** | **{global_cible:.2f} / 4.0** | **{global_cible - global_actuel:+.2f}** | **Tier 3 (Répétable)** |")
    lines.append("\n")
    
    lines.append("## 3. Détails des Écarts par Sous-Catégorie\n")
    lines.append("| Code | Nom de la Sous-Catégorie | Score Actuel | Score Cible | Justification / Constats d'Audit |")
    lines.append("|---|---|---|---|---|")
    for item in data:
        lines.append(f"| {item['sous_categorie']} | {item['nom']} | {item['score_actuel']:.0f} | {item['score_cible']:.0f} | {item['justification']} |")
        
    lines.append("\n## 4. Recommandations Cyber Majeures")
    lines.append("1. **Formaliser la Gouvernance de Sécurité (Govern - GV) :** Rédiger et faire approuver une Politique de Sécurité des Systèmes d'Information (PSSI) globale et désigner un Délégué à la Protection des Données (DPO) officiel.")
    lines.append("2. **Cartographier le Cycle de Vie des Données (Identify - ID) :** Réaliser une cartographie complète des flux de données personnelles et de transaction financière.")
    lines.append("3. **Renforcer la Sécurité des Plateformes (Protect - PR) :** Rendre obligatoire l'authentification forte (MFA) sur l'ensemble des consoles d'administration cloud et postes de développement. Intégrer de l'analyse de code automatisée (SAST) dans la chaîne de déploiement CI/CD.")
    lines.append("4. **Déployer une Surveillance Continue (Detect - DE) :** Mettre en œuvre une centralisation des logs (SIEM) et externaliser la surveillance en temps réel 24/7 à un SOC managé.")
    lines.append("5. **Rédiger les Plans d'Urgence et de Reprise (Respond & Recover - RS/RC) :** Créer un Playbook officiel de réponse aux violations de données (CNIL 72h) et élaborer des plans de continuité et de reprise d'activité (PCA/PRA).\n")
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"[+] Rapport Markdown généré avec succès en français : {output_path}")
    except Exception as e:
        print(f"Erreur lors de l'écriture du rapport : {e}")

if __name__ == "__main__":
    csv_file = "/workspace/data/nist_csf_evaluation.csv"
    report_file = "/workspace/reports/nist_csf_report.md"
    
    data = load_evaluation(csv_file)
    metrics = calculate_metrics(data)
    draw_ascii_chart(metrics)
    generate_report(data, metrics, report_file)
