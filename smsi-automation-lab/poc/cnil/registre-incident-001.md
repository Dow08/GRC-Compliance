# Registre Interne des Violations de Données — TechShop SAS
**Référence incident :** INC-2026-001  
**Version :** 1.0  
**Date de création :** 03/06/2026 03h00  
**Créé par :** Sophie Blanc (DPO)  
**Statut :** EN COURS

---

> 📋 **Pourquoi ce document ?**
> L'Article 33.5 du RGPD oblige tout responsable de traitement à **documenter toutes les violations**
> de données, même celles qui ne nécessitent pas de notification CNIL.
> Ce registre est le premier document à remplir dès qu'une violation est suspectée.
> Il sert de base à la notification CNIL et à l'analyse post-incident.

---

## SECTION 1 — Identification de l'incident

| Champ | Valeur |
|---|---|
| **Numéro d'incident** | INC-2026-001 |
| **Date/heure de détection** | 03/06/2026 à 02h17 UTC+2 |
| **Date/heure de notification interne** | 03/06/2026 à 02h30 UTC+2 |
| **Détecté par** | Système de monitoring Grafana + Prometheus |
| **Nature de l'alerte** | Export massif base de données WooCommerce (>500 MB en 8 minutes) |
| **Signalé à** | Thomas Rivet (DSI) + Sophie Blanc (DPO) |
| **DG informée** | 03/06/2026 à 07h00 UTC+2 — Marie Laurent |

---

## SECTION 2 — Nature de la violation

> **Qu'est-ce qu'une violation de données ?**
> Toute violation de la sécurité entraînant la destruction, la perte, l'altération, la divulgation
> non autorisée de données personnelles. Ici : **divulgation non autorisée** (confidentialité).

| Champ | Valeur |
|---|---|
| **Type de violation** | ☑️ Confidentialité (divulgation non autorisée) |
| | ☐ Intégrité (altération des données) |
| | ☐ Disponibilité (destruction/perte) |
| **Vecteur d'attaque** | Exploitation CVE WooCommerce 7.0.0 — injection SQL via paramètre de recherche produit |
| **Méthode d'accès** | Accès externe non authentifié via vulnérabilité applicative |
| **Durée de l'exposition** | Estimée à 8 minutes (02h09 → 02h17) |
| **Données exfiltrées** | Base de données clients WooCommerce (table wp_users + wp_usermeta + wp_woocommerce_order_items) |
| **Destination des données** | Inconnue — IP source : 185.220.101.X (nœud Tor identifié) |

---

## SECTION 3 — Personnes et données concernées

> **Pourquoi c'est crucial ?**
> La CNIL évalue la gravité de la violation en fonction du nombre de personnes touchées
> et de la sensibilité des données. Plus c'est grave, plus la notification est urgente.

### Personnes concernées

| Catégorie | Nombre estimé | Certitude |
|---|---|---|
| Clients B2C (particuliers) | ~14 200 | Élevée |
| Clients B2B (revendeurs) | ~800 | Élevée |
| **TOTAL** | **~15 000** | **Élevée** |

### Données concernées

| Type de données | Sensibilité | Volume |
|---|---|---|
| Nom + Prénom | Standard | 15 000 |
| Adresse email | Standard | 15 000 |
| Adresse postale de livraison | Standard | 14 500 |
| Numéro de téléphone | Standard | 12 000 |
| Historique de commandes | Standard | 15 000 |
| Hash de mot de passe (bcrypt) | Sensible | 15 000 |
| ~~Numéros de carte bancaire~~ | ~~Très sensible~~ | 0 (gérés par Stripe) |

> ✅ **Point positif :** TechShop SAS délègue le paiement à Stripe (SAQ A).
> Les numéros de carte bancaire ne sont PAS stockés dans la base WooCommerce.
> Cela réduit significativement la gravité de la violation.

> ⚠️ **Point préoccupant :** Les hash de mots de passe bcrypt ont fuité.
> Bien que bcrypt soit robuste, des attaques par dictionnaire ciblées sont possibles.
> Les clients doivent être invités à changer leur mot de passe.

---

## SECTION 4 — Évaluation de la gravité

> **La matrice de gravité CNIL** permet de déterminer si la notification est obligatoire
> et si les personnes concernées doivent être informées directement.

### Critères d'évaluation

