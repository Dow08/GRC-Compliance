# Évaluation de la Conformité RGPD : Syntaris Group
**Date :** 2026-05-27
**Statut :** Version Finale (Phase 3)
**Auditeur :** Cabinet de Conseil en Cybersécurité (Auditeur GRC)

Ce rapport présente une analyse approfondie de la conformité de Syntaris Group vis-à-vis des articles clés du Règlement Général sur la Protection des Données (RGPD), avec un focus particulier sur les Articles 5, 25, 32 et 33.

---

## 1. Article 5 : Principes relatifs au traitement des données personnelles
L'Article 5 définit les principes cardinaux du traitement des données. Pour Syntaris, deux principes fondamentaux sont actuellement mis en péril :

*   **Minimisation des données (Art 5.1.c) :** Syntaris collecte des données financières, des pièces d'identité et des données biométriques. L'audit montre un risque important de sur-conservation (conservation indéfinie des scans bruts de passeports après validation).
    *   *Remédiation :* Mettre en œuvre une suppression automatique des gabarits biométriques bruts dès la finalisation de la vérification d'identité. Ne stocker que le jeton de validation (token kyc).
*   **Limitation de la conservation (Art 5.1.e) :** Les données ne doivent pas être conservées plus longtemps que nécessaire.
    *   *Remédiation :* Rédiger et appliquer une politique stricte de durée de conservation des données (ex. données de transaction conservées 5 ans selon les obligations fiscales nationales, documents KYC supprimés sous 30 jours).

---

## 2. Article 25 : Protection des données dès la conception et par défaut
L'entreprise gère des flux hautement sensibles (paiements, identités) mais manque de cartographie formalisée et de mesures de protection automatiques de la vie privée.

*   **Protection dès la conception (Privacy by Design - Tokenisation des APIs) :** L'API de paiement ne doit jamais stocker ni faire transiter les numéros de carte de crédit (PAN) en clair dans les logs internes ou bases secondaires.
    *   *Remédiation :* Implémenter une tokenisation systématique des cartes bancaires au niveau de la passerelle de paiement (conformément aux exigences PCI-DSS).
*   **Protection par défaut (Privacy by Default - Données de test et moindre privilège) :** Les développeurs utilisent des données de production réelles pour tester leurs fonctionnalités et déboguer localement.
    *   *Remédiation :* Mettre en place un masquage systématique des données et utiliser un générateur de données synthétiques (fictives) pour tous les environnements de test. Enforcer un contrôle d'accès strict (RBAC) sur les bases de production.

---

## 3. Article 32 : Sécurité du traitement
L'Article 32 impose au responsable de traitement de mettre en œuvre des mesures techniques et organisationnelles appropriées pour garantir un niveau de sécurité adapté au risque.

*   **Écarts constatés à l'audit :**
    *   Absence de Politique de Sécurité des Systèmes d'Information (PSSI) formelle.
    *   Absence de centralisation des logs (SIEM) et de surveillance en temps réel (SOC) 24/7.
    *   MFA (Authentification Multi-Facteurs) non obligatoire sur l'ensemble des postes de développement.
*   **Remédiation :**
    *   Imposer le MFA obligatoire pour tous les accès administratifs et les comptes de développement (NIST PR.AA-03).
    *   Chiffrer toutes les bases de données au repos (AES-256) avec des clés gérées par Syntaris (BYOK via AWS KMS) pour les bases KYC (NIST PR.DS-01).
    *   Intégrer des outils d'analyse statique de code (SAST) dans la pipeline CI/CD pour prévenir l'injection de vulnérabilités applicatives (NIST PR.PS-06).

---

## 4. Article 33 : Notification de violation de données à l'autorité de contrôle
L'Article 33 impose au responsable de traitement de notifier à l'autorité de contrôle (la CNIL en France) toute violation de données personnelles dans un délai maximum de **72 heures** après en avoir pris connaissance, sauf si la violation n'est pas susceptible d'engendrer un risque pour les droits et libertés.

*   **Écarts constatés à l'audit :**
    *   Aucun plan formel de réponse aux incidents de sécurité ni de procédure d'escalade.
    *   Pas de modèle pré-rempli de notification de fuite de données.
    *   Aucun Délégué à la Protection des Données (DPO) désigné pour piloter la réponse réglementaire.
*   **Remédiation :**
    *   Désigner officiellement un DPO (Article 37) pour piloter la conformité globale et orchestrer les relations avec les autorités de contrôle.
    *   Créer un Playbook de réponse aux violations de données détaillant les étapes de détection, d'évaluation, de confinement, et de notification CNIL dans la fenêtre réglementaire des 72 heures.
    *   Conserver un registre interne obligatoire de toutes les violations de données constatées, même celles non notifiables.
