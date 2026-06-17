#!/usr/bin/env python3
"""
poc_privacy_compliance.py
-------------------------
Proof of Concept (PoC) technique de conformite RGPD & NIST CSF 2.0 pour Syntaris Group.
Ce script demontre deux piliers techniques de notre audit :
1. Privacy by Design (Art 25) : Tokenisation de cartes bancaires et masquage KYC.
2. Breach Detection & Response (Art 32/33) : Detection d incident et auto-generation
   du formulaire officiel de notification CNIL de fuite de donnees.
"""

import os
import json
import re
import hashlib
from datetime import datetime

# =====================================================================
# PARTIE 1 : PRIVACY BY DESIGN (ARTICLE 25 & PCI-DSS)
# =====================================================================

def tokenise_pan(pan):
    """
    Simule la tokenisation securisee d un numero de carte bancaire (PAN).
    Remplace le numero par un jeton de transaction unique et conserve les 4 derniers chiffres.
    """
    clean_pan = re.sub(r'\D', '', pan)
    if len(clean_pan) < 13 or len(clean_pan) > 19:
        return "Erreur : Format de carte invalide"
    
    # Generation du token via un hash SHA-256 sale (simule la passerelle de tokenisation)
    salt = "SYNTARIS_SECRET_SALT_2026"
    token_hash = hashlib.sha256((clean_pan + salt).encode()).hexdigest()[:16].upper()
    
    # Formatage : 4 derniers chiffres conserves pour le support
    last_four = clean_pan[-4:]
    token = f"TOKEN-V5-{token_hash[:4]}-{token_hash[4:8]}-{token_hash[8:12]}-{last_four}"
    return token

def anonymise_profil_kyc(profil_original):
    """
    Prend un profil client brut issu de la base KYC et retourne un profil
    minimise et anonymise utilisable pour les environnements de test.
    """
    profil_anonyme = {
        "id_client": profil_original["id_client"],
        "statut_kyc": profil_original["statut_kyc"],
        # Masquage des donnees nominatives
        "nom_complet": profil_original["nom_complet"][0] + "..." + "X" * (len(profil_original["nom_complet"]) - 2),
        "email_masque": re.sub(r'(^.)([^@]+)(@.+)', r'\1***\3', profil_original["email"]),
        # Suppression des donnees biometriques brutes dans l environnement cible
        "gabarit_biometrique_brut": "REJECTED_BY_DEFAULT_ENVIRONMENT_TESTS",
        "scan_passeport_base64": "PURGED_BY_DEFAULT_RETENTION_RULE_30_DAYS",
        "jeton_validation_kyc": hashlib.md5(profil_original["id_client"].encode()).hexdigest().upper()
    }
    return profil_anonyme


# =====================================================================
# PARTIE 2 : BREACH DETECTION & RESPONSE (ARTICLE 32 & 33)
# =====================================================================

# Simulation de logs de transaction cloud AWS CloudTrail / CloudWatch
LOGS_SIMULES = [
    {"timestamp": "2026-05-27T08:00:12Z", "ip": "192.168.1.50", "api_key": "sk_live_98ab", "endpoint": "/v1/charges", "status": 200, "payload_size_kb": 2.4},
    {"timestamp": "2026-05-27T08:01:45Z", "ip": "192.168.1.50", "api_key": "sk_live_98ab", "endpoint": "/v1/charges", "status": 200, "payload_size_kb": 1.8},
    # Debut de l attaque : Requete massive anormale sur les fichiers biometriques bruts depuis une IP externe inconnue
    {"timestamp": "2026-05-27T08:10:01Z", "ip": "198.51.100.22", "api_key": "sk_test_dev_98ab", "endpoint": "/v1/kyc/biometrics/raw_templates", "status": 200, "payload_size_kb": 45000},
    {"timestamp": "2026-05-27T08:10:05Z", "ip": "198.51.100.22", "api_key": "sk_test_dev_98ab", "endpoint": "/v1/kyc/biometrics/raw_templates", "status": 200, "payload_size_kb": 48000},
    {"timestamp": "2026-05-27T08:10:10Z", "ip": "198.51.100.22", "api_key": "sk_test_dev_98ab", "endpoint": "/v1/kyc/biometrics/raw_templates", "status": 200, "payload_size_kb": 52000},
    {"timestamp": "2026-05-27T08:12:30Z", "ip": "192.168.1.50", "api_key": "sk_live_98ab", "endpoint": "/v1/charges", "status": 200, "payload_size_kb": 1.9}
]

def scan_logs_pour_incidents(logs):
    """
    Analyse les logs de l infrastructure à la recherche de fuites potentielles.
    Regle de detection : Téléchargement unitaire de fichiers biometriques de taille > 10MB
    depuis une cle d API de developpement externe (sk_test_dev).
    """
    alertes = []
    for log in logs:
        if "/v1/kyc/biometrics/" in log["endpoint"] and log["payload_size_kb"] > 10000:
            if log["api_key"].startswith("sk_test_dev"):
                alertes.append(log)
    return alertes

