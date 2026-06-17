# Checklist de Réponse à Incident — 72h CNIL
**TechShop SAS | INC-2026-001**

> 🎯 **Objectif de ce document**
> Guide opérationnel à utiliser dès la détection d'une violation de données.
> Chaque case doit être cochée avec l'heure et la personne responsable.
> Ce document prouve à la CNIL que TechShop SAS a suivi un processus structuré.

---

## ⏱️ H+0 à H+2 — Détection et confirmation

> **Pourquoi cette phase est critique ?**
> Les premières minutes déterminent l'ampleur des dégâts. L'objectif est de
> **stopper l'hémorragie** avant tout — pas d'analyser, pas de communiquer.

- [x] **02h17** Alerte détectée — Thomas Rivet
- [x] **02h25** Isolation du serveur compromis — Thomas Rivet
- [x] **02h30** Confirmation : violation de données personnelles avérée — Thomas Rivet
- [x] **02h30** Ouverture du registre d'incident (INC-2026-001) — Sophie Blanc
- [x] **02h35** Préservation des preuves (logs, captures mémoire) — Thomas Rivet
- [x] **02h45** Blocage IP attaquante sur Cloudflare — Thomas Rivet
- [ ] ~~Vérifier si d'autres systèmes sont compromis~~ — Thomas Rivet

---

## ⏱️ H+2 à H+6 — Évaluation et escalade

> **Pourquoi escalader rapidement ?**
> La DG doit être informée pour prendre la décision de notification.
> Un consultant ou un avocat RGPD peut être nécessaire.
> Chaque heure compte pour respecter le délai des 72h.

- [x] **07h00** Information de Marie Laurent (DG) — Sophie Blanc
- [x] **07h30** Évaluation du périmètre de la violation — Sophie Blanc + Thomas Rivet
- [x] **08h00** Activation cellule de crise (DG + DSI + DPO) — Marie Laurent
- [x] **08h30** Décision : notification CNIL obligatoire — Marie Laurent
- [ ] Contacter l'assureur cyber (si contrat) — Marie Laurent
- [ ] Contacter avocat RGPD si nécessaire — Marie Laurent

---

## ⏱️ H+6 à H+24 — Préparation de la notification

> **Ce que la CNIL examine en priorité**
> Elle vérifie que vous avez bien identifié QUI est touché et QUOI a fuité.
> Une notification incomplète vaut mieux qu'une notification tardive —
> vous pouvez la compléter dans les 30 jours suivants.

- [x] **09h00** Identification des catégories de données exposées — Sophie Blanc
- [x] **09h30** Dénombrement des personnes concernées (~15 000) — Thomas Rivet
- [x] **10h00** Évaluation de la gravité (score 11/15 = élevée) — Sophie Blanc
- [ ] Rédaction de la notification CNIL — Sophie Blanc
- [ ] Validation de la notification par Marie Laurent (DG) — Marie Laurent
- [ ] Soumission sur notifications.cnil.fr — Sophie Blanc

---

## ⏱️ H+24 à H+72 — Communication aux personnes concernées

> **Dois-je toujours prévenir les clients ?**
> NON — seulement si le risque pour leurs droits est ÉLEVÉ.
> Dans notre cas : oui. Email + adresse + historique commandes exposés.
> Le message doit être clair, honnête et donner des conseils concrets.

- [ ] Rédaction de l'email aux 15 000 clients — Sophie Blanc
- [ ] Validation email par Marie Laurent — Marie Laurent
- [ ] Envoi de l'email via HubSpot — Camille Dupont (Marketing)
- [ ] Publication d'un avis sur le site TechShop SAS — Nicolas Bernard
- [ ] Mise en place d'une FAQ clients sur l'incident — Laura Petit

---

## ⏱️ H+72 et au-delà — Remédiation et suivi

> **La violation est notifiée — et après ?**
> La CNIL peut demander des informations complémentaires dans les 30 jours.
> Vous devez prouver que le problème est corrigé et que vous avez tiré les leçons.

- [ ] **J+7** Patch WooCommerce 10.7.0 déployé en production — Thomas Rivet
- [ ] **J+7** Rapport forensique complet — Thomas Rivet
- [ ] **J+14** Post-mortem incident — Équipe complète
- [ ] **J+14** Mise à jour du SMSI (contrôle A.8.8) — Dorian Poncelet
- [ ] **J+30** Complément de notification CNIL si nécessaire — Sophie Blanc
- [ ] **J+30** Clôture de l'incident — Sophie Blanc

---

## 📞 Contacts d'urgence

| Interlocuteur | Contact | Rôle |
|---|---|---|
| **CNIL** | notifications.cnil.fr | Portail notification en ligne |
| **CNIL** | 01 53 73 22 22 | Standard (heures ouvrées) |
| **CERT-FR** | cert-fr.ssi.gouv.fr | Signalement incident cyber |
| **Cybermalveillance** | cybermalveillance.gouv.fr | Assistance PME |
| **Assureur cyber** | À compléter | Déclaration sinistre |
| **Avocat RGPD** | À compléter | Conseil juridique |

---

*TechShop SAS — Document confidentiel*
