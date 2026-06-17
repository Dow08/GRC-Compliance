# Rapport d'Évaluation de Maturité NIST CSF 2.0
**Date :** 2026-05-27
**Organisation :** Syntaris Group
**Auditeur :** Cabinet d'Audit et de Conseil Cybersécurité

## 1. Synthèse Exécutive
Ce rapport présente l'état de la maturité en cybersécurité de Syntaris Group évalué par rapport au référentiel international NIST CSF 2.0. Les activités de Syntaris en tant que fintech (traitement de paiements et vérification d'identité KYC biométrique) imposent des contrôles de protection et de résilience cyber extrêmement rigoureux. Actuellement, Syntaris présente des caractéristiques de niveau de maturité Tier 1 (Partiel) / Tier 2 (Informé du risque), avec un objectif d'atteindre le niveau Tier 3 (Répétable) / Tier 4 (Adaptatif) pour rassurer ses clients bancaires et s'assurer de sa conformité réglementaire transatlantique (RGPD / PCI-DSS).

## 2. Résumé de la Maturité par Fonction NIST

| Fonction NIST | Code | Score Actuel | Score Cible | Écart (Gap) | Niveau Cible Visé |
|---|---|---|---|---|---|
| Gouverner (Govern) | GV | 1.50 / 4.0 | 3.67 / 4.0 | +2.17 | Tier 3 (Répétable) |
| Identifier (Identify) | ID | 1.50 / 4.0 | 3.75 / 4.0 | +2.25 | Tier 3 (Répétable) |
| Protéger (Protect) | PR | 1.83 / 4.0 | 4.00 / 4.0 | +2.17 | Tier 4 (Adaptatif) |
| Détecter (Detect) | DE | 1.50 / 4.0 | 4.00 / 4.0 | +2.50 | Tier 4 (Adaptatif) |
| Répondre (Respond) | RS | 1.00 / 4.0 | 4.00 / 4.0 | +3.00 | Tier 4 (Adaptatif) |
| Récupérer (Recover) | RC | 1.00 / 4.0 | 4.00 / 4.0 | +3.00 | Tier 4 (Adaptatif) |
| **GLOBAL** | **TOTAL** | **1.50 / 4.0** | **3.86 / 4.0** | **+2.36** | **Tier 3 (Répétable)** |


## 3. Détails des Écarts par Sous-Catégorie

| Code | Nom de la Sous-Catégorie | Score Actuel | Score Cible | Justification / Constats d'Audit |
|---|---|---|---|---|
| GV.OC-01 | Mission organisationnelle comprise | 2 | 4 | La mission est comprise de facon informelle mais non formalisee dans une charte d entreprise. |
| GV.OC-03 | Exigences legales et reglementaires comprises | 2 | 4 | Le RGPD et PCI-DSS sont identifies mais pas completement integres dans les processus techniques. |
| GV.RM-01 | Objectifs de gestion des risques convenus | 1 | 3 | Pas de politique formelle de gestion des risques validée par la direction. |
| GV.RR-01 | Roles et responsabilites cyber etablis | 2 | 4 | Les roles existent au sein de la technique mais pas de responsabilisation transverse ni de DPO officiel. |
| GV.PO-01 | Politique cyber etablie | 1 | 4 | Pas de PSSI (Politique de Securite des Systemes d Information) globale et redigee. |
| GV.SC-01 | Programme de gestion des risques fournisseurs | 1 | 3 | Pas d audit systematique de la conformite des sous-traitants cloud et SaaS (Art 28 RGPD). |
| ID.AM-01 | Inventaire materiel maintenu | 2 | 3 | Inventaire automatique partiel des serveurs cloud mais pas des equipements locaux. |
| ID.AM-03 | Cartographie des flux de donnees | 1 | 4 | Aucune cartographie des flux de donnees personnelles et de paiement n est documentee. |
| ID.RA-01 | Vulnerabilites identifiees | 2 | 4 | Des scans de vulnerabilites ad-hoc sont faits mais pas de processus de gestion des correctifs formalise. |
| ID.RA-05 | Risques cyber prioritises | 1 | 4 | Pas de registre des risques formellement mis a jour et presente au CODIR. |
| PR.AA-03 | Authentification forte (MFA) | 2 | 4 | MFA actif sur les consoles cloud mais pas sur l ensemble des postes de developpement ni acces admin. |
| PR.AA-05 | Acces gere selon moindre privilege | 1 | 4 | Droits d acces trop permissifs accordes par defaut aux developpeurs et supports. |
| PR.DS-01 | Donnees protegees au repos | 2 | 4 | Bases de donnees cloud chiffrees par defaut mais cles de chiffrement gerees par le fournisseur (pas de KMS propre). |
| PR.DS-02 | Donnees protegees en transit | 3 | 4 | HTTPS systematique sur les APIs de paiement externes. |
| PR.DS-11 | Sauvegardes creees et testees | 2 | 4 | Sauvegardes automatiques dans le cloud mais pas de tests de restauration periodiques documentes. |
| PR.PS-06 | Pratiques securite du code | 1 | 4 | Pas d analyse statique de code (SAST) systematique ni de controle des dependances dans la CI/CD. |
| DE.CM-01 | Reseaux surveilles | 2 | 4 | Logs cloud collectes mais pas de SIEM ni de surveillance en temps reel centralisee. |
| DE.AE-02 | Activites suspectes analysees | 1 | 4 | Pas d equipe dediee (SOC interne ou externe) pour analyser et lever les alertes 24/7. |
| RS.MA-01 | Plan de reponse execute | 1 | 4 | Pas de plan de reponse aux incidents documente (PUI) ni de playbook de gestion des violations de donnees. |
| RS.CO-02 | Parties prenantes internes notifiees | 1 | 4 | Pas de procedure d escalade vers le juridique pour la notification CNIL sous 72h (Art 33). |
| RC.RP-01 | Plan de reprise execute | 1 | 4 | Pas de plan de continuite ni de reprise d activite (PCA/PRA) formalise et teste pour la fintech. |
| RC.RP-03 | Integrite sauvegardes verifiee | 1 | 4 | Aucun test formel de restauration des sauvegardes n est realise regulierement. |

## 4. Recommandations Cyber Majeures
1. **Formaliser la Gouvernance de Sécurité (Govern - GV) :** Rédiger et faire approuver une Politique de Sécurité des Systèmes d'Information (PSSI) globale et désigner un Délégué à la Protection des Données (DPO) officiel.
2. **Cartographier le Cycle de Vie des Données (Identify - ID) :** Réaliser une cartographie complète des flux de données personnelles et de transaction financière.
3. **Renforcer la Sécurité des Plateformes (Protect - PR) :** Rendre obligatoire l'authentification forte (MFA) sur l'ensemble des consoles d'administration cloud et postes de développement. Intégrer de l'analyse de code automatisée (SAST) dans la chaîne de déploiement CI/CD.
4. **Déployer une Surveillance Continue (Detect - DE) :** Mettre en œuvre une centralisation des logs (SIEM) et externaliser la surveillance en temps réel 24/7 à un SOC managé.
5. **Rédiger les Plans d'Urgence et de Reprise (Respond & Recover - RS/RC) :** Créer un Playbook officiel de réponse aux violations de données (CNIL 72h) et élaborer des plans de continuité et de reprise d'activité (PCA/PRA).
