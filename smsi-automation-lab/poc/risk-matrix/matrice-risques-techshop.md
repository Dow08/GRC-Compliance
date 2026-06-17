# Matrice des Risques — TechShop SAS
**Version :** 1.0
**Date :** Juin 2026
**Méthode :** EBIOS RM simplifié
**Auteur :** Dorian Poncelet (Consultant GRC)

---

## Échelle de cotation

### Vraisemblance (V)
| Niveau | Valeur | Signification |
|---|---|---|
| Très faible | 1 | Scénario théorique, aucun précédent dans le secteur |
| Faible | 2 | Possible mais peu probable dans les 12 mois |
| Élevée | 3 | Probable dans les 12 mois, précédents dans le secteur |
| Très élevée | 4 | Quasi certain dans les 12 mois |

### Impact (I)
| Niveau | Valeur | Signification |
|---|---|---|
| Faible | 1 | Perturbation mineure, < 1 jour d'indisponibilité |
| Significatif | 2 | Impact notable, 1-3 jours, coût < 10 000€ |
| Grave | 3 | Impact majeur, > 3 jours, coût 10 000€ - 100 000€ |
| Critique | 4 | Menace la survie de l'entreprise, coût > 100 000€ |

### Criticité = V × I
| Score | Niveau | Action |
|---|---|---|
| 1-4 | 🟢 Faible | Surveiller |
| 5-8 | 🟡 Modéré | Traiter sous 6 mois |
| 9-12 | 🟠 Élevé | Traiter sous 3 mois |
| 13-16 | 🔴 Critique | Traiter immédiatement |

---

## Matrice visuelle

```
         │  IMPACT
         │  1-Faible  2-Significatif  3-Grave   4-Critique
─────────┼──────────────────────────────────────────────────
V  4     │    4          8            12🟠        16🔴
R  Très  │                          R007        R001
A  élevée│
I        │
S  3     │    3          6🟡          9🟠         12🟠
E  Élevée│                          R005        R002,R003
M        │                                      R006
B  2     │    2          4           6🟡          8🟡
L  Faible│                                      R004
A        │
N  1     │    1          2            3           4
C  Très  │
E  faible│
```

---

## Registre des 7 risques principaux

### R001 — Ransomware sur les serveurs OVH 🔴
| Champ | Valeur |
|---|---|
| **Actif impacté** | Serveurs OVH (WooCommerce + ERP Odoo) |
| **Menace** | Ransomware (chiffrement + exfiltration) |
| **Vulnérabilité** | Plugin WooCommerce non patché, XML-RPC actif |
| **Vraisemblance** | 4 — Très élevée (secteur e-commerce = cible prioritaire) |
| **Impact** | 4 — Critique (site HS + données clients + ERP inaccessible) |
| **Criticité** | **16/16** 🔴 |
| **Traitement** | Réduire |
| **Contrôles ISO** | A.8.7, A.8.8, A.8.13, A.5.26 |
| **Coût remédiation** | 2 820€/an (EDR) + 2 000€ (plan IR) |
| **Risque résiduel cible** | 8/16 après mesures |

**Scénario d'attaque :**
> Un attaquant exploite la CVE WooCommerce 7.0.0 pour accéder au serveur OVH.
> Il se déplace latéralement vers l'ERP Odoo (même segment réseau).
> Il déploie un ransomware qui chiffre tous les disques.
> Demande de rançon : 50 000€ en Bitcoin.
> Site e-commerce hors ligne = perte CA estimée à 8 000€/jour.

---

### R002 — Fuite de données clients (breach RGPD) 🟠
| Champ | Valeur |
|---|---|
| **Actif impacté** | Base de données clients (15 000 personnes) |
| **Menace** | Exfiltration de données personnelles |
| **Vulnérabilité** | Injection SQL WooCommerce, accès DB non restreint |
| **Vraisemblance** | 3 — Élevée (vulnérabilité technique confirmée par WPScan) |
| **Impact** | 4 — Critique (amende CNIL 128 000€ + perte de confiance) |
| **Criticité** | **12/16** 🟠 |
| **Traitement** | Réduire |
| **Contrôles ISO** | A.8.28, A.5.34, A.8.12 |
| **Coût remédiation** | 500€ (migration AWS) + 3 000€ (DPA + conformité RGPD) |
| **Risque résiduel cible** | 6/16 après mesures |

---

