# Notification de Violation de Données à Caractère Personnel
**Article 33 du Règlement (UE) 2016/679 (RGPD)**

> 📋 **Ce document correspond au formulaire officiel disponible sur**
> **notifications.cnil.fr**
> En réalité, cette notification se fait en ligne sur le portail de la CNIL.
> Ce document en est la version archivable pour le registre interne de TechShop SAS.

---

## PARTIE 1 — Identification du responsable de traitement

| Champ | Valeur |
|---|---|
| **Raison sociale** | TechShop SAS |
| **Forme juridique** | Société par Actions Simplifiée |
| **SIREN** | 123 456 789 (fictif) |
| **Adresse siège** | 15 Rue du Commerce, 31000 Toulouse, France |
| **Secteur d'activité** | Commerce de détail en ligne — Code NAF 4791Z |
| **Taille** | 47 salariés — CA 3,2M€ |

---

## PARTIE 2 — Coordonnées du DPO

> **Pourquoi le DPO est-il obligatoire ici ?**
> TechShop SAS traite des données personnelles à grande échelle (15 000 clients).
> La désignation d'un DPO est obligatoire selon l'Article 37 RGPD.
> C'est le DPO qui signe et soumet la notification à la CNIL.

| Champ | Valeur |
|---|---|
| **Nom** | Sophie Blanc |
| **Fonction** | Délégué(e) à la Protection des Données (DPO) |
| **Email** | sophie.blanc@techshop.fr |
| **Téléphone** | +33 5 61 XX XX XX |
| **DPO interne ou externe** | Interne |

---

## PARTIE 3 — Description de la violation

> **C'est la section la plus importante.**
> La CNIL veut comprendre exactement ce qui s'est passé, comment et pourquoi.
> Soyez précis mais ne speculez pas — indiquez "en cours d'investigation"
> pour ce qui n'est pas encore confirmé.

### 3.1 Date et heure de la violation

| Champ | Valeur |
|---|---|
| **Date de la violation** | 03/06/2026 à 02h09 UTC+2 (heure estimée de début) |
| **Date de détection** | 03/06/2026 à 02h17 UTC+2 |
| **Délai détection → notification** | ~44 heures (dans le délai légal de 72h) |
| **La violation est-elle en cours ?** | NON — serveur isolé à 02h25 |

### 3.2 Nature de la violation

> **Les 3 types de violation selon le RGPD :**
> - **Confidentialité** : données divulguées à des personnes non autorisées ← notre cas
> - **Intégrité** : données modifiées de façon non autorisée
> - **Disponibilité** : données perdues ou inaccessibles

☑️ **Atteinte à la confidentialité** — Accès non autorisé et exfiltration de données

☐ Atteinte à l'intégrité

☐ Atteinte à la disponibilité

### 3.3 Description factuelle

```
Le 03 juin 2026 à 02h09 UTC+2, un acteur malveillant a exploité une vulnérabilité
d'injection SQL (CVE associée à WooCommerce version 7.0.0) pour accéder à la base
de données clients du site e-commerce de TechShop SAS hébergé sur infrastructure OVH.

L'attaque a permis l'exfiltration de la table clients de la base WooCommerce pendant
une durée estimée à 8 minutes (02h09 → 02h17), pour un volume de données de
~487 MB compressés.

L'attaque a été détectée automatiquement par le système de monitoring Grafana/Prometheus
via une alerte sur le volume de données sortant anormal. Le serveur a été isolé à 02h25.

L'IP source identifiée (185.220.101.X) correspond à un nœud du réseau Tor.
Une plainte pénale est en cours de dépôt (Article 323-1 du Code pénal).
```

### 3.4 Cause de la violation

```
Cause technique directe :
Plugin WooCommerce version 7.0.0 (installé depuis novembre 2022, non mis à jour).
Vulnérabilité d'injection SQL exploitable sans authentification via le paramètre
de recherche produit (?s= parameter).

Cause organisationnelle :
Absence de processus de gestion des correctifs (patch management) formalisé.
Absence de surveillance des CVE applicables aux composants du SI.

Facteurs contributifs :
- Interface XML-RPC WordPress activée (vecteur d'accès supplémentaire)
- Absence de Web Application Firewall applicatif interne
- Centralisation des logs non réalisée (délai de détection de 8 minutes)
```

