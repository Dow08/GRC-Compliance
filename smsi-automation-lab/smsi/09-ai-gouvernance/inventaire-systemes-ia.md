# Inventaire des Systèmes d'Intelligence Artificielle — TechShop SAS
**Version :** 1.0
**Date :** Juin 2026
**Auteur :** Dorian Poncelet (Consultant GRC)
**Statut :** Validé
**Référence :** Règlement UE 2024/1689 (AI Act) — Article 49 / ISO/IEC 42001:2023

---

## Contexte réglementaire

Le **Règlement européen sur l'IA (AI Act)** est entré en vigueur le 1er août 2024. Ses obligations
s'appliquent progressivement :

```
Août 2024   → Entrée en vigueur
Fév. 2025   → Interdictions (IA à risque inacceptable)
Août 2025   → Modèles d'IA à usage général (GPAI)
Août 2026   → Systèmes à haut risque (Annexe III)
Août 2027   → Systèmes embarqués dans produits réglementés
```

> **Position TechShop SAS :** L'entreprise est **utilisatrice** de systèmes d'IA (pas développeuse).
> Elle relève du statut de **déployeur** au sens de l'AI Act (Art. 3.4). À ce titre, elle a des
> obligations de transparence, de surveillance humaine et de documentation — même pour les
> systèmes IA fournis par des tiers (HubSpot, Stripe, Google).

---

## Méthode d'inventaire

L'inventaire suit la taxonomie AI Act :

| Niveau de risque | Définition | Obligation principale |
|---|---|---|
| **Inacceptable** | IA interdite (manipulation, score social...) | Interdit — ne pas déployer |
| **Haut risque** | Impact sur droits fondamentaux, emploi, accès services | Documentation, audit, supervision humaine obligatoires |
| **Risque limité** | Interaction avec humains non évidente | Obligation de transparence |
| **Risque minimal** | Jeux, spam filters, recommandations simples | Bonnes pratiques volontaires |

---

## Inventaire des systèmes IA — TechShop SAS

### IA-001 — Moteur de recommandations produits (WooCommerce)

| Champ | Détail |
|---|---|
| **Système** | Plugin WooCommerce "Product Recommendations" |
| **Fournisseur** | WooCommerce / Automattic |
| **Fonction** | Suggère des produits complémentaires ou similaires aux clients sur la base de leur historique de navigation et d'achat |
| **Données en entrée** | Historique de navigation, panier en cours, historique commandes, produits similaires achetés par d'autres |
| **Personnes affectées** | ~15 000 clients actifs |
| **Niveau de risque AI Act** | **Risque minimal** — recommandations commerciales, pas d'impact sur droits fondamentaux |
| **Transparence** | Partiellement — les recommandations ne sont pas toujours clairement identifiées comme automatisées |
| **Supervision humaine** | Faible — le responsable e-commerce peut ajuster les règles de recommandation |
| **Statut conformité** | ⚠️ **Partiel** — mention "recommandé pour vous" sans explication du mécanisme |
| **Action requise** | Ajouter une mention de transparence ("Ces suggestions sont basées sur votre historique") |

---

### IA-002 — Détection de fraude Stripe Radar

