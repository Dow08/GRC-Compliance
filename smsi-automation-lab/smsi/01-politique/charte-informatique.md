# Charte Informatique — TechShop SAS
**Version :** 1.0
**Date :** Juin 2026
**Auteur :** Dorian Poncelet (Consultant GRC)
**Approuvée par :** Marie Laurent, Directrice Générale
**Statut :** Validé — Applicable à tous les collaborateurs
**Référence :** ISO 27001:2022 A.5.10 / A.6.2 / RGPD Art. 32

---

## Préambule

Cette charte s'applique à toute personne utilisant les ressources informatiques de TechShop SAS : employés en CDI ou CDD, stagiaires, alternants, prestataires et intérimaires disposant d'un accès aux systèmes.

Elle n'est pas un texte théorique. Elle décrit des comportements concrets attendus au quotidien. Son non-respect peut entraîner des sanctions disciplinaires, voire des poursuites judiciaires si la violation cause un préjudice à TechShop SAS ou à ses clients.

---

## 1. Matériel et équipements

### Ce que TechShop met à ta disposition
Chaque collaborateur dispose d'un poste de travail (fixe ou portable), d'un accès Google Workspace et, selon son rôle, d'accès aux applications métier (Odoo, WooCommerce, HubSpot).

### Tes responsabilités
- **Tu es responsable du matériel qui t'est confié.** Une perte, un vol ou une casse doit être signalé à Thomas Rivet (DSI) dans les 24 heures.
- **Les équipements TechShop servent à travailler.** Un usage personnel occasionnel est toléré (consultation perso, musique en fond) — un usage abusif ou problématique ne l'est pas.
- **Ton poste se verrouille automatiquement après 5 minutes.** Ne désactive pas ce paramètre. Quand tu quittes ton bureau, tu verrouilles (raccourci : Windows + L sur PC, Cmd + Ctrl + Q sur Mac).
- **Tu n'installes pas de logiciel sans validation du DSI.** Y compris les extensions de navigateur. Si tu as besoin d'un outil, tu envoies un email à thomas.rivet@techshop.fr — la réponse vient en 48h.

### Travail à distance et BYOD
- L'accès aux systèmes TechShop depuis l'extérieur se fait **uniquement via le VPN WireGuard**.
- Utiliser son téléphone personnel pour accéder aux emails professionnels est autorisé avec l'appli Google Workspace. Les données TechShop ne doivent pas migrer vers d'autres applications (WhatsApp, Telegram, stockage personnel...).
- En cas de départ ou de fin de mission, les applications professionnelles sont désinstallées et les accès révoqués le jour même.

---

## 2. Mots de passe et authentification

C'est le sujet où les habitudes naturelles sont les plus dangereuses.

### Les règles non négociables
- **Tu n'utilises pas le même mot de passe partout.** Si un service quelconque est piraté et que ton mot de passe est dans la fuite, tous tes autres comptes doivent rester protégés.
- **Longueur minimum : 12 caractères** pour les comptes internes TechShop. Un mot de passe long et mémorisable ("Techshop-Toulouse-2026!") vaut mieux qu'un court et complexe impossible à retenir.
- **Le MFA est obligatoire** sur Google Workspace et sur tout service qui le propose. Ce n'est pas optionnel.
- **Tu ne communiques jamais ton mot de passe à personne** — y compris au DSI. Si Thomas a besoin d'accéder à quelque chose, il utilise ses propres identifiants d'administrateur.
- **Si tu penses que ton mot de passe a été compromis**, tu le changes immédiatement et tu envoies un email à securite@techshop.fr.

### Gestionnaire de mots de passe
TechShop encourage l'utilisation d'un gestionnaire (Bitwarden, 1Password...). C'est la seule façon réaliste d'avoir des mots de passe différents et forts partout. Le DSI peut t'aider à en configurer un.

---

## 3. Messagerie et communications

### Email
- L'adresse `@techshop.fr` est une adresse professionnelle. Elle est utilisée pour les communications liées au travail.
- **Tu ne cliques pas sur les liens dans les emails non sollicités**, même s'ils semblent venir d'un collègue, d'une banque ou d'un fournisseur connu. En cas de doute, tu appelles la personne.
- Les pièces jointes d'expéditeurs inconnus ne s'ouvrent pas. En cas d'hésitation : `securite@techshop.fr`.
- Tu ne transfères pas de données clients ou de documents confidentiels vers des adresses email personnelles.