---

## PARTIE 4 — Personnes et données concernées

> **La CNIL évalue la gravité en fonction de ces informations.**
> Si vous ne connaissez pas encore le nombre exact, donnez une fourchette.
> Vous pourrez compléter dans les 30 jours suivant la notification initiale.

### 4.1 Catégories de personnes concernées

| Catégorie | Nombre | Détail |
|---|---|---|
| Clients particuliers (B2C) | ~14 200 | Ayant passé au moins 1 commande |
| Clients professionnels (B2B) | ~800 | Revendeurs partenaires |
| **TOTAL** | **~15 000** | Fourchette : 14 500 à 15 200 |

> ⚠️ Le dénombrement exact est en cours — confirmation définitive sous 72h.

### 4.2 Catégories de données concernées

| Catégorie de données | Sensibilité RGPD | Exposé ? |
|---|---|---|
| Nom et prénom | Standard | ✅ OUI |
| Adresse email | Standard | ✅ OUI |
| Adresse postale de livraison | Standard | ✅ OUI |
| Numéro de téléphone | Standard | ✅ OUI (pour ~80% des clients) |
| Historique de commandes | Standard | ✅ OUI |
| Hash de mot de passe (bcrypt) | Sensible | ✅ OUI |
| Données de paiement (CB) | Très sensible | ❌ NON — gérées exclusivement par Stripe |
| Données de santé | Sensible | ❌ NON |
| Données de mineurs | Sensible | ❌ NON (vérification en cours) |

### 4.3 Volume de données exfiltrées

- **Volume estimé :** ~487 MB (données compressées)
- **Format :** Dump SQL complet de la table wp_users et tables WooCommerce associées

---

## PARTIE 5 — Conséquences probables

> **La CNIL veut savoir quels risques concrets les personnes encourent.**
> Soyez honnête — minimiser les risques peut aggraver votre situation
> si la CNIL découvre que vous avez sous-estimé les impacts.

### 5.1 Risques pour les personnes concernées

| Risque | Probabilité | Gravité |
|---|---|---|
| **Phishing ciblé** (email + nom) | Élevée | Moyenne |
| **Spam commercial non désiré** | Élevée | Faible |
| **Usurpation d'identité partielle** | Moyenne | Élevée |
| **Attaque par credential stuffing** (si même mdp ailleurs) | Moyenne | Élevée |
| **Fraude à la livraison** (adresse connue) | Faible | Moyenne |
| **Accès aux comptes TechShop** (hash bcrypt) | Faible | Moyenne |

### 5.2 Absence de risque sur les données bancaires

> Les données de paiement (numéros de carte bancaire, CVV) ne sont pas
> stockées dans l'infrastructure TechShop SAS. Elles sont traitées
> exclusivement par Stripe (certifié PCI-DSS). Ce point est confirmé
> par notre architecture SAQ A et les logs Stripe.

---

## PARTIE 6 — Mesures prises et envisagées

> **C'est votre chance de montrer à la CNIL que vous réagissez de façon responsable.**
> Des mesures rapides et pertinentes peuvent réduire significativement les sanctions.
> La CNIL distingue les entreprises qui "font de leur mieux" de celles qui négligent.

### 6.1 Mesures immédiates (J+0)

| Mesure | Heure | Responsable | Statut |
|---|---|---|---|
| Isolation du serveur compromis | 02h25 | Thomas Rivet | ✅ Fait |
| Blocage IP attaquante (Cloudflare) | 02h30 | Thomas Rivet | ✅ Fait |
| Préservation des preuves numériques | 02h45 | Thomas Rivet | ✅ Fait |
| Mise en maintenance du site | 03h30 | Thomas Rivet | ✅ Fait |
| Désactivation XML-RPC | 07h00 | Thomas Rivet | ✅ Fait |

