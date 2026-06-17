# Lab d'Audit de Conformité GRC - Syntaris Group
## Cadre d'Audit Conjoint NIST CSF 2.0 & RGPD pour Plateforme Fintech

[![GRC Audit](https://img.shields.io/badge/GRC-Audit-blue.svg)](#)
[![NIST CSF 2.0](https://img.shields.io/badge/Framework-NIST%20CSF%202.0-green.svg)](#)
[![GDPR Compliant](https://img.shields.io/badge/Conformite-RGPD-orange.svg)](#)
[![Python Automation](https://img.shields.io/badge/Automatisation-Python%203-blue.svg)](#)

Ce dépôt constitue un laboratoire d'audit de sécurité et de conformité réglementaire pour **Syntaris Group**, une fintech en pleine croissance spécialisée dans le traitement des paiements en ligne et la vérification d'identité numérique (KYC) en Europe et aux États-Unis.

En tant que conseiller externe en cybersécurité, ce lab démontre comment aligner la gouvernance d'entreprise, les exigences réglementaires (RGPD, PCI-DSS) et les cadres de sécurité internationaux (NIST CSF 2.0) au sein d'une feuille de route technique pilotée par les risques.

---

## 📂 Structure du Dépôt

*   `data/nist_csf_evaluation.csv` : Base de données brute de l'audit GRC contenant 22 sous-catégories clés du NIST CSF 2.0 évaluées avec scores actuels, cibles et justifications d'audit.
*   `scripts/scoring_nist_csf.py` : Script d'automatisation Python 3 qui calcule les scores de maturité, trace des graphiques comparatifs en barres ASCII et exporte automatiquement le rapport détaillé.
*   `scripts/poc_privacy_compliance.py` : Preuve de Concept (PoC) active démontrant la tokenisation (Privacy by Design) et la réponse automatisée aux violations de données selon l'Article 33 du RGPD.
*   `reports/nist_csf_report.md` : Rapport de maturité NIST CSF 2.0 détaillé généré automatiquement en français.
*   `reports/gdpr_compliance_analysis.md` : Analyse de conformité RGPD axée sur les Articles 5 (Principes), 25 (Privacy by Design/Default), 32 (Sécurité) et 33 (Notification des violations sous 72h).
*   `reports/roadmap_recommendations.md` : Feuille de route stratégique priorisée (Urgence Haute/Moyenne/Faible) basée sur la loi de Pareto (Risque vs Effort d'implémentation).
*   `reports/poc_incident_cnil_notification.txt` : Projet de déclaration officielle CNIL généré automatiquement à la suite de la détection d'un incident de sécurité simulé.
*   `reports/presentation_slides.md` : Trame de soutenance complète pour une présentation orale de 5 à 10 minutes (CODIR ou examen académique).

---

## ⚙️ Scoring de Maturité & Génération de Heatmap

Ce laboratoire utilise du code pour prouver et automatiser la GRC. Pour exécuter le scoring automatique de maturité et générer la heatmap comparative, lancez la commande suivante :

```bash
python3 scripts/scoring_nist_csf.py
```

### Aperçu de la Sortie Console
```text
============================================================
      PROFIL DE MATURITE NIST CSF 2.0 : ACTUEL VS CIBLE
============================================================

GV - GOVERN:
  Actuel:  [████████░░░░░░░░░░░░] 1.50 / 4.0
  Cible:   [██████████████████░░] 3.67 / 4.0
  Écart:   +2.17

ID - IDENTIFY:
  Actuel:  [████████░░░░░░░░░░░░] 1.50 / 4.0
  Cible:   [███████████████████░] 3.75 / 4.0
  Écart:   +2.25

PR - PROTECT:
  Actuel:  [█████████░░░░░░░░░░░] 1.83 / 4.0
  Cible:   [████████████████████] 4.00 / 4.0
  Écart:   +2.17

DE - DETECT:
  Actuel:  [████████░░░░░░░░░░░░] 1.50 / 4.0
  Cible:   [████████████████████] 4.00 / 4.0
  Écart:   +2.50

RS - RESPOND:
  Actuel:  [█████░░░░░░░░░░░░░░░] 1.00 / 4.0
  Cible:   [████████████████████] 4.00 / 4.0
  Écart:   +3.00

RC - RECOVER:
  Actuel:  [█████░░░░░░░░░░░░░░░] 1.00 / 4.0
  Cible:   [████████████████████] 4.00 / 4.0
  Écart:   +3.00
============================================================
```

---

### 🧪 Preuve de Concept (PoC) Interactive : Privacy by Design & Automatisation RGPD

Pour démontrer la mise en œuvre concrète de l'Article 25 du RGPD (Tokenisation et Masquage de données de test) et de l'Article 33 (Détection d'une fuite et auto-génération d'une notification CNIL sous 72h), exécutez le script d'accompagnement :

```bash
python3 scripts/poc_privacy_compliance.py
```

Ce script simule une attaque cyber en cours sur les bases biométriques de Syntaris, l'isole en temps réel et pré-remplit instantanément le projet de déclaration officielle CNIL dans le fichier `reports/poc_incident_cnil_notification.txt`.

---

## 🎯 Enjeux Stratégiques Clés & Écarts Majeurs

1.  **Progression de Maturité :** La maturité globale de sécurité se situe actuellement à un niveau faible de **1.50 / 4.0** (Tier 1 - Partiel / Tier 2 - Informé), avec un objectif cible fixé à **3.86 / 4.0** (Tier 3/4 - Répétable/Adaptatif).
2.  **Sensibilité de la Biométrie :** La collecte de gabarits biométriques faciaux pour le KYC active strictement l'**Article 9 du RGPD (Données Sensibles)**, ce qui rend la nomination formelle d'un DPO et la réalisation d'une Analyse d'Impact (AIPD/DPIA) juridiquement obligatoires.
3.  **Écarts Critiques sur Respond & Recover :** Les fonctions de réponse aux incidents (RS) et de reprise d'activité (RC) sont les plus exposées, affichant un score actuel de **1.00 / 4.0**. Syntaris n'a aucun plan formel de réponse aux violations de données ni de plan de continuité/reprise d'activité (PCA/PRA).

---

## 🛡️ Plan d'Action & Feuille de Route (Loi de Pareto)

*   **Priorité 1 (0-30 Jours - Quick Wins) :** Désigner formellement un DPO + Rédiger le playbook de notification CNIL sous 72h + Imposer le double facteur (MFA) sur les consoles cloud et les dépôts de code (GitHub).
*   **Priorité 2 (30-90 Jours - Protections Techniques) :** Déployer la tokenisation des cartes bancaires (PCI-DSS) + Automatiser la génération de données de test synthétiques (Art 25 - Privacy by Default) + Chiffrer les sauvegardes (AES-256).
*   **Priorité 3 (90-180 Jours - Gouvernance Continue) :** Rédiger la Politique de Sécurité (PSSI) et la Charte Informatique + Externaliser la surveillance de sécurité 24/7 à un SOC managé tiers.

---

## 🤝 Utilisation du Lab
1.  Clonez ce dépôt de recherche.
2.  Explorez les métriques de scoring brutes dans `data/nist_csf_evaluation.csv`.
3.  Exécutez les scripts Python pour observer l'analyse en temps réel et mettre à jour vos livrables.