| Champ | Détail |
|---|---|
| **Système** | Stripe Radar (ML de détection de fraude) |
| **Fournisseur** | Stripe Inc. (USA) |
| **Fonction** | Analyse chaque transaction pour détecter les paiements frauduleux. Peut bloquer automatiquement une transaction ou demander une vérification supplémentaire (3DS). |
| **Données en entrée** | Montant, pays, device fingerprint, historique de la carte, vitesse de transaction, adresse IP |
| **Personnes affectées** | Tous les clients passant une commande (~15 000 personnes) |
| **Niveau de risque AI Act** | **Risque limité à haut risque** — selon l'interprétation : décision automatisée impactant l'accès à un service (refus de paiement = impossibilité d'achat) |
| **Transparence** | Partielle — Stripe fournit un score de risque mais TechShop ne communique pas aux clients les raisons d'un refus |
| **Supervision humaine** | Partielle — Thomas Rivet peut consulter les transactions bloquées et les débloquer manuellement |
| **Droits des personnes** | ⚠️ Un client dont la transaction est refusée a-t-il le droit de contester ? (Art. 22 RGPD + AI Act Art. 26.3) |
| **Statut conformité** | ⚠️ **Partiel** — procédure de contestation absente |
| **Action requise** | Documenter la procédure de contestation manuelle + informer les clients de l'existence d'une vérification automatisée |

---

### IA-003 — Scoring et segmentation HubSpot (CRM)

| Champ | Détail |
|---|---|
| **Système** | HubSpot Lead Scoring + Workflow automation |
| **Fournisseur** | HubSpot Inc. (USA) |
| **Fonction** | Attribue un score à chaque prospect selon son comportement (emails ouverts, pages visitées, achats). Déclenche automatiquement des campagnes email selon ce score. |
| **Données en entrée** | Comportement email, navigation site, historique achat, profil démographique |
| **Personnes affectées** | ~8 000 prospects et clients CRM |
| **Niveau de risque AI Act** | **Risque minimal** — marketing B2C, pas de décision impactant des droits fondamentaux |
| **Transparence** | Faible — les clients ne savent pas qu'ils sont scorés |
| **Supervision humaine** | Partielle — le responsable marketing peut modifier les workflows |
| **Lien RGPD** | ⚠️ Le profilage commercial est soumis au droit d'opposition (Art. 21 RGPD) |
| **Statut conformité** | ⚠️ **Partiel** — pas de mention du profilage dans la politique de confidentialité |
| **Action requise** | Mentionner le profilage dans la politique de confidentialité + activer le droit d'opposition |

---

### IA-004 — Google Analytics 4 (analyse comportementale)

| Champ | Détail |
|---|---|
| **Système** | Google Analytics 4 avec modélisation comportementale |
| **Fournisseur** | Google LLC (USA) |
| **Fonction** | Analyse le comportement des visiteurs, prédit les conversions, modélise les audiences pour les campagnes Google Ads |
| **Données en entrée** | Pages visitées, durée, clics, IP pseudonymisée, device, sessions |
| **Personnes affectées** | ~50 000 visiteurs/mois |
| **Niveau de risque AI Act** | **Risque minimal** — analytics agrégés, pas de décision individuelle automatisée |
| **Transparence** | Partielle — bandeau cookies présent, mais les fonctions IA de GA4 ne sont pas explicitées |
| **Supervision humaine** | Haute — les décisions marketing restent humaines, GA4 fournit des insights |
| **Statut conformité** | ⚠️ **Partiel** — IP anonymisation activée mais fonctions de modélisation IA à documenter |
| **Action requise** | Documenter les fonctions IA de GA4 dans le registre des traitements RGPD |

---

### IA-005 — Filtrage anti-spam Google Workspace

| Champ | Détail |
|---|---|
| **Système** | Google Workspace Spam & Phishing Filter (ML) |
| **Fournisseur** | Google LLC (USA) |
| **Fonction** | Filtre automatiquement les emails entrants comme spam, phishing ou légitimes |
| **Données en entrée** | Contenu email, expéditeur, liens, pièces jointes, réputation domaine |
| **Personnes affectées** | 47 employés TechShop |
| **Niveau de risque AI Act** | **Risque minimal** — filtre technique interne, pas d'impact sur droits fondamentaux |
| **Transparence** | Haute — les emails filtrés sont visibles dans le dossier Spam |
| **Supervision humaine** | Haute — tout employé peut marquer un email comme "non spam" |
| **Statut conformité** | ✅ **Conforme** — usage standard, supervision humaine naturelle |
| **Action requise** | Aucune |

---

## Synthèse du portefeuille IA

| ID | Système | Niveau risque | Conformité | Priorité |
|---|---|:---:|:---:|:---:|
| IA-001 | Recommandations WooCommerce | Minimal | ⚠️ Partiel | P3 |
| IA-002 | Stripe Radar (fraude) | Limité/Haut | ⚠️ Partiel | **P1** |
| IA-003 | HubSpot scoring | Minimal | ⚠️ Partiel | P2 |
| IA-004 | Google Analytics 4 | Minimal | ⚠️ Partiel | P3 |
| IA-005 | Google Spam Filter | Minimal | ✅ Conforme | — |

### Points d'attention prioritaires

**Stripe Radar est le système le plus sensible.** C'est le seul qui prend des décisions automatisées avec un impact direct sur la capacité d'un client à acheter. Si un client légitime est bloqué sans recours, c'est potentiellement une violation de l'AI Act (Art. 26) et du RGPD (Art. 22). La procédure de contestation est à créer en priorité.

**Le profilage HubSpot n'est pas mentionné** dans la politique de confidentialité actuelle. C'est une non-conformité RGPD (Art. 13 — information sur le profilage) autant qu'un risque AI Act.

---

## Prochaines étapes

| Action | Responsable | Échéance |
|---|---|---|
| Procédure contestation Stripe Radar | DSI + DPO | 31/08/2026 |
| Mention profilage dans politique confidentialité | DPO | 31/08/2026 |
| Transparence recommandations WooCommerce | DSI | 31/10/2026 |
| Documentation IA GA4 dans registre RGPD | DPO | 31/10/2026 |
| Revue annuelle inventaire IA | DSI + DPO | Juin 2027 |

---

*Document produit dans le cadre du SMSI TechShop SAS — Projet portfolio GRC Automation + AI Governance*
*Prochaine révision : Juin 2027 ou lors de l'ajout d'un nouveau système IA*
