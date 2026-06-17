# Script d'automatisation des tests d'audit GRC Cyber-Compliance
# Lancer ce script dans PowerShell pour exécuter tous les cas de test.

Clear-Host
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "      LANCEMENT DE LA SUITE DE TESTS D'AUDIT CYBER-CONFORMITE GRC" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan

# 1. Configuration de l'environnement local Ollama
$env:OLLAMA_HOST = "http://localhost:11434"
Write-Host "[*] Configuration de OLLAMA_HOST sur http://localhost:11434" -ForegroundColor Gray

# 2. Test de diagnostic initial
Write-Host "`n[TEST 1] Diagnostic de la configuration..." -ForegroundColor Yellow
python cyber_compliance_agent.py --check-setup

# 3. Audit individuel de la base de données (PostgreSQL)
Write-Host "`n[TEST 2] Audit de la configuration de Base de Donnees (examples/db_playbook.yml)..." -ForegroundColor Yellow
python cyber_compliance_agent.py --file examples/db_playbook.yml --control DB_HARDENING --output examples/rapport_db.html

# 4. Audit individuel du déploiement Kubernetes (K8s)
Write-Host "`n[TEST 3] Audit de la configuration Kubernetes (examples/k8s_deployment.yaml)..." -ForegroundColor Yellow
python cyber_compliance_agent.py --file examples/k8s_deployment.yaml --control K8S_HARDENING --output examples/rapport_k8s.html

# 5. Scan complet du dépôt de configurations IaC (Dossier d'exemples)
Write-Host "`n[TEST 4] Scan complet et consolidé du dossier d'exemples..." -ForegroundColor Yellow
python cyber_compliance_agent.py --dir examples --output examples/dashboard_conformite.html

Write-Host "`n====================================================================" -ForegroundColor Green
Write-Host "                 SUITE DE TESTS TERMINEE AVEC SUCCES" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Green
Write-Host "[+] Les rapports d'audit suivants ont ete generes :" -ForegroundColor Green
Write-Host "    - Rapport individuel DB : examples/rapport_db.html" -ForegroundColor Green
Write-Host "    - Rapport individuel K8s : examples/rapport_k8s.html" -ForegroundColor Green
Write-Host "    - Tableau de Bord Global : examples/dashboard_conformite.html" -ForegroundColor Green
Write-Host "`nVous pouvez double-cliquer sur ces fichiers pour les ouvrir dans votre navigateur." -ForegroundColor Gray
Write-Host "Pour tester le blocage strict de securite (mode CI/CD), executez :" -ForegroundColor Gray
Write-Host "    python cyber_compliance_agent.py --file examples/db_playbook.yml --control DB_HARDENING --strict" -ForegroundColor Magenta