def genere_formulaire_notification_cnil(incident_details, n_clients_impactes=1250):
    """
    Genere un projet de declaration officielle de violation de donnees a envoyer
    a la CNIL sous 72h, conformement a l Article 33 du RGPD.
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append("=====================================================================")
    lines.append("          PROJET DE DECLARATION DE VIOLATION DE DONNEES (CNIL)")
    lines.append("                  CONFORME A L'ARTICLE 33 DU RGPD")
    lines.append("=====================================================================")
    lines.append(f"Date de Generation : {current_time}")
    lines.append("Statut de la declaration : Initiale (Notification dans les 72h)")
    lines.append("Organisme Responsable du Traitement : Syntaris Group Ltd")
    lines.append("Nom du Data Protection Officer (DPO) : seallia81@gmail.com (DPO Interimaire)")
    lines.append("---------------------------------------------------------------------")
    lines.append("1. NATURE DE LA VIOLATION")
    lines.append("   - Type d incident : Acces non autorise / Exfiltration de donnees")
    lines.append(f"   - Date de la decouverte de l incident : {incident_details[0]['timestamp']}")
    lines.append("   - Source de la detection : Analyse automatisee des logs API")
    lines.append("   - Categorie de donnees personnelles concernees :")
    lines.append("       * Donnees d identite (Documents de verification KYC)")
    lines.append("       * Gabarits Biometriques bruts de reconnaissance faciale (Sensibles, Art 9)")
    lines.append(f"   - Nombre approximatif de personnes concernees : ~{n_clients_impactes} clients fintech")
    lines.append("---------------------------------------------------------------------")
    lines.append("2. CONSEQUENCES PROBABLES")
    lines.append("   - Risque eleve d usurpation d identite cyber-bancaire.")
    lines.append("   - Risque de contournement des systemes de verification d identite tiers.")
    lines.append("---------------------------------------------------------------------")
    lines.append("3. MESURES DE REMEDIATION PRISES OU ENVISAGEES IMMEDIATEMENT")
    lines.append(f"   - [EFFECTUÉ] Revocation immediate de la cle d API compromise ({incident_details[0]['api_key']}).")
    lines.append(f"   - [EFFECTUÉ] Blocage au niveau pare-feu (WAF) de l IP malveillante ({incident_details[0]['ip']}).")
    lines.append("   - [EN COURS] Notification des utilisateurs impactes sans delai injustifie (Art 34).")
    lines.append("   - [PLANIFIÉ] Migration vers un chiffrement des donnees biometriques avec cles uniques.")
    lines.append("=====================================================================\n")
    return "\n".join(lines)


# =====================================================================
# INTERFACE PRINCIPALE DE DEMONSTRATION
# =====================================================================

def main():
    print("="*65)
    print("    SYNTARIS GRC LABS : PROOF OF CONCEPT (PoC) COMPLIANCE")
    print("      Verification de la conformite technique RGPD / NIST")
    print("="*65)
    
    # 1. Demonstration du Privacy by Design
    print("\n--- [DEMO 1] ARTICLE 25 : PRIVACY BY DESIGN & BY DEFAULT ---")
    pan_demo = "4973 1204 8839 4110"
    token_result = tokenise_pan(pan_demo)
    print(f"[+] PAN Original (Poste Client) : {pan_demo}")
    print(f"[+] PAN Tokenise (Base Syntaris) : {token_result} (Conforme PCI-DSS)")
    
    profil_kyc_brut = {
        "id_client": "USER-9921-X",
        "nom_complet": "Jean-Pierre Martin",
        "email": "jp.martin@gmail.com",
        "statut_kyc": "EN_COURS",
        "gabarit_biometrique_brut": "[Vector64] 0.119, -0.928, 0.443, 0.822...",
        "scan_passeport_base64": "JVBERi0xLjQKJcfsj6IKMSAwIG9iagogIDw8IC9UeXBlIC9DYXRhbG9n..."
    }
    
    print("\n[i] Exportation d un profil KYC brut pour l environnement de test...")
    profil_test = anonymise_profil_kyc(profil_kyc_brut)
    print(f"    - Nom masqué : {profil_test['nom_complet']}")
    print(f"    - Email masqué : {profil_test['email_masque']}")
    print(f"    - Données Biométriques : {profil_test['gabarit_biometrique_brut']} (Sécurisé par défaut)")
    print(f"    - Scan de passeport : {profil_test['scan_passeport_base64']} (Sécurisé par défaut)")
    
    # 2. Demonstration de la detection et notification
    print("\n--- [DEMO 2] ARTICLE 32 & 33 : DETECT, RESPOND & NOTIFY ---")
    print("[i] Analyse en cours des logs d infrastructure Cloudtrail en temps reel...")
    
    incidents = scan_logs_pour_incidents(LOGS_SIMULES)
    
    if incidents:
        print(f"\n[CRITIQUE] ALERTE DE SÉCURITÉ : {len(incidents)} telechargements suspects detectes !")
        print(f"    - IP Malveillante : {incidents[0]['ip']}")
        print(f"    - Endpoint Visé : {incidents[0]['endpoint']}")
        print(f"    - Cle d API compromise : {incidents[0]['api_key']}")
        
        print("\n[+] Lancement automatique de la procedure GRC - Notification CNIL sous 72H...")
        draft_cnil = genere_formulaire_notification_cnil(incidents)
        print(draft_cnil)
        
        # Sauvegarde automatique du projet de declaration dans le dossier reports
        chemin_sauvegarde = "/workspace/reports/poc_incident_cnil_notification.txt"
        with open(chemin_sauvegarde, "w", encoding="utf-8") as f:
            f.write(draft_cnil)
        print(f"[+] Projet de declaration CNIL genere et sauvegarde dans : {chemin_sauvegarde}")
    else:
        print("[+] Aucun incident suspect detecte dans les logs.")

if __name__ == "__main__":
    main()