### R003 — Compromission compte Google Workspace admin 🟠
| Champ | Valeur |
|---|---|
| **Actif impacté** | Google Workspace (email + Drive + tous les SaaS) |
| **Menace** | Phishing ciblé, credential stuffing |
| **Vulnérabilité** | MFA non généralisé sur les comptes admin |
| **Vraisemblance** | 3 — Élevée (phishing = vecteur #1 des compromissions PME) |
| **Impact** | 4 — Critique (accès à tous les emails + documents RH + accès aux autres SaaS) |
| **Criticité** | **12/16** 🟠 |
| **Traitement** | Réduire |
| **Contrôles ISO** | A.8.5, A.5.17, A.6.3 |
| **Coût remédiation** | 0€ (MFA gratuit) + 300€ (Bitwarden) + 1 500€ (formation phishing) |
| **Risque résiduel cible** | 4/16 après mesures |

---

### R004 — Indisponibilité fournisseur critique (Stripe) 🟡
| Champ | Valeur |
|---|---|
| **Actif impacté** | Service de paiement en ligne |
| **Menace** | Panne/incident chez Stripe |
| **Vulnérabilité** | Dépendance unique à Stripe, pas d'alternative |
| **Vraisemblance** | 2 — Faible (SLA Stripe 99.99%) |
| **Impact** | 4 — Critique (0 vente possible pendant la panne) |
| **Criticité** | **8/16** 🟡 |
| **Traitement** | Accepter + surveiller |
| **Contrôles ISO** | A.5.29, A.5.30 |
| **Coût remédiation** | 0€ (surveillance status page Stripe) |
| **Risque résiduel cible** | 8/16 (risque transféré à Stripe) |

---

### R005 — Accès non autorisé ERP Odoo (ex-employé) 🟠
| Champ | Valeur |
|---|---|
| **Actif impacté** | ERP Odoo (données RH, finances, commandes) |
| **Menace** | Accès frauduleux par ex-employé non désactivé |
| **Vulnérabilité** | Absence de procédure offboarding formalisée |
| **Vraisemblance** | 3 — Élevée (aucune procédure = risque permanent) |
| **Impact** | 3 — Grave (vol données RH/financières, sabotage) |
| **Criticité** | **9/16** 🟠 |
| **Traitement** | Réduire |
| **Contrôles ISO** | A.5.11, A.6.5, A.5.16 |
| **Coût remédiation** | 0€ (procédure interne) |
| **Risque résiduel cible** | 3/16 après checklist offboarding |

---

### R006 — Injection SQL sur WooCommerce 🟠
| Champ | Valeur |
|---|---|
| **Actif impacté** | Site e-commerce WooCommerce |
| **Menace** | Injection SQL via paramètres non filtrés |
| **Vulnérabilité** | Plugin WooCommerce 7.0.0, absence de WAF applicatif |
| **Vraisemblance** | 3 — Élevée (vulnérabilité confirmée par WPScan POC) |
| **Impact** | 3 — Grave (accès DB clients, modification prix, défacement) |
| **Criticité** | **9/16** 🟠 |
| **Traitement** | Réduire |
| **Contrôles ISO** | A.8.28, A.8.8, A.8.20 |
| **Coût remédiation** | 400€ (mise à jour WooCommerce) + 0€ (Cloudflare WAF) |
| **Risque résiduel cible** | 4/16 après patch et WAF |

---

### R007 — Non-conformité RGPD transferts AWS us-east-1 🟠
| Champ | Valeur |
|---|---|
| **Actif impacté** | Sauvegardes AWS S3 (données clients UE) |
| **Menace** | Transfert illicite de données personnelles hors UE |
| **Vulnérabilité** | Bucket S3 en us-east-1 sans SCC (Standard Contractual Clauses) |
| **Vraisemblance** | 4 — Très élevée (transfert actif et documenté) |
| **Impact** | 3 — Grave (amende CNIL jusqu'à 128 000€) |
| **Criticité** | **12/16** 🟠 |
| **Traitement** | Réduire |
| **Contrôles ISO** | A.5.34, A.5.31 |
| **Coût remédiation** | 500€ (migration eu-west-3) |
| **Risque résiduel cible** | 3/16 après migration |

---

## Synthèse — Carte des risques

| ID | Risque | Criticité | Budget remédiation | Priorité |
|---|---|---|---|---|
| R001 | Ransomware OVH | 16/16 🔴 | 4 820€/an | P1 |
| R002 | Fuite données RGPD | 12/16 🟠 | 3 500€ | P1 |
| R003 | Compromission Google Workspace | 12/16 🟠 | 1 800€ | P1 |
| R004 | Indispo Stripe | 8/16 🟡 | 0€ | P3 |
| R005 | Ex-employé Odoo | 9/16 🟠 | 0€ | P1 |
| R006 | Injection SQL WooCommerce | 9/16 🟠 | 400€ | P1 |
| R007 | Transferts AWS hors UE | 12/16 🟠 | 500€ | P1 |

**Budget total remédiation risques critiques : ~11 020€**
**ROI sécurité : prévient une amende CNIL potentielle de 128 000€**

---

## Plan de traitement — 90 jours

```
Mois 1 (Juin 2026)
├── R003 → Activer MFA Google Workspace (0€, 1 jour)
├── R005 → Créer checklist offboarding (0€, 1 jour)
├── R006 → Patcher WooCommerce 10.7.0 (400€, 2 jours)
└── R007 → Migrer AWS vers eu-west-3 (500€, 3 jours)

Mois 2 (Juillet 2026)
├── R001 → Déployer EDR (2 820€/an, 2 jours)
├── R001 → Rédiger Plan IR ransomware (2 000€, 5 jours)
└── R002 → Compléter conformité RGPD (3 000€, 8 jours)

Mois 3 (Août 2026)
├── R001 → Tester restauration sauvegardes (0€, 1 jour)
└── R002 → Former équipes (1 500€, 3 jours)
```

---

*Matrice générée dans le cadre du SMSI TechShop SAS*
*Méthode : EBIOS RM simplifié — ISO 27005*