### 6.2 Mesures à court terme (J+1 à J+7)

| Mesure | Échéance | Responsable |
|---|---|---|
| Mise à jour WooCommerce 10.7.0 | 10/06/2026 | Thomas Rivet |
| Audit complet des plugins WordPress | 10/06/2026 | Nicolas Bernard |
| Réinitialisation forcée des mots de passe clients | 10/06/2026 | Thomas Rivet |
| Communication aux 15 000 clients | 09/06/2026 | Sophie Blanc |
| Dépôt de plainte pénale (Article 323-1) | 06/06/2026 | Marie Laurent |

### 6.3 Mesures structurelles (J+8 à J+90)

| Mesure | Échéance | Contrôle ISO 27001 |
|---|---|---|
| Mise en place processus patch management | 30/06/2026 | A.8.8 |
| Déploiement SIEM (Wazuh) | 31/07/2026 | A.8.15 |
| Activation WAF applicatif interne | 31/07/2026 | A.8.20 |
| Segmentation réseau (VLAN) | 31/08/2026 | A.8.22 |
| Formation sécurité équipes IT | 31/07/2026 | A.6.3 |
| Pentest annuel WooCommerce | 31/12/2026 | A.8.34 |

---

## PARTIE 7 — Communication aux personnes concernées

> **Dois-je informer mes clients ?**
> OUI dans notre cas, car le risque pour leurs droits et libertés est ÉLEVÉ
> (Article 34 RGPD). La communication doit être claire, accessible,
> et donner des conseils concrets pour se protéger.

**Décision :** Communication aux 15 000 clients par email **avant le 09/06/2026**

**Contenu prévu de l'email :**

---

*Objet : [Important] Information sur la sécurité de votre compte TechShop*

Madame, Monsieur,

Nous vous contactons car votre compte TechShop SAS a été impacté par un incident de sécurité survenu le 3 juin 2026.

**Que s'est-il passé ?**
Notre site a subi une attaque informatique. Des données associées à votre compte ont pu être consultées par des personnes non autorisées : votre nom, adresse email, adresse postale et historique de commandes.

**Vos données bancaires ne sont PAS concernées** — elles sont gérées exclusivement par notre prestataire de paiement Stripe et n'étaient pas accessibles.

**Ce que vous devez faire immédiatement :**
1. **Changez votre mot de passe TechShop** sur techshop.fr/mon-compte
2. **Si vous utilisez le même mot de passe ailleurs**, changez-le également sur ces sites
3. **Méfiez-vous des emails suspects** mentionnant TechShop dans les prochaines semaines
4. En cas de doute, contactez-nous : security@techshop.fr ou 05 61 XX XX XX

Nous sommes sincèrement désolés de cet incident. Nous mettons tout en œuvre pour que cela ne se reproduise pas.

Marie Laurent
Directrice Générale, TechShop SAS

---

---

## PARTIE 8 — Déclaration et signature

| Champ | Valeur |
|---|---|
| **Je certifie** | Les informations fournies sont exactes et complètes à la date de notification |
| **Notification susceptible d'être complétée** | OUI — dénombrement exact en cours |
| **Date de notification CNIL** | 04/06/2026 à 22h00 UTC+2 |
| **Signataire** | Sophie Blanc — DPO TechShop SAS |

---

## Annexes

- **Annexe 1 :** Registre interne INC-2026-001
- **Annexe 2 :** Logs serveur horodatés (02h09 → 02h25)
- **Annexe 3 :** Rapport WPScan du 03/06/2026 (CVE WooCommerce)
- **Annexe 4 :** Architecture technique TechShop SAS (preuve non-stockage CB)
- **Annexe 5 :** Récépissé dépôt de plainte pénale

---

*Document confidentiel — TechShop SAS*
*Conservé 5 ans conformément à l'Article 33.5 RGPD*
*Référence : INC-2026-001 | Notification CNIL N° [attribué par la CNIL]*
