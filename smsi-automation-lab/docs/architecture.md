# Architecture Sécurisée — TechShop SAS
**Version :** 2.0
**Date :** Juin 2026
**Auteur :** Dorian Poncelet (Consultant GRC)
**Statut :** Validé
**Référence :** ISO 27001:2022 A.8.20, A.8.21, A.8.22 / ANSSI Guide Hygiène Informatique

---

## Principes de conception

### Security by Design
La sécurité n'est pas ajoutée après coup — elle est intégrée dès la conception de chaque composant.
Chaque flux réseau est justifié, chaque exposition est délibérée, chaque accès est authentifié.

### Defense in Depth (Défense en profondeur)
Aucune couche de sécurité n'est suffisante seule. L'architecture empile plusieurs contrôles
indépendants : un attaquant qui contourne Cloudflare tombe sur le firewall OVH, puis sur la
segmentation réseau, puis sur l'authentification applicative, puis sur le chiffrement des données.

```
Internet → [Cloudflare WAF] → [Firewall périmétrique] → [DMZ] → [Firewall interne]
        → [Tier applicatif] → [Firewall DB] → [Base de données]

Chaque couche est indépendante. La compromission d'une couche ne donne pas accès à la suivante.
```

### Hub and Spoke — Administration centralisée
Tous les accès d'administration transitent par un point unique (VPN WireGuard).
Aucun port d'administration (SSH, RDP, console) n'est exposé directement sur Internet.

```
Administrateur → [VPN WireGuard Hub] → Spoke 1 : Serveurs OVH
                                     → Spoke 2 : Console AWS
                                     → Spoke 3 : OVH Manager
                                     → Spoke 4 : Cloudflare Dashboard
```

---

## Architecture réseau — Vue d'ensemble

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                              INTERNET                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
                                    │
                          HTTPS/TLS 1.3 uniquement
                          Ports 80 (redirect) + 443
                                    │
╔══════════════════════════════════════════════════════════════════════════════╗
║  COUCHE 1 — PROTECTION PÉRIMÉTRIQUE (Cloudflare)                            ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │  Cloudflare (Proxy inverse + WAF + DDoS)                            │    ║
║  │  • WAF : règles OWASP Top 10 (mode BLOCK)                           │    ║
║  │  • Anti-DDoS : L3/L4/L7                                             │    ║
║  │  • Rate limiting : 100 req/min par IP                                │    ║
║  │  • Bot management : challenge sur comportements suspects             │    ║
║  │  • IP reputation : blocage des plages connues malveillantes          │    ║
║  │  • TLS termination : TLS 1.2 minimum, TLS 1.3 par défaut            │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
╚══════════════════════════════════════════════════════════════════════════════╝
                                    │
                          HTTPS (re-chiffré Cloudflare → OVH)
                          IP source : plages Cloudflare uniquement
                                    │
╔══════════════════════════════════════════════════════════════════════════════╗
║  COUCHE 2 — FIREWALL PÉRIMÉTRIQUE OVH                                       ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │  OVH Network Firewall (anti-spoofing + filtrage entrant/sortant)     │    ║
║  │                                                                      │    ║
║  │  Règles ENTRANTES autorisées :                                       │    ║
║  │    ACCEPT  TCP 443   depuis plages IP Cloudflare uniquement          │    ║
║  │    ACCEPT  UDP 51820 depuis IP admin VPN uniquement (WireGuard)      │    ║
║  │    DROP    ALL       tout le reste                                   │    ║
║  │                                                                      │    ║
║  │  Règles SORTANTES autorisées :                                       │    ║
║  │    ACCEPT  TCP 443   vers Internet (mises à jour, APIs tierces)      │    ║
║  │    ACCEPT  TCP 5432  vers subnet DB uniquement (PostgreSQL)          │    ║
║  │    ACCEPT  TCP 443   vers AWS S3 eu-west-3 (backups)                 │    ║
║  │    DROP    ALL       tout le reste                                   │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
╚══════════════════════════════════════════════════════════════════════════════╝
                                    │
                          Trafic filtré → DMZ uniquement
                                    │
╔══════════════════════════════════════════════════════════════════════════════╗
║  COUCHE 3 — DMZ (Zone Démilitarisée) — VLAN 10                              ║
║                                                                              ║
║  Principe : les serveurs exposés sur Internet sont isolés des serveurs       ║
║  internes. Une compromission de la DMZ ne donne pas accès au tier DB.        ║
║                                                                              ║
║  ┌──────────────────────┐    ┌──────────────────────────────────────────┐   ║
║  │  WooCommerce Srv 1   │    │  WooCommerce Srv 2 (Load Balancing)      │   ║
║  │  VPS OVH — Roubaix   │    │  VPS OVH — Roubaix                       │   ║
║  │                      │    │                                          │   ║
║  │  • Nginx (reverse    │    │  • Même config                           │   ║
║  │    proxy interne)    │    │  • Failover automatique                  │   ║
║  │  • PHP-FPM isolé     │    │                                          │   ║
║  │  • WordPress/Woo     │    │                                          │   ║
║  │  • Logs applicatifs  │    │                                          │   ║
║  └──────────┬───────────┘    └──────────────────────────────────────────┘   ║
║             │                                                                ║
║  INTERDIT depuis la DMZ :                                                    ║
║    • Accès direct à Internet (sortant bloqué sauf mises à jour)              ║
║    • Accès au VLAN administration (VLAN 30)                                  ║
║    • Accès SSH depuis Internet                                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
                                    │
                   Firewall interne (micro-segmentation)
                   ACCEPT TCP 3306/5432 depuis DMZ vers DB uniquement
                                    │
