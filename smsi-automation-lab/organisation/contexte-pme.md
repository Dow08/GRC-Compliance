# Contexte Organisation — TechShop SAS
**Version :** 1.0 | **Date :** juin 2026 | **Statut :** Référence projet

---

## Identité

| Champ | Valeur |
|---|---|
| Raison sociale | TechShop SAS |
| Secteur | E-commerce — matériel gaming et électronique grand public |
| Marché | B2C (particuliers) + B2B (revendeurs indépendants) |
| Siège social | 12 rue des Innovations, 31000 Toulouse |
| Entrepôt logistique | Zone Industrielle de Labège, 31670 |
| Effectif | 47 salariés |
| Chiffre d'affaires | 3,2M€ (2025) |
| Clients actifs | ~15 000 (base RGPD) |
| Fondée en | 2018 |

---

## Organisation interne

| Rôle | Nom | Responsabilités SMSI |
|---|---|---|
| Directrice Générale | Marie Laurent | Sponsor SMSI, engagement de la direction |
| Directeur des Systèmes d'Information | Thomas Rivet | Responsable technique SMSI |
| Délégué à la Protection des Données | Sophie Blanc | RGPD, registre des traitements |
| Responsable Logistique | Karim Benali | Actifs physiques, entrepôt |
| Responsable Marketing | Léa Moreau | Données clients, campagnes |
| Comptable / RH | Nathalie Perrin | Données RH, paie |

---

## Infrastructure technique

### Serveurs et hébergement

| Composant | Solution | Hébergeur | Localisation |
|---|---|---|---|
| Serveur web e-commerce | VPS OVH — 4 vCPU / 16 Go RAM / 200 Go SSD | OVH Cloud | Roubaix, France |
| Serveur applicatif (ERP) | VPS OVH — 2 vCPU / 8 Go RAM / 100 Go SSD | OVH Cloud | Roubaix, France |
| Base de données (WooCommerce) | MySQL 8.0 sur serveur web | OVH Cloud | Roubaix, France |
| ERP | Odoo 17 Community | OVH Cloud | Roubaix, France |

### Services SaaS

| Service | Fournisseur | Usage | Données traitées |
|---|---|---|---|
| CRM | HubSpot (Free/Starter) | Gestion contacts, pipeline commercial | Contacts B2B, historique |
| Paiement | Stripe + PayPal | Paiement en ligne | Données bancaires tokenisées |
| Email / Collaboration | Google Workspace Business Starter | Email pro, Drive, Meet | Emails internes, documents |
| Stockage / Backup | AWS S3 (bucket us-east-1) | Sauvegardes nocturnes | Backup BDD, fichiers |
| CDN / WAF | Cloudflare (Free) | Protection DDoS, cache | Logs d'accès |
| VPN | WireGuard (auto-hébergé) | Accès admin aux serveurs | Authentification admin |
| Supervision | Grafana + Prometheus | Monitoring serveurs | Métriques système |

### Connectivité

- **Accès admin serveurs :** VPN WireGuard (clés Ed25519, MFA non déployé — point de non-conformité)
- **Accès employés :** Internet (Google Workspace + SaaS), pas de réseau d'entreprise unifié
- **Téléphonie :** Mobile (forfaits personnels — BYOD — point de risque)

---

## Données traitées

| Catégorie | Volume | Sensibilité | Localisation |
|---|---|---|---|
| Données clients (identité, email, adresse) | ~15 000 personnes | Confidentiel | OVH FR + HubSpot |
| Historique commandes | ~45 000 commandes | Confidentiel | OVH FR |
| Données bancaires | Tokenisées via Stripe | Secret → délégué Stripe | Stripe US |
| Données RH (contrats, fiches de paie) | 47 dossiers | Secret | Google Drive + Comptable |
| Données marketing (newsletter) | ~8 000 abonnés | Interne | HubSpot |
| Logs applicatifs | Continu | Interne | OVH FR + Cloudflare |
| Sauvegardes | Quotidiennes | Confidentiel | AWS S3 us-east-1 ⚠️ |

> ⚠️ Les sauvegardes AWS S3 en us-east-1 constituent un transfert de données hors UE — point de non-conformité RGPD identifié.

---

## Enjeux de conformité

### ISO 27001:2022
TechShop vise la certification ISO 27001 dans le cadre d'un appel d'offres B2B (client grand compte exige le certificat pour 2027). Le SMSI est à construire de zéro — aucune politique de sécurité formalisée n'existe actuellement.

### NIS2 (Directive EU 2022/2555)
TechShop est une PME non classée "entité essentielle" ou "entité importante" au sens strict. Cependant, sa dépendance à des fournisseurs critiques (Stripe, Cloudflare) et son activité de service numérique la placent dans le radar de la directive. Les mesures de l'Article 21 doivent être documentées.

### RGPD (Règlement EU 2016/679)
TechShop traite les données personnelles de ~15 000 clients et 47 salariés. Points critiques :
- **Transfert hors UE :** Sauvegardes AWS us-east-1 (non couvert par une décision d'adéquation sans clauses contractuelles types)
- **Sous-traitants :** HubSpot (US), Stripe (US), Google Workspace (US) → DPA à vérifier
- **Exercice des droits :** Aucune procédure formalisée pour les demandes d'accès/suppression
- **Délais de conservation :** Non définis pour les données clients inactifs

### PCI-DSS
TechShop n'est pas directement en scope PCI-DSS car elle ne stocke, ne traite, ni ne transmet les données de cartes bancaires (déléguées à Stripe). Elle est en **SAQ A** (questionnaire minimal). À documenter.

---

## Risques principaux (synthèse initiale)

| # | Risque | Vraisemblance | Impact |
|---|---|---|---|
| R01 | Ransomware sur les serveurs OVH | Élevée | Critique |
| R02 | Fuite de données clients (breach RGPD) | Moyenne | Critique |
| R03 | Compromission compte Google Workspace admin | Moyenne | Élevé |
| R04 | Indisponibilité Stripe (fournisseur critique) | Faible | Critique |
| R05 | Accès non autorisé ERP Odoo (ex-employé) | Faible | Élevé |
| R06 | Injection SQL WooCommerce | Faible | Élevé |
| R07 | Non-conformité RGPD transferts AWS us-east-1 | Certaine | Moyen |

*Analyse complète dans `smsi/03-analyse-risques/registre-risques.md`*
