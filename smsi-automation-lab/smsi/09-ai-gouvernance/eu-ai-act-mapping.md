# Mapping EU AI Act — TechShop SAS
**Version :** 1.0
**Date :** Juin 2026
**Auteur :** Dorian Poncelet (Consultant GRC)
**Statut :** Validé
**Référence :** Règlement UE 2024/1689 (AI Act) — Entré en vigueur le 01/08/2024

---

## Positionnement de TechShop dans l'écosystème AI Act

L'AI Act distingue trois rôles distincts dans la chaîne de valeur de l'IA :

```
FOURNISSEUR          IMPORTATEUR        DÉPLOYEUR          UTILISATEUR FINAL
(développe l'IA)     (distribue)        (utilise l'IA)     (personne physique)
     │                    │                  │                      │
Stripe, Google,         N/A            TechShop SAS          Clients TechShop
HubSpot, Woo                           (notre rôle)
```

**TechShop SAS est exclusivement déployeur.** Elle n'a pas développé les systèmes IA qu'elle utilise.
Cela limite ses obligations mais ne l'en exempte pas — l'AI Act impose des responsabilités aux déployeurs,
notamment en termes de surveillance, de transparence envers les utilisateurs finaux et de documentation.

---

## Obligations des déployeurs selon l'AI Act

### Article 26 — Obligations des déployeurs de systèmes IA à haut risque

Les obligations qui s'appliquent à TechShop pour les systèmes potentiellement à haut risque (IA-002 Stripe) :

| Obligation | Article | Applicable TechShop | État | Action |
|---|:---:|:---:|:---:|---|
| Utiliser le système conformément aux instructions du fournisseur | 26.1 | Oui | ✅ | Stripe utilisé selon documentation |
| Assurer une supervision humaine | 26.1 | Oui | ⚠️ | Procédure de révision manuelle à formaliser |
| Surveiller le fonctionnement du système | 26.5 | Oui | ⚠️ | Monitoring des transactions bloquées à mettre en place |
| Informer les personnes concernées | 26.10 | Oui | ❌ | Mention manquante sur le site |
| Tenir un registre des activités IA | 26.6 | Oui | ❌ | Registre IA à créer (ce document) |

---

## Analyse par article — Obligations applicables à TechShop

### Titre II — Pratiques d'IA interdites (Art. 5)

TechShop n'utilise aucun système d'IA relevant des pratiques interdites :

| Pratique interdite | Concerné ? | Justification |
|---|:---:|---|
| Manipulation subliminale des comportements | Non | Les recommandations produits sont transparentes |
| Exploitation des vulnérabilités (âge, handicap) | Non | Pas de ciblage de populations vulnérables |
| Notation sociale par autorités publiques | Non | TechShop est une entreprise privée |
| Identification biométrique en temps réel | Non | Aucun système biométrique déployé |
| Profilage pour inférer des données sensibles | Non | HubSpot scoring basé sur comportement achat uniquement |

> **Conclusion Art. 5 :** TechShop SAS ne déploie aucune IA relevant des pratiques interdites. ✅

---

### Titre III — Systèmes IA à haut risque (Art. 6 + Annexe III)

L'Annexe III liste les domaines où les systèmes IA sont présumés à haut risque. Analyse pour TechShop :

| Domaine Annexe III | Système IA TechShop | Classification | Justification |
|---|---|:---:|---|
| Infrastructures critiques | Aucun | Non applicable | TechShop n'opère pas d'infrastructure critique |
| Éducation et formation | Aucun | Non applicable | Pas d'IA dans le recrutement |
| Emploi, gestion des travailleurs | Aucun | Non applicable | Pas d'IA RH automatisée |
| Accès aux services privés essentiels | **Stripe Radar** | **À évaluer** | Décision automatisée sur accès au service de paiement |
| Application de la loi | Aucun | Non applicable | |
| Gestion des migrations | Aucun | Non applicable | |
| Administration de la justice | Aucun | Non applicable | |
| Processus démocratiques | Aucun | Non applicable | |

**Stripe Radar — analyse détaillée du risque AI Act :**

La question est : le refus automatique d'une transaction constitue-t-il un "accès à des services privés essentiels" au sens de l'Annexe III, point 5(b) ?

```
Arguments pour le haut risque :
  → Le paiement en ligne est le seul moyen d'achat sur le site
  → Un refus automatique empêche concrètement l'accès au service
  → La décision est prise sans intervention humaine initiale
  → Le client n'a pas de recours automatique

Arguments contre le haut risque :
  → Il ne s'agit pas d'un service "essentiel" (santé, logement, crédit)
  → D'autres moyens de paiement existent (PayPal)
  → Stripe est responsable du système, pas TechShop
  → Le déployeur n'a pas accès au modèle de scoring
```

