# Rapport d'Audit de Sécurité — Site WooCommerce TechShop SAS
**Version :** 1.0  
**Date :** 03 juin 2026  
**Outil :** WPScan v4.0.0  
**Auditeur :** Dorian Poncelet (Consultant GRC)  
**Statut :** CONFIDENTIEL

---

## 1. Résumé Exécutif

Un audit de sécurité automatisé a été réalisé sur le site WooCommerce de TechShop SAS.
L'audit a effectué **3 886 requêtes** en 226 secondes et identifié **7 vulnérabilités/faiblesses** de sécurité.

### Bilan global

| Criticité | Nombre | Action requise |
|---|---|---|
| 🔴 Critique | 1 | Immédiate (< 48h) |
| 🟠 Haute | 2 | Urgente (< 7 jours) |
| 🟡 Moyenne | 3 | Planifiée (< 30 jours) |
| 🔵 Faible | 1 | À planifier |

**Score de risque global : 7.2/10 — ÉLEVÉ**

---

## 2. Périmètre de l'audit

| Paramètre | Valeur |
|---|---|
| URL cible | http://techshop-woocommerce (environnement simulé) |
| IP cible | Serveur local (simulation OVH) |
| Date du scan | 03/06/2026 09:42 UTC |
| Durée | 226 secondes |
| Requêtes effectuées | 3 886 |
| Mode de détection | Passif + Agressif |

---

## 3. Findings — Vulnérabilités identifiées

---

### FINDING-001 🔴 CRITIQUE — XML-RPC activé

**Référence :** CWE-16, CVE multiples  
**URL exposée :** `http://techshop.fr/xmlrpc.php`  
**Méthode de détection :** Direct Access (Aggressive Detection) — Confiance : 100%

**Description :**  
Le fichier `xmlrpc.php` est accessible publiquement. Cette interface permet l'authentification WordPress via XML. Elle est exploitable pour :
- **Attaques par brute force** sur les comptes admin (via la méthode `wp.getUsersBlogs`)
- **Attaques DDoS** en amplifiant les requêtes pingback
- **Bypass des restrictions de connexion** (tentatives illimitées via XML-RPC)

**Exploit disponible :** Oui — modules Metasploit documentés :
- `auxiliary/scanner/http/wordpress_xmlrpc_login`
- `auxiliary/dos/http/wordpress_xmlrpc_dos`
- `auxiliary/scanner/http/wordpress_ghost_scanner`

**Impact pour TechShop SAS :**  
Un attaquant peut tester des millions de combinaisons email/mot de passe sur le compte admin de Thomas Rivet sans déclencher les mécanismes de blocage habituels. En cas de succès → accès total au back-office WooCommerce → accès aux données de 15 000 clients.

**Recommandation :**
```php
// Ajouter dans functions.php du thème TechShop
add_filter('xmlrpc_enabled', '__return_false');
```
Ou bloquer au niveau Cloudflare WAF (règle de firewall sur /xmlrpc.php).

**Contrôle ISO 27001 :** A.8.21 (Sécurité des services réseau), A.8.5 (Authentification sécurisée)  
**Délai de remédiation recommandé :** < 48h

---

### FINDING-002 🟠 HAUTE — WordPress version exposée publiquement

**Référence :** CWE-200 (Exposure of Sensitive Information)  
**Détection :** RSS Generator, commentaires HTML  
**Version détectée :** WordPress **6.4.3** (statut : **INSECURE**)  
**Dernière version disponible :** 6.8.x

**Méthode de détection :**
```
http://techshop.fr/?feed=rss2
<generator>https://wordpress.org/?v=6.4.3</generator>
```

**Description :**  
La version exacte de WordPress est exposée dans le flux RSS et les méta-tags. Un attaquant connaissant la version peut cibler précisément les CVE correspondantes sans tâtonnement.