╔══════════════════════════════════════════════════════════════════════════════╗
║  COUCHE 4 — TIER APPLICATIF — VLAN 20                                       ║
║                                                                              ║
║  ┌────────────────────────────┐    ┌───────────────────────────────────┐    ║
║  │  Odoo 17 ERP               │    │  Grafana + Prometheus             │    ║
║  │  Cloud OVH — Strasbourg    │    │  (Supervision)                    │    ║
║  │                            │    │                                   │    ║
║  │  • Accès : VPN uniquement  │    │  • Accès : VPN uniquement         │    ║
║  │  • Pas d'exposition        │    │  • Collecte métriques DMZ + DB    │    ║
║  │    directe Internet        │    │  • Alertes vers DSI               │    ║
║  │  • Auth : MFA obligatoire  │    │                                   │    ║
║  └────────────┬───────────────┘    └───────────────────────────────────┘    ║
║               │                                                              ║
╚═══════════════╪══════════════════════════════════════════════════════════════╝
                │
                │  Firewall DB (deny-all par défaut)
                │  ACCEPT TCP 5432 depuis VLAN 20 uniquement
                │
╔══════════════════════════════════════════════════════════════════════════════╗
║  COUCHE 5 — TIER DONNÉES — VLAN 40 (isolé)                                  ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │  Base de données (MySQL WooCommerce + PostgreSQL Odoo)               │    ║
║  │                                                                      │    ║
║  │  • Aucune exposition Internet (zéro port ouvert vers l'extérieur)   │    ║
║  │  • Accès depuis DMZ : lecture/écriture applicative uniquement        │    ║
║  │  • Accès depuis VLAN 20 : Odoo uniquement                           │    ║
║  │  • Chiffrement at-rest : activé                                      │    ║
║  │  • Backup chiffré vers AWS S3 eu-west-3 (Object Lock activé)        │    ║
║  │  • Compte DB applicatif : privilèges minimaux (pas de DROP/ALTER)    │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
╚══════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════╗
║  VLAN 30 — RÉSEAU D'ADMINISTRATION (isolé de tous les autres VLAN)          ║
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │  VPN WireGuard (Hub)                                                 │    ║
║  │  Port UDP 51820 — seul port d'administration exposé                  │    ║
║  │                                                                      │    ║
║  │  Accès autorisé UNIQUEMENT via tunnel VPN authentifié :              │    ║
║  │    → SSH serveurs OVH (clé + MFA)                                   │    ║
║  │    → Console OVH Manager                                             │    ║
║  │    → Console AWS (MFA obligatoire)                                   │    ║
║  │    → Interface Odoo admin                                            │    ║
║  │    → Dashboard Grafana                                               │    ║
║  │    → Cloudflare Dashboard                                            │    ║
║  │                                                                      │    ║
║  │  Politique de rotation des clés : annuelle                           │    ║
║  │  Logs de connexion VPN : conservés 12 mois                          │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
╚══════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════╗
║  VLAN 50 — WIFI INVITÉS (isolé — accès Internet uniquement)                 ║
║                                                                              ║
║  • Aucun accès aux VLAN 10, 20, 30, 40                                      ║
║  • Accès Internet uniquement via NAT dédié                                  ║
║  • Débit limité (pas de saturation de la bande passante production)          ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Flux de données — Matrice de flux autorisés

| Source | Destination | Port | Protocole | Justification |
|---|---|:---:|---|---|
| Internet | Cloudflare | 443 | HTTPS/TLS 1.3 | Trafic client WooCommerce |
| Cloudflare | DMZ VLAN 10 | 443 | HTTPS (re-chiffré) | Proxy Cloudflare → WooCommerce |
| DMZ VLAN 10 | DB VLAN 40 | 3306 | MySQL chiffré | WooCommerce → BDD |
| VLAN 20 | DB VLAN 40 | 5432 | PostgreSQL chiffré | Odoo → BDD |
| VLAN 20 | DMZ VLAN 10 | 443 | HTTPS | Supervision Grafana → métriques web |
| VLAN 30 (VPN) | Tous VLAN | 22 | SSH (clé) | Administration uniquement |
| DB VLAN 40 | AWS S3 | 443 | HTTPS/TLS | Backup chiffré sortant |
| Administrateur | VLAN 30 | 51820 | WireGuard UDP | Accès admin via VPN |
| **TOUT le reste** | **TOUT** | **ALL** | **DROP** | **Deny-all par défaut** |

---

## Chiffrement — État par flux

| Flux | Chiffrement | Protocole | Certificat |
|---|:---:|---|---|
| Client → Cloudflare | ✅ | TLS 1.3 | Let's Encrypt (auto-renouvelé) |
| Cloudflare → WooCommerce | ✅ | TLS 1.2+ | Certificat Origin OVH |
| WooCommerce → BDD | ✅ | MySQL TLS | Certificat interne |
| Odoo → BDD | ✅ | PostgreSQL SSL | Certificat interne |
| Admin → VPN | ✅ | WireGuard (ChaCha20) | Clés asymétriques |
| Backup → AWS S3 | ✅ | TLS + SSE-S3 | AWS géré |
| BDD at-rest | ✅ | AES-256 | Clé gérée OVH |

---

## Segmentation VLAN — Récapitulatif

| VLAN | Nom | Contenu | Accès depuis Internet | Accès admin |
|:---:|---|---|:---:|:---:|
| 10 | DMZ | WooCommerce (web) | ✅ via Cloudflare | Via VPN uniquement |
| 20 | Applicatif | Odoo ERP, Grafana | ❌ | Via VPN uniquement |
| 30 | Administration | VPN WireGuard | UDP 51820 uniquement | C'est le point d'entrée |
| 40 | Données | BDD MySQL + PostgreSQL | ❌ | Via VPN uniquement |
| 50 | WiFi invités | Postes visiteurs | ✅ Internet uniquement | ❌ isolé |

**Règle fondamentale :** un VLAN ne peut communiquer avec un VLAN adjacent que sur les ports
strictement nécessaires. Tout autre flux est bloqué par défaut (deny-all inter-VLAN).

---

## Architecture CISO Assistant (déploiement local)

```
┌─────────────────────────────────────────────────────────┐
│              POSTE ADMINISTRATEUR (local)               │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Docker Desktop                         │   │
│  │                                                  │   │
│  │  ┌────────────┐  API  ┌────────────────────┐    │   │
│  │  │  Frontend  │◄─────►│     Backend        │    │   │
│  │  │  :3000     │       │  Django :8000      │    │   │
│  │  │  (Next.js) │       │  (REST API)        │    │   │
│  │  └────────────┘       └─────────┬──────────┘    │   │
│  │                                 │                │   │
│  │                       ┌─────────▼──────────┐    │   │
│  │                       │   PostgreSQL 15     │    │   │
│  │                       │   Volume persistant │    │   │
│  │                       └────────────────────┘    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  Réseau Docker interne (bridge isolé)                   │
│  Ports exposés uniquement sur localhost :               │
│    → :3000 (interface utilisateur)                      │
│    → :8000 (API — accès scripts Python)                 │
│  Aucun port exposé sur l'interface réseau publique      │
└─────────────────────────────────────────────────────────┘
```

**Sécurité du déploiement CISO Assistant :**
- Réseau Docker isolé — les containers ne sont pas accessibles depuis le réseau local
- PostgreSQL non exposé (port 5432 uniquement accessible inter-containers)
- Variables sensibles dans `.env` (exclu du dépôt Git via `.gitignore`)
- `DJANGO_DEBUG=False` en production
- `SECRET_KEY` générée aléatoirement (100 caractères minimum)

---

## Contrôles de sécurité — Correspondance ISO 27001

| Contrôle architectural | Contrôle ISO 27001:2022 | Risque adressé |
|---|---|---|
| Cloudflare WAF | A.8.22 — Filtrage Web | R02, R06, R15 |
| Firewall périmétrique OVH | A.8.20 — Sécurité réseau | R01, R09 |
| DMZ (VLAN 10 isolé) | A.8.21 — Sécurité services réseau | R01, R02 |
| Segmentation VLAN | A.8.20 — Sécurité réseau | R09 |
| VPN WireGuard (Hub) | A.8.20, A.6.7 — Télétravail | R13 |
| MFA sur tous les accès admin | A.8.5 — Authentification sécurisée | R03 |
| BDD isolée VLAN 40 | A.8.21 — Sécurité services réseau | R02, R05 |
| Chiffrement at-rest BDD | A.8.23 — Cryptographie | R02 |
| Backup S3 Object Lock | A.8.13 — Sauvegarde | R01, R11 |
| Logs centralisés Grafana | A.8.15 — Journalisation | R01, R02 |
| WiFi invités isolé VLAN 50 | A.8.20 — Sécurité réseau | R09 |

---

*Document produit dans le cadre du SMSI TechShop SAS — Projet portfolio GRC Automation*
*Prochaine révision : Décembre 2026*
