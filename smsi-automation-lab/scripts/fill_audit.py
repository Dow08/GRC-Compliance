import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ciso_assistant.settings')
django.setup()

from core.models import RequirementAssessment, ComplianceAssessment

AUDIT_ID = 'bf24017b-d5bf-475b-b878-ed4eba7eb6b4'
AUDIT_NAME = 'TechShop'  # Fallback si l UUID change apres recreation de la base

# Evaluations realistes TechShop SAS
# Completes : A.5.1 a A.5.13 + A.5.14 a A.8.34
# (status, result, extended_result, observation)
EVALS = {
    'a.5.1':  ('in_progress','partially_compliant','improvement_required','Le fond est la : analyse de risques realisee, engagement de la direction obtenu, perimetre defini. Ce qui manque c est la forme — le document n est pas encore signe et les employes ne savent pas qu il existe. Priorite : validation DG + diffusion avant fin juillet.'),
    'a.5.2':  ('in_progress','partially_compliant','improvement_required','Roles DSI/DPO/DG identifies. Fiches de poste securite non formalisees. Organigramme securite a documenter.'),
    'a.5.3':  ('in_progress','partially_compliant','improvement_required','Separation admin/utilisateur Odoo en cours. Google Workspace : compte admin unique. Action: comptes admin dedies separes des comptes nominatifs.'),
    'a.5.4':  ('in_progress','partially_compliant','improvement_required','Engagement direction present dans politique securite en cours. Pas encore signe formellement. Action: signature DG avant fin juillet 2026.'),
    'a.5.5':  ('to_do','non_compliant','minor_non_conformity','Aucun contact formel etabli avec CNIL/ANSSI/CERT-FR. Pas de procedure de liaison avec autorites. Action: documenter contacts reglementaires et procedure escalade.'),
    'a.5.6':  ('to_do','non_compliant','minor_non_conformity','Pas de participation a des groupes de securite sectoriels. Veille menaces informelle. Action: abonnement CERT-FR + adhesion club RSSI local.'),
    'a.5.7':  ('to_do','non_compliant','minor_non_conformity','Pas de threat intelligence formelle. Veille CVE manuelle sur WordPress. Action: abonnement flux NVD/CERT-FR automatise.'),
    'a.5.8':  ('to_do','non_compliant','minor_non_conformity','Securite non integree dans gestion de projet. Pas de security by design. Action: checklist securite pour tout nouveau projet IT.'),
    'a.5.9':  ('in_progress','compliant','conformity','Inventaire actifs complete : 26 actifs, 4 types, 4 niveaux classification. Document valide DSI juin 2026. Revue annuelle planifiee.'),
    'a.5.10': ('in_progress','partially_compliant','improvement_required','Charte informatique en cours de redaction. Regles usage acceptables non encore signees par employes. Action: finaliser et faire signer avant formation securite.'),
    'a.5.11': ('to_do','non_compliant','minor_non_conformity','Procedure offboarding non formalisee. Restitution actifs informelle. Action: checklist retour materiel + revocation acces J0 depart.'),
    'a.5.12': ('in_progress','compliant','conformity','Classification documentee : 4 niveaux (Public/Interne/Confidentiel/Secret). Appliquee sur 26 actifs. Grille dans inventaire-actifs.md.'),
    'a.5.13': ('to_do','non_compliant','minor_non_conformity','Classification documentee mais etiquetage physique des supports absent. Emails non etiquetes. Action: template etiquetage + politique diffusion.'),
    'a.5.14': ('in_progress','partially_compliant','improvement_required','Transferts via HTTPS/TLS actifs. AWS S3 chiffre. Pas de politique formelle de transfert securise. Emails non chiffres de bout en bout. Action: politique transfert securise + chiffrement emails sensibles.'),
    'a.5.15': ('in_progress','partially_compliant','improvement_required','Controle acces dans Odoo et Google Workspace mais non unifie. Pas de politique formelle. Revue acces non systematique.'),
    'a.5.16': ('in_progress','partially_compliant','improvement_required','Gestion identites dans Google Workspace et Odoo separement. Pas de IAM centralise. Comptes generiques encore presents.'),
    'a.5.17': ('to_do','non_compliant','minor_non_conformity','Politique mots de passe non formalisee. Pas de gestionnaire impose. Action: politique mots de passe + deployer gestionnaire type Bitwarden.'),
    'a.5.18': ('in_progress','partially_compliant','improvement_required','Droits acces par role dans Odoo. Pas de revue periodique formelle. Principe moindre privilege non systematique.'),
    'a.5.19': ('to_do','non_compliant','minor_non_conformity','Pas de politique securite fournisseurs. Stripe/Cloudflare/AWS utilises sans evaluation securite formelle.'),
    'a.5.20': ('to_do','non_compliant','minor_non_conformity','Contrats fournisseurs sans clauses securite explicites. Pas de SLA securite avec OVH/AWS. Action: clauses securite nouveaux contrats.'),
    'a.5.21': ('to_do','non_compliant','minor_non_conformity','Aucun processus gestion securite chaine approvisionnement TIC. Dependances WooCommerce/plugins non auditees.'),
    'a.5.22': ('to_do','non_compliant','minor_non_conformity','Pas de suivi formel services fournisseurs. OVH/AWS surveilles techniquement sans revue securite periodique documentee.'),
    'a.5.23': ('in_progress','partially_compliant','improvement_required','Cloudflare gere securite cloud. Pas de politique formelle securite services cloud. Responsabilites partagees AWS non documentees.'),
    'a.5.24': ('to_do','non_compliant','minor_non_conformity','Pas de procedure gestion incidents formalisee. Incidents traites au cas par cas. Pas de classification ni playbook IR.'),
    'a.5.25': ('to_do','non_compliant','minor_non_conformity','Pas d\'evaluation ni classification des incidents. Aucun historique incidents documente. Action: journal incidents + grille classification.'),
    'a.5.26': ('to_do','non_compliant','major_non_conformity','Non-conformite majeure. En cas de ransomware ce soir, personne chez TechShop ne sait quoi faire dans les premieres heures. Pas de contact OVH identifie, pas de procedure d isolation, pas de numero d astreinte. Les premieres 4 heures apres une attaque sont determinantes — chaque heure sans plan multiplie le cout de la remise en etat. A traiter avant tout audit externe.'),
    'a.5.27': ('to_do','non_compliant','minor_non_conformity','Incidents passes non documentes ni capitalises. Aucun retour experience formel. Action: post-mortem systematique apres incident.'),
    'a.5.28': ('to_do','non_compliant','minor_non_conformity','Pas de collecte preuves numeriques formalisee. En cas intrusion, incapacite constitution dossier legal.'),
    'a.5.29': ('in_progress','partially_compliant','improvement_required','PCA/PRA non documente. Sauvegardes AWS S3 en place. Tests restauration non effectues. RTO/RPO non definis.'),
    'a.5.30': ('to_do','non_compliant','minor_non_conformity','Aucune preparation continuite SI face aux menaces ICT. Scenarios de crise non testes. Action: exercice de crise annuel.'),
    'a.5.31': ('in_progress','partially_compliant','improvement_required','Conformite RGPD partiellement adressee via DPO Sophie Blanc. Veille reglementaire informelle. NIS2 en cours d\'evaluation.'),
    'a.5.32': ('in_progress','partially_compliant','improvement_required','Droits propriete intellectuelle respectes sur logiciels. Licences non toutes inventoriees. Plugins WooCommerce: verification en cours.'),
    'a.5.33': ('in_progress','partially_compliant','improvement_required','Sauvegardes AWS S3 en place. Pas de politique retention documentee par type de donnee. Durees non alignees RGPD.'),
    'a.5.34': ('in_progress','partially_compliant','improvement_required','DPO Sophie Blanc en place. Registre traitements partiel. Transferts AWS us-east-1 non conformes RGPD. Action: mise en conformite transferts hors UE.'),
    'a.5.35': ('to_do','non_compliant','minor_non_conformity','Audit interne SMSI non realise. Premier audit prevu 2026. Pas de programme audit formel.'),
    'a.5.36': ('to_do','non_compliant','minor_non_conformity','Conformite politiques non verifiee systematiquement. Pas de checklist conformite. Action: tableau de bord trimestriel.'),
    'a.5.37': ('to_do','non_compliant','minor_non_conformity','Procedures exploitation non documentees. Procedures backup/restore informelles. Action: documenter operations critiques SI.'),
    'a.6.1': ('in_progress','partially_compliant','improvement_required','Verification antecedents informelle. Clauses confidentialite dans contrats. Action: formaliser screening RH.'),
    'a.6.2': ('in_progress','partially_compliant','improvement_required','Clauses securite dans certains contrats. Pas de clause type systematique. Action: template contrat avec responsabilites securite.'),
    'a.6.3': ('to_do','non_compliant','minor_non_conformity','C est le point le plus fragile du SMSI. 47 personnes qui ouvrent des emails toute la journee, sans jamais avoir eu une seule heure de sensibilisation phishing. Le risque R10 est coté 8/16 exactement a cause de ca. Cybermalveillance.gouv.fr propose des modules gratuits — il n y a aucune raison valable de ne pas avoir commence.'),
    'a.6.4': ('to_do','non_compliant','minor_non_conformity','Pas de processus disciplinaire formel pour violations securite. Action: politique sanctions dans reglement interieur.'),
    'a.6.5': ('to_do','non_compliant','minor_non_conformity','Pas de procedure offboarding securite. Risque ex-employe acces actifs. Action: checklist depart revocation acces sous 24h.'),
    'a.6.6': ('to_do','non_compliant','minor_non_conformity','Pas d\'accord confidentialite specifique avec sous-traitants. Action: NDA systematique pour acces SI TechShop.'),
    'a.6.7': ('in_progress','partially_compliant','improvement_required','VPN WireGuard disponible. Politique teletravail informelle. Pas de regles formelles BYOD.'),
    'a.6.8': ('to_do','non_compliant','minor_non_conformity','Aucun canal signalement incidents securite connu des employes. Action: procedure signalement + sensibilisation.'),
    'a.7.1': ('in_progress','partially_compliant','improvement_required','Bureaux Toulouse avec acces badge. Entrepot Labege securise. Pas de politique perimetre securite documentee.'),
    'a.7.2': ('in_progress','partially_compliant','improvement_required','Acces physiques controles. Pas de registre entrees/sorties. Zones sensibles non clairement delimitees.'),
    'a.7.3': ('in_progress','partially_compliant','improvement_required','Bureaux securises. Pas de politique bureau propre formelle. Ecrans non systematiquement verrouilles apres inactivite.'),
    'a.7.4': ('to_do','non_compliant','minor_non_conformity','Aucune surveillance physique des locaux. Pas de cameras. Action: evaluer besoin surveillance selon risques physiques.'),
    'a.7.5': ('in_progress','partially_compliant','improvement_required','Serveurs OVH en datacenter securise. Locaux Toulouse: protection physique basique. Pas de salle serveur dediee.'),
    'a.7.6': ('in_progress','partially_compliant','improvement_required','Serveurs OVH proteges par datacenter OVH. Locaux Toulouse: protection incendie standard batiment.'),
    'a.7.7': ('to_do','non_compliant','minor_non_conformity','Politique bureau propre non formalisee. Documents sensibles laisses sur bureaux. Action: clean desk + verrouillage automatique postes.'),
    'a.7.8': ('in_progress','partially_compliant','improvement_required','Materiels installes en racks OVH. Pas de politique cablage documentee pour locaux Toulouse.'),
    'a.7.9': ('to_do','non_compliant','minor_non_conformity','Pas de politique securite actifs hors site. PC portables emportes sans regles chiffrement/verrouillage.'),
    'a.7.10': ('in_progress','partially_compliant','improvement_required','Supports stockes mais pas de procedure destruction securisee. Pas de dechiqueteur certifie pour supports sensibles.'),
    'a.7.11': ('in_progress','partially_compliant','improvement_required','Onduleurs OVH datacenter OK. Locaux Toulouse: pas alimentation secourue. Risque panne electrique postes travail.'),
    'a.7.12': ('in_progress','partially_compliant','improvement_required','Cablage reseau Toulouse non documente. OVH gere cablage datacenter. Pas de schema reseau local a jour.'),
    'a.7.13': ('in_progress','partially_compliant','improvement_required','Maintenance serveurs via OVH. Pas de politique maintenance postes utilisateurs. Pas de contrat maintenance formel parc complet.'),
    'a.7.14': ('to_do','non_compliant','minor_non_conformity','Pas de procedure mise au rebut securisee. Risque recuperation donnees anciens disques. Action: effacement certifie avant cession.'),
    'a.8.1': ('in_progress','partially_compliant','improvement_required','Postes utilisateurs sans politique formelle. Antivirus non uniformise. Action: politique endpoint + EDR centralise.'),
    'a.8.2': ('in_progress','partially_compliant','improvement_required','Droits admin limites sur certains postes. Pas de politique privilege minimum. Comptes admin locaux encore presents.'),
    'a.8.3': ('in_progress','partially_compliant','improvement_required','Acces information restreint dans Odoo par role. Pas de politique acces information globale.'),
    'a.8.4': ('in_progress','partially_compliant','improvement_required','Acces code source WooCommerce limite. Pas de politique formelle. Depot Git sans protection branches systematique.'),
    'a.8.5': ('in_progress','partially_compliant','improvement_required','Situation paradoxale : le DG a le MFA, les 46 autres non. Dont deux comptes admin avec acces total au SI. C est probablement la correction la plus rapide et la plus impactante de tout le plan — moins de 2 heures de travail pour diviser le risque R03 par quatre. Pas d excuse pour ne pas l avoir fait.'),
    'a.8.6': ('in_progress','partially_compliant','improvement_required','Grafana/Prometheus pour supervision. Pas de gestion capacite formelle. Risque saturation stockage AWS S3.'),
    'a.8.7': ('in_progress','partially_compliant','improvement_required','Cloudflare WAF protege contre malwares. Pas antivirus centralise postes. Pas scan malware emails.'),
    'a.8.8': ('in_progress','partially_compliant','improvement_required','MAJ WooCommerce non systematiques. Patches OVH manuels. Pas de processus patch management formel. Risque CVE.'),
    'a.8.9': ('to_do','non_compliant','minor_non_conformity','Aucune gestion configuration formelle. Configs serveurs non documentees. Pas de baseline securite. Action: documenter configs reference.'),
    'a.8.10': ('to_do','non_compliant','minor_non_conformity','Pas de politique suppression donnees. Donnees clients conservees indefiniment. Action: politique retention + suppression automatisee.'),
    'a.8.11': ('to_do','non_compliant','minor_non_conformity','Pas de masquage donnees en env test. Donnees clients potentiellement en dev. Risque RGPD. Action: anonymisation donnees test.'),
    'a.8.12': ('to_do','non_compliant','minor_non_conformity','Aucun DLP en place. Extraction donnees clients non detectee. Action: evaluer solution DLP ou regles Google Workspace.'),
    'a.8.13': ('in_progress','partially_compliant','improvement_required','Sauvegardes AWS S3 en place. Frequence et retention non documentees. Tests restauration non effectues. RTO/RPO non definis.'),
    'a.8.14': ('in_progress','partially_compliant','improvement_required','Redondance OVH partielle. Cloudflare disponibilite CDN. Pas plan redondance complet. SPOF identifies sur ERP Odoo.'),
    'a.8.15': ('to_do','non_compliant','minor_non_conformity','Logs Grafana/Prometheus disponibles non centralises. Pas de SIEM. Retention logs non definie. Action: centralisation + retention 12 mois.'),
    'a.8.16': ('to_do','non_compliant','minor_non_conformity','Grafana surveille infra mais pas surveillance activite reseau dediee. Pas IDS/IPS. Action: activer surveillance anomalies Cloudflare.'),
    'a.8.17': ('to_do','non_compliant','minor_non_conformity','Horloges serveurs sync NTP OVH. Pas de politique synchronisation temps formelle ni verification reguliere.'),
    'a.8.18': ('in_progress','partially_compliant','improvement_required','Outils admin SSH/OVH limites. Acces admin non logues systematiquement. Pas de politique formelle outils admin.'),
    'a.8.19': ('in_progress','partially_compliant','improvement_required','Logiciels installes sans validation formelle. Plugins WooCommerce sans audit securite. Action: whitelist logiciels approuves.'),
    'a.8.20': ('in_progress','partially_compliant','improvement_required','Cloudflare WAF + filtrage. Reseau interne non segmente. Pas firewall applicatif interne. Action: segmentation + regles firewall.'),
    'a.8.21': ('in_progress','partially_compliant','improvement_required','Services web HTTPS. Ports inutiles non systematiquement fermes. Pas audit services reseau regulier.'),
    'a.8.22': ('to_do','non_compliant','minor_non_conformity','Pas de segmentation reseau. Serveurs web et ERP meme segment. Risque lateral movement. Action: VLAN separation prod/admin.'),
    'a.8.23': ('in_progress','partially_compliant','improvement_required','Cloudflare filtre web. Pas de filtrage web interne postes. Action: filtrage DNS type Cloudflare Gateway.'),
    'a.8.24': ('in_progress','partially_compliant','improvement_required','HTTPS/TLS actif tous services web. Chiffrement AWS S3. Politique chiffrement non documentee. Certificats via Cloudflare.'),
    'a.8.25': ('to_do','non_compliant','minor_non_conformity','Pas de cycle dev securise formel. Evolutions WooCommerce sans revue securite code. Action: checklist SDLC + revue code.'),
    'a.8.26': ('to_do','non_compliant','minor_non_conformity','Exigences securite applicative non documentees. WooCommerce/Odoo configures sans baseline securite formelle.'),
    'a.8.27': ('to_do','non_compliant','minor_non_conformity','Architecture securite non documentee. Pas de principes securite architecture definis. Action: documenter architecture securite reference.'),
    'a.8.28': ('to_do','non_compliant','minor_non_conformity','Dev securise non formalise. Risque injection SQL WooCommerce identifie (R006). Action: formation OWASP Top 10 + tests securite.'),
    'a.8.29': ('to_do','non_compliant','minor_non_conformity','Pas de tests securite avant mise en production. Pas de pentest. Action: test OWASP ZAP avant chaque release majeure.'),
    'a.8.30': ('to_do','non_compliant','minor_non_conformity','Dev externalise non encadre securite. Pas clauses securite prestataires. Action: exigences securite dans cahiers des charges.'),
    'a.8.31': ('in_progress','partially_compliant','improvement_required','Env dev/prod separes partiellement. Pas de politique separation formelle. Donnees production potentiellement en dev.'),
    'a.8.32': ('to_do','non_compliant','minor_non_conformity','Pas de gestion changements formelle. Changements prod sans procedure validation. Action: process change management.'),
    'a.8.33': ('to_do','non_compliant','minor_non_conformity','Infos tests non protegees. Donnees clients potentiellement en test. Risque RGPD. Action: anonymisation donnees test.'),
    'a.8.34': ('to_do','non_compliant','minor_non_conformity','Aucun pentest realise. Pas audit securite externe. Action: pentest annuel WooCommerce + infra OVH. Budget a prevoir.'),
}

try:
    audit = ComplianceAssessment.objects.get(id=AUDIT_ID)
except ComplianceAssessment.DoesNotExist:
    audit = ComplianceAssessment.objects.filter(name__icontains=AUDIT_NAME).first()
    if not audit:
        raise Exception(f"Audit introuvable par ID {AUDIT_ID} ni par nom '{AUDIT_NAME}'")
    print(f'Audit trouve par nom: {audit.name} ({audit.id})')

ras = RequirementAssessment.objects.filter(compliance_assessment=audit)
print(f'Total: {ras.count()}')

updated = 0
not_found = 0
for ra in ras:
    req = ra.requirement
    if not req or not req.ref_id:
        continue
    key = req.ref_id.lower().strip()
    if key in EVALS:
        status, result, extended, obs = EVALS[key]
        ra.status = status
        ra.result = result
        ra.extended_result = extended
        ra.observation = obs
        ra.save()
        updated += 1
    else:
        not_found += 1

print(f'Updated: {updated}')
print(f'Not matched: {not_found}')
