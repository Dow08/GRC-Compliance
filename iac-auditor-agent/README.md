# IAC-G.R.C-Auditor_ AGENT

Cet outil est un auditeur automatisé de conformité GRC (Gouvernance, Risques & Conformité) conçu pour l'Infrastructure-as-Code (IaC). 

Il permet d'analyser vos fichiers de configuration technique (Ansible, Terraform, Kubernetes, Docker) et de valider leur niveau de sécurité **avant** qu'ils ne soient déployés en production.

L'architecture repose sur le pattern **« Parser-to-Reasoner »** :
1. **Parser (Local, Python standard)** : Le script lit et extrait la configuration technique sans aucune dépendance externe (zéro `pip install`, fonctionne sur n'importe quelle machine vierge).
2. **Reasoner (Raisonnement IA)** : L'extraction est envoyée à un modèle d'intelligence artificielle (une IA locale tournant sur votre machine via **Ollama / Gemma 2**, ou un modèle distant comme Anthropic Claude, OpenAI GPT ou Google Gemini) qui joue le rôle d'auditeur de sécurité. J'ai choisi ici un modèle local pour éviter toute fuite de données ou problématiques avec des données sensibles. 
3. **Reporter (Restitution)** : L'outil génère un rapport d'audit détaillé, fait la correspondance réglementaire et fournit le plan de remédiation technique sous forme de commandes ou de blocs de code directement exploitables.

---

## Commandes

### 1. Tester la connexion avec votre IA locale
```powershell
python cyber_compliance_agent.py --check-setup
```

### 2. Lancer le mode démo / tutoriel d'apprentissage
```powershell
python cyber_compliance_agent.py
```

### 3. Auditer l'intégralité d'un dossier d'exemples et générer le Tableau de Bord HTML
```powershell
python cyber_compliance_agent.py --dir examples --output examples/dashboard_conformite.html
```

### 4. Lancer un audit ciblé sur un fichier spécifique
```powershell
python cyber_compliance_agent.py --file examples/db_playbook.yml --control DB_HARDENING --output examples/rapport_db.html
```

---

## 📂 Structure du Projet

Le dépôt est organisé de manière claire et structurée :

* 📁 **`examples/`** : Contient les différents exemples de configurations techniques IaC servant de cibles d'audit (playbooks Ansible, manifestes Kubernetes). Les rapports HTML générés lors des tests y sont également sauvegardés.
* 📁 **`poc/`** : Regroupe les captures d'écran de Proof of Concept illustrant le fonctionnement de l'outil et l'interface du tableau de bord interactif.
* 📄 **`cyber_compliance_agent.py`** : Le code source de l'auditeur GRC.
* 📄 **`run_tests.ps1`** : Script d'automatisation pour lancer l'ensemble des scénarios de test sous Windows.

---

## 🎯 Pourquoi utiliser cet outil ?

Dans les équipes SecOps et GRC, les audits de conformité réglementaire sont souvent des tâches manuelles, lentes et déconnectées du cycle de développement. Ce projet résout ce problème en automatisant l'audit et en le plaçant directement dans les mains des développeurs et des équipes sécurité :

* **Audit Préventif** : Détecte les vulnérabilités avant qu'elles ne soient appliquées sur vos serveurs.
* **Zéro Dépendance** : Écrit uniquement avec les bibliothèques standards de Python. Aucune installation requise sur votre machine ou vos agents de build.
* **Confidentialité Intégrale (Interne)** : Fonctionne de manière autonome à 100 % hors-ligne avec des modèles de langage locaux (Ollama), garantissant qu'aucune donnée de configuration sensible ne quitte votre réseau.
* **Auto-remédiation et Diagnostic** : Donne des explications précises et le code correctif exact prêt à être appliqué.

---

## 📚 Sur quelles sources se base l'audit ?

L'évaluation de la conformité repose sur des cadres réglementaires officiels et des standards reconnus de l'industrie :

1. **ISO/IEC 27001:2022 (Annexe A)** : L'outil mappe sémantiquement les configurations techniques aux mesures de sécurité de l'organisation (A.5.15 pour le contrôle d'accès, A.8.20 pour la sécurité réseau, A.8.24 pour la cryptographie, A.8.2 pour les privilèges utilisateur).
2. **Directive Européenne NIS 2 (Article 21)** : Liaison directe avec les obligations légales de gestion des risques (politique de chiffrement, contrôle d'accès, sécurité de l'infrastructure).
3. **Référentiel de Vulnérabilités (CWE & CVE)** : L'IA identifie et classe dynamiquement les failles détectées selon la nomenclature du MITRE (CWE-256 pour les mots de passe en clair, CWE-319 pour l'absence de TLS, CWE-284 pour les accès réseau non restreints) et les associe à des classes de CVE historiques.
4. **Guides de Hardening Professionnels** : Les recommandations de correction s'inspirent des **CIS Benchmarks** (Center for Internet Security) et des bonnes pratiques de l'ANSSI.

---

## 🛠️ Fonctionnalités Principales

* **Audit individuel de fichier (`--file`)** : Analyse ciblée d'une configuration (ex: un playbook Ansible ou un manifeste K8s) par rapport à un contrôle de la matrice.
* **Scan récursif de répertoires (`--dir`)** : Analyse l'intégralité d'un dossier. Le script identifie automatiquement la nature de chaque fichier de configuration et lui associe le bon contrôle de sécurité.
* **Tableau de Bord HTML Consolidé** : Génère un rapport graphique sombre, interactif et moderne compilant l'état de conformité de l'ensemble du projet (avec taux de réussite global, métadonnées GRC et volets de remédiation). Imprimable directement en PDF.
* **Mode Strict CI/CD (`--strict`)** : Utile pour bloquer les déploiements non conformes en renvoyant un code d'erreur (`exit 1`) tout en affichant un rapport de diagnostic verbeux dans le journal de build.
* **Outil de Diagnostic local (`--check-setup`)** : Permet de tester instantanément l'état de vos configurations IA.

---

## 🚀 Intégration DevSecOps (GitHub Actions)

Ce script est conçu pour se positionner comme une **barrière de sécurité (Security Gate)** directement dans votre chaîne de CI/CD. 

Voici un exemple simple d'intégration dans un workflow **GitHub Actions** pour auditer automatiquement vos playbooks et bloquer le build si une faille critique est introduite :

```yaml
name: GRC Infrastructure Security Audit

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  security-audit:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      # Si vous utilisez un fournisseur cloud payant (ex: OpenAI)
      - name: Run GRC Compliance Audit (Strict Mode)
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python cyber_compliance_agent.py --dir examples --strict --output examples/dashboard_conformite.html

      # Archiver le rapport HTML généré pour consultation
      - name: Archive Compliance Report
        uses: actions/upload-artifact@v3
        with:
          name: GRC-Compliance-Dashboard
          path: examples/dashboard_conformite.html
```

---



---
*Développé pour simplifier le dialogue entre les équipes techniques (Ops/Dev) et les équipes de Gouvernance Cyber (GRC).*