### Comment reconnaître un phishing
Trois signaux d'alarme :
1. L'email crée une **urgence artificielle** ("Votre compte sera bloqué dans 24h")
2. Le lien pointe vers un **domaine bizarre** (techsh0p.fr, techshop-securite.net...)
3. On te demande de **saisir tes identifiants** quelque part

Si tu cliques par erreur : tu déconnectes le poste du réseau et tu appelles Thomas immédiatement. Pas d'email, pas de message — un appel direct.

---

## 4. Données et confidentialité

### La classification c'est concret
Les documents TechShop sont classés en 4 niveaux. En pratique :

| Niveau | Exemples | Ce que tu ne fais pas |
|---|---|---|
| **Public** | Catalogue produits, site web | — |
| **Interne** | Procédures internes, organigramme | Ne pas envoyer à des externes |
| **Confidentiel** | Contrats, données fournisseurs, tarifs | Ne pas envoyer sans chiffrement |
| **Secret** | Données clients, données RH, mots de passe | Accès strictement limité au besoin |

### Données clients — RGPD
TechShop gère les données personnelles de 15 000 clients. C'est une responsabilité légale.
- Tu ne télécharges pas de fichier client sur ton poste personnel ou une clé USB non chiffrée.
- Tu n'utilises pas les données clients à des fins autres que celles prévues (traitement de commande, SAV).
- Si un client te demande à exercer ses droits RGPD (accès, rectification, suppression), tu le transfères immédiatement à Sophie Blanc (DPO) : `dpo@techshop.fr`.

### Stockage et partage
- Les documents de travail se stockent sur **Google Drive TechShop**, pas sur le bureau de ton poste.
- Les clés USB ne sont pas interdites, mais elles ne contiennent pas de données clients ou RH.
- Avant d'utiliser un service cloud personnel (WeTransfer, Dropbox perso...) pour transférer un fichier pro, tu demandes au DSI — il existe des solutions validées.

---

## 5. Internet et réseaux

- La navigation sur internet depuis les équipements TechShop est filtrée. Les sites manifestement inappropriés (jeux d'argent, contenus illégaux...) sont bloqués.
- Le réseau WiFi "TechShop-Invités" est réservé aux visiteurs. Tu utilises le réseau interne.
- En déplacement, tu te connectes au réseau d'un hôtel ou d'un café **uniquement via le VPN**. Les réseaux publics sont potentiellement espionnés.

---

## 6. Incidents et signalement

**Tu n'as pas à avoir honte de signaler une erreur.** La sécurité repose sur la transparence, pas sur la perfection. Un clic sur un mauvais lien signalé dans les 5 minutes peut éviter une catastrophe. Le même clic dissimulé pendant 3 jours peut coûter des centaines de milliers d'euros.

### Quoi signaler
- Un email de phishing reçu (même si tu n'as pas cliqué)
- Un clic sur un lien suspect
- Un comportement anormal de ton poste (lenteur soudaine, fichiers qui disparaissent, pop-ups inhabituels)
- La perte ou le vol d'un équipement
- Un accès inhabituel à tes comptes (notification de connexion depuis un endroit inconnu)

### Comment signaler
**Email :** securite@techshop.fr
**Urgence (ransomware, intrusion active) :** appel direct Thomas Rivet — numéro affiché dans le bureau.

---

## 7. Départ de TechShop

Le jour de ton départ (démission, fin de contrat, licenciement) :
- Tous tes accès sont révoqués dans la journée : Google Workspace, Odoo, VPN, HubSpot.
- Les équipements prêtés sont restitués avant ta dernière heure de présence.
- Les données professionnelles stockées localement sont supprimées ou transférées.
- Les obligations de confidentialité sur les données TechShop, ses clients et ses partenaires perdurent après ton départ. C'est contractuel.

---

## Signature

En signant cette charte, je confirme avoir pris connaissance de son contenu et m'engage à le respecter.

| Nom | Prénom | Poste | Date | Signature |
|---|---|---|---|---|
| | | | | |

*Retourner le document signé à la DRH (Nathalie Perrin) lors de la remise du matériel.*

---

*Document classifié : INTERNE*
*Prochaine révision : Juin 2027 ou suite à incident majeur*