**Décision TechShop :** Appliquer les obligations de haut risque à titre conservatoire sur Stripe Radar,
dans l'attente des lignes directrices de la Commission européenne sur l'interprétation de l'Annexe III.
Effort de mise en conformité limité (procédure contestation + mention transparence).

---

### Titre IV — Obligations de transparence (Art. 50)

L'Article 50 impose des obligations de transparence pour certains systèmes IA, même à risque minimal.

| Obligation | Système | Applicable | État | Action |
|---|---|:---:|:---:|---|
| Informer qu'on interagit avec une IA (chatbot) | — | Non | N/A | Pas de chatbot |
| Marquer les contenus générés par IA (deepfake) | — | Non | N/A | Pas de contenu généré IA |
| Indiquer qu'un système de recommandation est utilisé | IA-001 WooCommerce | Oui | ⚠️ | Mention à ajouter |
| Indiquer l'existence d'un profilage émotionnel | — | Non | N/A | |

---

### Titre V — Modèles d'IA à usage général — GPAI (Art. 51-56)

TechShop utilise des services basés sur des GPAI (GPT-4 via HubSpot AI features, Gemini via Google Workspace).

| Usage | Fournisseur GPAI | Obligation TechShop |
|---|---|---|
| Rédaction emails marketing (HubSpot AI) | OpenAI (via HubSpot) | Transparence interne si sortie publiée |
| Résumé de données (Google Workspace AI) | Google Gemini | Vérifier que données clients ne sont pas envoyées au modèle |
| Traduction automatique (Google Translate) | Google | Risque minimal — usage ponctuel |

> **Point critique :** Vérifier que les fonctionnalités IA de HubSpot et Google Workspace ne traitent
> pas de données personnelles clients dans leurs modèles. Clause à vérifier dans les DPA respectifs.

---

## Plan de mise en conformité AI Act — TechShop SAS

### Mesures à court terme (avant août 2026)

| Action | Priorité | Effort | Responsable |
|---|:---:|---|---|
| Créer le registre des systèmes IA (ce document) | P1 | Fait ✅ | Consultant GRC |
| Procédure contestation décision Stripe Radar | P1 | 0,5 jour | DSI + DPO |
| Mention transparence recommandations WooCommerce | P2 | 0,5 jour | DSI |
| Mention profilage HubSpot dans CGU/Politique confidentialité | P2 | 0,5 jour | DPO |
| Vérifier DPA HubSpot et Google Workspace sur usage GPAI | P2 | 0,5 jour | DPO |

### Mesures à moyen terme (avant août 2027)

| Action | Priorité | Effort | Responsable |
|---|:---:|---|---|
| Revue annuelle de l'inventaire des systèmes IA | P2 | 0,5 jour | DSI + DPO |
| Formation DSI et DPO sur l'AI Act | P2 | 1 jour | Direction |
| Intégration AI Act dans la politique de sécurité | P3 | 0,5 jour | Consultant GRC |
| Questionnaire sécurité IA envoyé aux fournisseurs (Stripe, HubSpot) | P3 | 1 jour | DPO |

---

## Correspondances avec le SMSI ISO 27001

L'AI Governance n'est pas séparé du SMSI — elle s'y intègre :

| Obligation AI Act | Contrôle ISO 27001:2022 | Synergies |
|---|---|---|
| Inventaire systèmes IA | A.5.9 (Inventaire actifs) | L'inventaire IA étend l'inventaire actifs |
| Surveillance systèmes IA | A.8.16 (Surveillance) | Même infrastructure de monitoring |
| Gestion incidents IA | A.5.24–A.5.26 (Incidents) | Même procédure d'incidents |
| Droits des personnes sur IA | A.5.34 (Protection données) | Lien direct RGPD-AI Act |
| Formation IA | A.6.3 (Sensibilisation) | Intégrer IA dans la formation sécurité |
| Documentation systèmes IA | A.5.37 (Procédures documentées) | Documentation technique IA |

> **Conclusion stratégique :** Mettre en conformité le SMSI ISO 27001 couvre ~60% des obligations
> AI Act pour TechShop. Ce n'est pas un deuxième projet — c'est une extension naturelle.

---

*Document produit dans le cadre du SMSI TechShop SAS — Projet portfolio GRC Automation + AI Governance*
*Référence : Règlement UE 2024/1689 — Texte consolidé disponible sur eur-lex.europa.eu*
*Prochaine révision : Août 2026 (entrée en vigueur obligations haut risque)*
