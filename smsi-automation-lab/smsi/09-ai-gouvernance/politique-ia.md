# Politique d'Usage Responsable de l'Intelligence Artificielle — TechShop SAS
**Version :** 1.0
**Date :** Juin 2026
**Auteur :** Dorian Poncelet (Consultant GRC)
**Approuvée par :** Marie Laurent, Directrice Générale
**Statut :** Validé
**Référence :** AI Act UE 2024/1689 / ISO/IEC 42001:2023 / RGPD Art. 22

---

## Préambule

L'intelligence artificielle est déjà présente dans nos outils quotidiens — souvent sans qu'on le réalise. Les recommandations produits de notre site, le filtre anti-fraude de Stripe, le scoring de prospects dans HubSpot : ce sont des systèmes qui prennent des décisions ou influencent nos clients de façon automatisée.

Cette politique ne vise pas à freiner l'adoption de l'IA chez TechShop. Elle vise à s'assurer qu'on sait ce qu'on utilise, pourquoi on l'utilise, et que nos clients et employés sont traités équitablement — y compris quand c'est un algorithme qui décide.

Le règlement européen sur l'IA (AI Act) entre en application progressive jusqu'en 2027. TechShop choisit d'anticiper, non par obligation légale immédiate, mais parce que nos clients B2B grands comptes vont nous poser ces questions dans leurs appels d'offres.

---

## 1. Périmètre

Cette politique s'applique à :
- Tous les systèmes IA utilisés par TechShop SAS, qu'ils soient intégrés à nos outils (Stripe, HubSpot, Google) ou utilisés de façon autonome
- L'usage d'outils IA génératifs par les employés dans le cadre professionnel (ChatGPT, Copilot, Gemini, Claude...)
- Tout futur système IA envisagé avant son déploiement

---

## 2. Principes directeurs

### 2.1 Transparence envers les clients
Nos clients ont le droit de savoir quand une décision les concernant implique un système automatisé. Cela inclut :
- Le filtrage de fraude sur leurs paiements
- Les recommandations de produits
- Le ciblage publicitaire basé sur leur comportement

Nous ne cachons pas que nous utilisons ces technologies. Nous l'indiquons clairement dans notre politique de confidentialité et sur notre site.

### 2.2 Supervision humaine
Aucune décision automatisée ayant un impact significatif sur un client ne reste sans recours humain. En pratique :
- Une transaction refusée par Stripe peut être réexaminée par le DSI
- Un client qui conteste une décision automatisée obtient une réponse humaine dans les 48h

### 2.3 Non-discrimination
Les systèmes IA que nous déployons ne doivent pas produire de résultats discriminatoires sur la base de l'origine, du genre, de l'âge ou de tout autre critère protégé. Quand nous n'avons pas la visibilité sur un modèle tiers, nous nous appuyons sur les certifications du fournisseur et le DPA.

### 2.4 Minimisation des données
Un système IA ne traite que les données nécessaires à sa fonction. Nous n'enrichissons pas les profils clients au-delà de ce qui est utile au service.

### 2.5 Responsabilité
Thomas Rivet (DSI) est le référent technique des systèmes IA. Sophie Blanc (DPO) est responsable de leur conformité RGPD et AI Act. Marie Laurent (DG) valide tout nouveau déploiement IA.

---

## 3. Règles d'usage — Outils IA génératifs (employés)

L'usage d'outils IA génératifs (ChatGPT, Copilot, Claude, Gemini...) par les employés est autorisé dans le cadre professionnel sous conditions :

### Ce qui est autorisé
- Rédaction d'emails, de documents, de résumés à partir d'informations non confidentielles
- Aide à la programmation, débogage de code
- Traduction de documents internes (niveau "Interne")
- Brainstorming et recherche d'idées

### Ce qui est interdit
- **Saisir des données personnelles de clients** (emails, adresses, commandes) dans un outil IA tiers
- **Saisir des données RH** (salaires, évaluations, informations médicales) dans un outil IA tiers
- **Saisir des informations confidentielles** (contrats fournisseurs, données financières non publiques)
- **Présenter un contenu généré par IA comme personnel** dans un contexte professionnel externe (offres commerciales, communications officielles) sans validation humaine

### Pourquoi ces règles
Quand vous tapez des données dans ChatGPT ou n'importe quel outil IA en ligne, vous les envoyez sur des serveurs tiers. Même si l'outil prétend ne pas entraîner ses modèles avec vos données, vous n'avez aucun moyen de le vérifier. Une fuite de données clients via un outil IA = violation RGPD + responsabilité TechShop.

### En pratique
Si tu as besoin d'un outil IA pour un usage professionnel, parle-en à Thomas Rivet. Il peut proposer des alternatives conformes (Microsoft 365 Copilot avec DPA, ou des outils avec traitement en UE).

---

## 4. Processus d'approbation — Nouveau système IA

Avant tout déploiement d'un nouveau système ou fonctionnalité IA :

```
Étape 1 — Identification
  → Qui propose le système ? Pour quel usage ?
  → Est-ce une fonctionnalité d'un outil existant ou un nouveau service ?

Étape 2 — Évaluation (DSI + DPO)
  → Niveau de risque AI Act (inventaire-systemes-ia.md)
  → Données personnelles impliquées ? (RGPD)
  → DPA disponible chez le fournisseur ?
  → Supervision humaine possible ?

Étape 3 — Décision
  → Risque minimal + DPA OK → DSI décide
  → Risque limité ou haut risque → Validation DG requise
  → Pratique interdite → Refus systématique

Étape 4 — Documentation
  → Ajout à l'inventaire des systèmes IA
  → Mise à jour politique de confidentialité si nécessaire
  → Information des employés concernés
```

---

## 5. Surveillance et revue

| Action | Fréquence | Responsable |
|---|---|---|
| Revue de l'inventaire des systèmes IA | Annuelle | DSI + DPO |
| Vérification des DPA fournisseurs IA | Annuelle | DPO |
| Formation employés sur usage IA responsable | Annuelle | DSI + RH |
| Revue de la présente politique | Annuelle | DG + Consultant GRC |

---

## 6. En cas d'incident impliquant un système IA

Un incident impliquant un système IA (décision erronée, biais détecté, fuite de données via outil IA) suit la procédure générale de gestion des incidents (`smsi/05-plan-traitement/procedure-incidents.md`) avec un qualificatif "IA" dans le registre des incidents.

Points spécifiques aux incidents IA :
- Conserver les inputs et outputs du système au moment de l'incident (preuve)
- Notifier le fournisseur du système IA concerné
- Évaluer si des personnes ont été impactées (correction possible ?)
- Documenter pour la revue annuelle

---

## Signature

| Rôle | Nom | Date |
|---|---|---|
| Directrice Générale | Marie Laurent | Juin 2026 |
| DSI — Référent technique IA | Thomas Rivet | Juin 2026 |
| DPO — Référente conformité IA | Sophie Blanc | Juin 2026 |

---

*Document classifié : INTERNE*
*Prochaine révision : Juin 2027 ou lors de l'entrée en vigueur de nouvelles obligations AI Act*