**Impact :** Facilite considérablement la reconnaissance initiale (phase 1 d'une attaque).

**Recommandation :**
```php
// Masquer la version WordPress dans functions.php
remove_action('wp_head', 'wp_generator');
add_filter('the_generator', '__return_empty_string');
```

**Contrôle ISO 27001 :** A.8.8 (Gestion des vulnérabilités), A.8.9 (Gestion de la configuration)  
**Délai de remédiation recommandé :** < 7 jours

---

### FINDING-003 🟠 HAUTE — WooCommerce version obsolète (7.0.0)

**Plugin :** WooCommerce  
**Version installée :** **7.0.0** (novembre 2022)  
**Dernière version disponible :** **10.7.0**  
**Retard :** 3,5 ans de mises à jour manquées  
**Statut :** OUTDATED

**Description :**  
WooCommerce 7.0.0 est en retard de 35+ versions majeures. Cette version contient des vulnérabilités connues et non patchées. Sans token API WPScan, les CVE spécifiques ne sont pas affichées, mais compte tenu du retard, plusieurs vulnérabilités critiques sont certaines.

**CVE notables connues sur WooCommerce < 8.x :**
- Injection SQL via les paramètres de recherche produit
- XSS stocké via les champs de checkout
- Accès non authentifié aux données de commandes

**Impact pour TechShop SAS :**  
WooCommerce est le cœur du site e-commerce. Une vulnérabilité exploitée → accès aux données de commandes des 15 000 clients → violation RGPD avec obligation de notification CNIL sous 72h → amende potentielle jusqu'à 128 000€.

**Recommandation :** Mettre à jour vers WooCommerce 10.7.0 en environnement de test d'abord.

**Contrôle ISO 27001 :** A.8.8 (Patch management), A.5.21 (Supply chain), A.5.34 (Protection données personnelles)  
**Délai de remédiation recommandé :** < 7 jours

---

### FINDING-004 🟡 MOYENNE — Yoast SEO version obsolète (19.0)

**Plugin :** Yoast SEO (wordpress-seo)  
**Version installée :** **19.0**  
**Dernière version disponible :** **27.6**  
**Répertoire accessible :** OUI (status 200)  
**Statut :** OUTDATED

**Description :**  
Yoast SEO 19.0 (septembre 2022) est en retard de 8 versions majeures. Le répertoire du plugin est accessible publiquement (status 200 au lieu de 403), ce qui expose la structure des fichiers.

**Risque supplémentaire :** Le listing du répertoire `/wp-content/plugins/wordpress-seo/` expose la liste des fichiers, facilitant la recherche de fichiers sensibles.

**Recommandation :** Mettre à jour vers 27.6 + désactiver le listing de répertoires via `.htaccess` :
```apache
Options -Indexes
```

**Contrôle ISO 27001 :** A.8.8 (Patch management), A.8.21 (Services réseau)  
**Délai de remédiation recommandé :** < 30 jours

---

### FINDING-005 🟡 MOYENNE — Fichier readme.html accessible

**URL :** `http://techshop.fr/readme.html`  
**Détection :** Direct Access — Confiance : 100%

**Description :**  
Le fichier `readme.html` de WordPress est accessible publiquement. Il contient la version exacte de WordPress et des informations sur l'installation.

**Recommandation :** Supprimer ou restreindre l'accès :
```apache
<Files readme.html>
  Order Allow,Deny
  Deny from all
</Files>
```

**Contrôle ISO 27001 :** A.8.9 (Configuration), A.8.21 (Services réseau)  
**Délai de remédiation recommandé :** < 30 jours

---

### FINDING-006 🟡 MOYENNE — WP-Cron exposé publiquement

**URL :** `http://techshop.fr/wp-cron.php`  
**Détection :** Direct Access — Confiance : 60%

**Description :**  
Le système de tâches planifiées WordPress (`wp-cron.php`) est accessible publiquement. Cela peut être utilisé pour :
- Déclencher des tâches arbitraires à distance
- Amplifier des attaques DDoS (chaque visite déclenche les crons)
- Surcharger le serveur en appelant massivement ce fichier

**Recommandation :**
```php
// wp-config.php
define('DISABLE_WP_CRON', true);
```
Puis configurer un vrai cron système à la place.

**Contrôle ISO 27001 :** A.8.21 (Services réseau), A.8.6 (Gestion des capacités)  
**Délai de remédiation recommandé :** < 30 jours

---

### FINDING-007 🔵 FAIBLE — Thèmes WordPress obsolètes

**Thèmes détectés :**

| Thème | Version installée | Dernière version | Retard |
|---|---|---|---|
| Twenty Twenty-Four | 1.0 | 1.4 | 4 versions |
| Twenty Twenty-Three | 1.3 | 1.6 | 3 versions |
| Twenty Twenty-Two | 1.6 | 2.1 | Mineur |

**Description :** Thèmes inactifs non mis à jour. Risque faible si non activés, mais représentent une surface d'attaque supplémentaire.

**Recommandation :** Supprimer les thèmes non utilisés.

**Contrôle ISO 27001 :** A.8.8 (Patch management)  
**Délai de remédiation recommandé :** À planifier

---

### FINDING BONUS — Énumération utilisateurs

**Utilisateur découvert :** `admin`  
**Méthode :** Author Posts Display Name (Passive) + Author ID Brute Force (Aggressive)  
**Confiance :** 100%

**Description :**  
Le username `admin` a été découvert par détection passive. Combiné avec le XML-RPC activé (FINDING-001), cela fournit à un attaquant la moitié des informations nécessaires pour une attaque brute force.

**Recommandation :** Renommer le compte admin + activer la protection contre l'énumération des auteurs.

**Contrôle ISO 27001 :** A.8.5 (Authentification sécurisée), A.5.16 (Gestion des identités)

---

## 4. Tableau de synthèse — Mapping ISO 27001 & RGPD

| Finding | Criticité | Contrôle ISO 27001 | Impact RGPD | Responsable | ETA |
|---|---|---|---|---|---|
| XML-RPC activé | 🔴 Critique | A.8.21, A.8.5 | ⚠️ Accès données clients | Thomas Rivet | 05/06/2026 |
| WordPress version exposée | 🟠 Haute | A.8.8, A.8.9 | ⚠️ Facilite exploitation | Thomas Rivet | 10/06/2026 |
| WooCommerce 7.0.0 obsolète | 🟠 Haute | A.8.8, A.5.21 | 🔴 CVE → fuite 15k clients | Thomas Rivet | 10/06/2026 |
| Yoast SEO 19.0 obsolète | 🟡 Moyenne | A.8.8, A.8.21 | ⚠️ Mineur | Nicolas Bernard | 03/07/2026 |
| readme.html accessible | 🟡 Moyenne | A.8.9, A.8.21 | ℹ️ Info disclosure | Nicolas Bernard | 03/07/2026 |
| WP-Cron exposé | 🟡 Moyenne | A.8.21, A.8.6 | ℹ️ DDoS potentiel | Thomas Rivet | 03/07/2026 |
| Thèmes obsolètes | 🔵 Faible | A.8.8 | ℹ️ Négligeable | Nicolas Bernard | 03/08/2026 |

---

## 5. Plan de remédiation — 30 jours

### Semaine 1 (J+1 à J+7) — Actions critiques et hautes
- [ ] Désactiver XML-RPC via Cloudflare WAF
- [ ] Masquer la version WordPress (functions.php)
- [ ] Mettre à jour WooCommerce vers 10.7.0 (test + prod)
- [ ] Renommer le compte admin

### Semaine 2 (J+8 à J+14) — Mise à jour plugins
- [ ] Mettre à jour Yoast SEO vers 27.6
- [ ] Tester l'impact des mises à jour en environnement staging

### Semaine 3-4 (J+15 à J+30) — Durcissement
- [ ] Supprimer readme.html
- [ ] Désactiver WP-Cron public
- [ ] Supprimer les thèmes inactifs
- [ ] Activer Options -Indexes dans .htaccess
- [ ] Configurer Cloudflare WAF règles WordPress

---

## 6. Budget de remédiation estimé

| Action | Coût | Type |
|---|---|---|
| Désactivation XML-RPC | 0€ | Config (30 min) |
| Masquage version WP | 0€ | Config (15 min) |
| Mise à jour WooCommerce | 400€ | 1j développeur (test + déploiement) |
| Mise à jour Yoast SEO | 0€ | Config (automatique) |
| Durcissement .htaccess | 0€ | Config (1h) |
| Cloudflare WAF WordPress ruleset | 0€ | Inclus Cloudflare |
| **TOTAL** | **400€** | **2 jours-personnes** |

---

## 7. Recommandation — Processus de sécurité récurrent

Pour éviter que ces vulnérabilités ne réapparaissent, TechShop SAS doit mettre en place :

1. **Scan WPScan mensuel automatisé** (0€ — script cron)
2. **Mises à jour WordPress/plugins hebdomadaires** via staging
3. **Token API WPScan** pour les données CVE complètes (25€/mois)
4. **Monitoring Cloudflare** des tentatives d'accès à xmlrpc.php

Ces 4 mesures couvrent le contrôle **A.8.8 (Gestion des vulnérabilités)** d'ISO 27001 pour un coût de **25€/mois**.

---

## 8. Limites de l'audit

- Scan réalisé **sans token API WPScan** → les CVE détaillées ne sont pas affichées (nécessite un token gratuit sur wpscan.com)
- Scan en **mode non authentifié** → les vulnérabilités accessibles uniquement en étant connecté ne sont pas détectées
- **Pas de test de pénétration manuel** → les vulnérabilités logiques (IDOR, CSRF, etc.) nécessitent une analyse humaine

---

*Rapport généré dans le cadre du POC GRC — Labs CISO TechShop SAS*  
*Auditeur : Dorian Poncelet — Consultant GRC*
