# Support de Présentation : Audit GRC de Syntaris Group
## Plan Stratégique de Sécurité et de Conformité NIST CSF 2.0 & RGPD
**Présentateur :** Dorian Poncelet — Conseiller en Cybersécurité

---

## Diapositive 1 : Contexte de l'Audit
### Qui est Syntaris Group ?
*   **Activité :** Fournisseur de solutions fintech de paiement numérique en ligne et de vérification d'identité numérique (KYC).
*   **Envergure :** Forte croissance et opérations transatlantiques (Europe et États-Unis).
*   **Infrastructure :** Architecture hybride Cloud-Local (Cloud public AWS/Azure pour le moteur transactionnel, serveurs sur site sécurisés pour l'administration et le corporatif).
*   **Enjeux de Conformité :** RGPD (Europe), PCI-DSS (Secteur bancaire) et exigences de maturité cyber formulées par les banques partenaires.

---

## Diapositive 2 : Cartographie des Actifs & Données Critiques
*   **Données Financières (RGPD / PCI-DSS) :**
    *   Numéros de cartes bancaires (PAN), montants et historique des transactions de paiement.
*   **Données d'Identité et de Biométrie (RGPD Art. 9 / KYC) :**
    *   Scans de passeports/cartes d'identité, gabarits biométriques de reconnaissance faciale.
    *   *Alerte de Conformité :* Traiter de la biométrie (données sensibles) rend obligatoire la nomination d'un DPO et la réalisation d'une Analyse d'Impact (AIPD/DPIA).
*   **Données Système & Propriété Intellectuelle :**
    *   Code source des APIs de paiement, clés d'accès API de production, configurations cloud.

---

## Diapositive 3 : Top 3 des Risques d'Entreprise
1.  **Exfiltration ou fuite de la base KYC & Biométrique :**
    *   *Impact :* Amende administrative jusqu'à 4% du CA mondial (Art. 83), perte de confiance instantanée des marchands, audit de la CNIL.
2.  **Indisponibilité de la plateforme de paiement (DDoS / Ransomware) :**
    *   *Impact :* Perte de chiffre d'affaires immédiate, pénalités contractuelles (SLA) avec les marchands en ligne.
3.  **Piratage de la chaîne d'approvisionnement logiciel (Software Supply Chain) :**
    *   *Impact :* Injection de code malveillant sur les APIs de paiement (type Magecart) volant les cartes de crédit en temps réel lors du traitement.

---

## Diapositive 4 : Profil de Maturité NIST CSF 2.0
*   **Score Moyen Actuel :** **1.50 / 4.0** *(Niveau 1 - Partiel / Niveau 2 - Informé)*
*   **Score Moyen Cible :** **3.86 / 4.0** *(Niveau 3 - Répétable / Niveau 4 - Adaptatif)*

### Résultats par Fonction :
*   **Govern (GV) :** Actuel 1.50 -> Cible 3.67 *(Écart : +2.17)*
*   **Identify (ID) :** Actuel 1.50 -> Cible 3.75 *(Écart : +2.25)*
*   **Protect (PR) :** Actuel 1.83 -> Cible 4.00 *(Écart : +2.17)*
*   **Detect (DE) :** Actuel 1.50 -> Cible 4.00 *(Écart : +2.50)*
*   **Respond (RS) :** Actuel 1.00 -> Cible 4.00 *(Écart : +3.00)* - **ÉCART CRITIQUE**
*   **Recover (RC) :** Actuel 1.00 -> Cible 4.00 *(Écart : +3.00)* - **ÉCART CRITIQUE**

---

## Diapositive 5 : Focus RGPD — Écarts Majeurs Identifiés
*   **Article 5 (Minimisation) :** Conservation indéfinie et non justifiée des scans de passeports et gabarits biométriques de KYC.
*   **Article 25 (Privacy by Design/Default) :** Développeurs utilisant des données de clients réels pour déboguer ; numéros de cartes en clair visibles dans certains logs.
*   **Article 32 (Sécurité) :** Absence de MFA obligatoire sur les postes des ingénieurs ; pas d'analyse automatisée de sécurité du code source.
*   **Article 33 (Notification sous 72h) :** Pas de DPO désigné, absence totale de plan d'action d'urgence et de playbook de gestion de fuites de données.

---

## Diapositive 6 : Feuille de Route Priorité 1 : Quick Wins (0-30 Jours)
### Objectif : Protection Juridique et Contrôle d'Accès Critique
*   **REC-01 : Désigner un DPO et Rédiger le Playbook de Notification CNIL sous 72H**
    *   *Mesure :* Assurer la conformité légale immédiate aux Articles 33 et 37. Préparer les modèles d'escalade et de déclaration de crise.
    *   *Responsable :* Direction Générale / Affaires Juridiques.
*   **REC-02 : Activer le MFA Obligatoire sur les Accès d'Administration et Dépôts de Code**
    *   *Mesure :* Éliminer 99% des risques d'accès non autorisés par phishing ou vol de mot de passe.
    *   *Responsable :* DevOps / Sécurité IT.

---

## Diapositive 7 : Feuille de Route Priorité 2 : Protections (30-90 Jours)
### Objectif : Sécurisation Technique et Résilience Opérationnelle
*   **REC-03 : Tokenisation des Cartes Bancaires & Génération de Données de Test**
    *   *Mesure :* Remplacer les cartes par des jetons (PCI-DSS) et automatiser la création de bases de test synthétiques (Art 25 - Privacy by Default).
    *   *Responsable :* Ingénierie Logicielle / Équipe QA.
*   **REC-04 : Chiffrement AES-256 des Bases de Données et Sauvegardes Froides**
    *   *Mesure :* Chiffrer au repos et créer des sauvegardes déconnectées (offline) immuables pour se prémunir des ransomwares.
    *   *Responsable :* Infrastructure IT.

---

## Diapositive 8 : Feuille de Route Priorité 3 : Gouvernance (90-180 Jours)
### Objectif : Amélioration Continue et Détection Continue
*   **REC-05 : Rédiger la PSSI de Syntaris et la Charte Informatique Collaborateur**
    *   *Mesure :* Formaliser les attentes de sécurité et sensibiliser l'ensemble du personnel pour limiter l'ingénierie sociale.
    *   *Responsable :* RSSI / RH / DPO.
*   **REC-06 : Surveillance 24/7 via la mise en place d'un SOC Managé Tiers**
    *   *Mesure :* Centraliser les logs de sécurité (SIEM) et externaliser l'analyse et la levée de doute en temps réel à un partenaire de confiance.
    *   *Responsable :* Directeur de la Sécurité IT.

---

## Diapositive 9 : Conclusion
### Enseignements Clés pour Syntaris Group
*   **La Sécurité comme Accélérateur de Business :** Une gouvernance mature NIST CSF 2.0 est un prérequis indispensable pour rassurer et signer de grands partenaires bancaires.
*   **La Protection des Données est Non Négociable :** Passer de la conservation de documents biométriques bruts à un statut KYC tokenisé protège Syntaris des amendes réglementaires majeures.
*   **GRC Moderne et Technique :** Utiliser des bases de données structurées (CSV) et des scripts d'analyse automatisés assure un audit continu, fiable et directement présentable au CODIR.

### Merci pour votre attention ! Questions ?