| Critère | Évaluation | Score |
|---|---|---|
| **Facilité d'identification** des personnes | Élevée (nom + email + adresse) | 3/3 |
| **Nombre de personnes** concernées | Élevé (15 000) | 3/3 |
| **Sensibilité des données** | Moyenne (pas de bancaires, pas de santé) | 2/3 |
| **Conséquences potentielles** | Phishing ciblé, usurpation identité | 2/3 |
| **Caractéristiques des personnes** | Population générale (pas de mineurs identifiés) | 1/3 |

**Score global : 11/15 → Gravité ÉLEVÉE**

### Décision

| Action | Obligatoire ? | Décision TechShop SAS |
|---|---|---|
| Notification CNIL | ✅ OUI (> seuil de notification) | **OUI — avant le 06/06/2026 02h17** |
| Communication aux personnes | ✅ OUI (risque élevé pour les droits) | **OUI — sous 72h supplémentaires** |
| Notification autorités sectorielles | ❌ NON (pas OIV/OSE) | Non applicable |

---

## SECTION 5 — Mesures prises immédiatement

> **Ce que TechShop SAS a fait dans les premières heures.**
> La CNIL regarde si l'entreprise a réagi rapidement et de façon appropriée.
> Une réaction rapide peut réduire les sanctions.

### Actions techniques (Thomas Rivet — DSI)

| Heure | Action | Statut |
|---|---|---|
| 02h25 | Isolation du serveur WooCommerce du réseau | ✅ Fait |
| 02h30 | Blocage de l'IP source 185.220.101.X sur Cloudflare | ✅ Fait |
| 02h45 | Capture des logs serveur (préservation des preuves) | ✅ Fait |
| 03h00 | Sauvegarde de la base de données pour analyse forensique | ✅ Fait |
| 03h30 | Désactivation du site (maintenance) | ✅ Fait |
| 07h00 | Désactivation XML-RPC | ✅ Fait |
| 08h00 | Patch WooCommerce 10.7.0 en cours | 🔄 En cours |

### Actions organisationnelles (Sophie Blanc — DPO)

| Heure | Action | Statut |
|---|---|---|
| 02h30 | Ouverture du registre d'incident | ✅ Fait |
| 07h00 | Information de la DG (Marie Laurent) | ✅ Fait |
| 08h00 | Activation cellule de crise | ✅ Fait |
| 09h00 | Début préparation notification CNIL | 🔄 En cours |
| 10h00 | Préparation email communication clients | 🔄 En cours |

---

## SECTION 6 — Analyse de causalité

> **Pourquoi cette violation s'est-elle produite ?**
> Cette section est cruciale pour l'amélioration continue (Article 32 RGPD).
> Elle sera examinée par la CNIL en cas d'audit.

### Cause racine

**Cause technique :** Plugin WooCommerce 7.0.0 non mis à jour depuis novembre 2022.
Vulnérabilité d'injection SQL connue exploitée via le paramètre de recherche produit.

**Cause organisationnelle :** Absence de processus de patch management formalisé (contrôle
ISO 27001 A.8.8 identifié comme non-conforme lors de l'audit du 02/06/2026).

**Cause humaine :** Aucune ressource dédiée à la veille CVE WordPress/WooCommerce.

### Facteurs aggravants

- XML-RPC activé (facilité d'accès supplémentaire)
- Absence de WAF applicatif interne
- Logs non centralisés (détection tardive — 8 minutes après le début)

### Facteurs atténuants

- Stripe gère les paiements → aucune donnée bancaire exposée
- Cloudflare WAF a limité l'exfiltration (alerte déclenchée rapidement)
- Mots de passe hashés en bcrypt (non exploitables immédiatement)
- Réponse rapide de l'équipe technique

---

## SECTION 7 — Suivi et clôture

| Étape | Responsable | Échéance | Statut |
|---|---|---|---|
| Notification CNIL | Sophie Blanc | 06/06/2026 02h17 | 🔄 En cours |
| Communication clients | Sophie Blanc | 09/06/2026 | 🔄 En cours |
| Remédiation technique complète | Thomas Rivet | 10/06/2026 | 🔄 En cours |
| Post-mortem incident | Thomas Rivet + Sophie Blanc | 17/06/2026 | ⏳ Planifié |
| Mise à jour SMSI | Dorian Poncelet (consultant) | 30/06/2026 | ⏳ Planifié |
| Clôture incident | Sophie Blanc | 30/06/2026 | ⏳ Planifié |

---

*Document confidentiel — TechShop SAS*
*Conservé 5 ans conformément à l'Article 33.5 RGPD*
