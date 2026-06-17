import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ciso_assistant.settings')
django.setup()

from core.models import AppliedControl, RequirementAssessment, ComplianceAssessment
from django.utils import timezone

# Controles appliques TechShop SAS
# Status : active / in_progress / on_hold / deprecated
# Category : policy / process / technical_measure / physical_measure

CONTROLS = [
    # ---- ACTIFS (implementes) ----
    {
        'name': 'Cloudflare WAF - Protection applicative',
        'description': 'Pare-feu applicatif Cloudflare actif sur WooCommerce. Filtre OWASP Top 10, DDoS, bots malveillants.',
        'status': 'active',
        'category': 'technical_measure',
        'eta': None,
        'effort': 'S',
        'cost': 252,  # 21/mois x 12
    },
    {
        'name': 'TLS 1.3 - Chiffrement des communications',
        'description': 'TLS 1.3 active sur WooCommerce via Cloudflare. Certificats Let\'s Encrypt auto-renouvelés.',
        'status': 'active',
        'category': 'technical_measure',
        'eta': None,
        'effort': 'S',
        'cost': 0,
    },
    {
        'name': 'Sauvegardes AWS S3 eu-west-3',
        'description': 'Sauvegardes quotidiennes BDD WooCommerce + Odoo vers bucket S3 Paris. Retention 30 jours.',
        'status': 'active',
        'category': 'technical_measure',
        'eta': None,
        'effort': 'M',
        'cost': 120,
    },
    {
        'name': 'VPN WireGuard - Acces administration securise',
        'description': 'VPN WireGuard dedie acces SSH serveurs OVH. Seuls les admins avec cle peuvent se connecter.',
        'status': 'active',
        'category': 'technical_measure',
        'eta': None,
        'effort': 'M',
        'cost': 0,
    },
    {
        'name': 'Supervision Grafana + Prometheus',
        'description': 'Monitoring temps reel infrastructure OVH. Alertes disponibilite et performances.',
        'status': 'active',
        'category': 'technical_measure',
        'eta': None,
        'effort': 'M',
        'cost': 240,
    },
    {
        'name': 'DPO designe - Sophie Blanc',
        'description': 'Delegue a la Protection des Donnees designe volontairement. Registre des traitements en cours.',
        'status': 'active',
        'category': 'process',
        'eta': None,
        'effort': 'S',
        'cost': 0,
    },
    {
        'name': 'Inventaire des actifs informationnels',
        'description': '26 actifs inventories et classes selon 4 niveaux (Public/Interne/Confidentiel/Secret). Valide juin 2026.',
        'status': 'active',
        'category': 'policy',
        'eta': None,
        'effort': 'M',
        'cost': 0,
    },
    {
        'name': 'Analyse de risques EBIOS RM',
        'description': '15 risques analyses selon EBIOS RM simplifie. Cotation brute et residuelle. Valide CODIR juin 2026.',
        'status': 'active',
        'category': 'process',
        'eta': None,
        'effort': 'L',
        'cost': 0,
    },
    {
        'name': 'Hebergement OVH datacenter certifie ISO 27001',
        'description': 'Serveurs WooCommerce et Odoo heberges dans datacenters OVH certifies ISO 27001. Securite physique deleguee.',
        'status': 'active',
        'category': 'physical_measure',
        'eta': None,
        'effort': 'S',
        'cost': 3600,
    },
    {
        'name': 'Stripe PCI-DSS SAQ A - Paiement securise',
        'description': 'Traitement paiements CB deleguee a Stripe (certifie PCI-DSS). TechShop ne stocke aucun numero de carte.',
        'status': 'active',
        'category': 'process',
        'eta': None,
        'effort': 'S',
        'cost': 0,
    },
    # ---- EN COURS (in_progress) ----
    {
        'name': 'MFA Google Workspace - Deploiement tous comptes',
        'description': 'Activation MFA obligatoire sur les 47 comptes GW. Actuellement 1/47. Action M01 du PTR.',
        'status': 'in_progress',
        'category': 'technical_measure',
        'eta': '2026-07-31',
        'effort': 'S',
        'cost': 0,
    },
    {
        'name': 'Migration sauvegardes AWS eu-west-3 (RGPD)',
        'description': 'Suppression replication S3 vers us-east-1. Migration complete vers eu-west-3 Paris. Action M02.',
        'status': 'in_progress',
        'category': 'technical_measure',
        'eta': '2026-07-31',
        'effort': 'M',
        'cost': 600,
    },
    {
        'name': 'Politique de securite de l information',
        'description': 'Document en cours de finalisation. Engagement direction present. Signature DG prevue juillet 2026.',
        'status': 'in_progress',
        'category': 'policy',
        'eta': '2026-07-31',
        'effort': 'M',
        'cost': 0,
    },
    {
        'name': 'Procedure offboarding securise',
        'description': 'Checklist revocation acces J0 depart. 3 comptes orphelins a desactiver. Action M04.',
        'status': 'in_progress',
        'category': 'process',
        'eta': '2026-08-31',
        'effort': 'S',
        'cost': 0,
    },
    {
        'name': 'Cloudflare WAF - Mode blocage OWASP',
        'description': 'Passage mode Log vers mode Block pour regles OWASP Top 10 + regles WordPress. Action M05.',
        'status': 'in_progress',
        'category': 'technical_measure',
        'eta': '2026-08-31',
        'effort': 'S',
        'cost': 0,
    },
    {
        'name': 'S3 Object Lock - Protection anti-ransomware',
        'description': 'Activation Object Lock mode COMPLIANCE (retention 30j). Compte AWS secondaire dedie backup. Action M03.',
        'status': 'in_progress',
        'category': 'technical_measure',
        'eta': '2026-08-31',
        'effort': 'M',
        'cost': 0,
    },
    {
        'name': 'Audit plugins WordPress et politique patch',
        'description': 'Inventaire 47 plugins. Suppression plugins non maintenus. Politique: patch < 72h pour CVE critique. Action M10.',
        'status': 'in_progress',
        'category': 'process',
        'eta': '2026-08-31',
        'effort': 'M',
        'cost': 0,
    },
    {
        'name': 'RBAC Odoo - Principe moindre privilege',
        'description': 'Reconfiguration des roles Odoo. Separation acces RH / commandes / comptabilite. Suppression comptes generiques.',
        'status': 'in_progress',
        'category': 'technical_measure',
        'eta': '2026-09-30',
        'effort': 'M',
        'cost': 0,
    },
    # ---- PLANIFIES (on_hold = a faire) ----
    {
        'name': 'EDR Wazuh - Detection menaces serveurs',
        'description': 'Deploiement agent Wazuh sur serveurs OVH. Detection comportementale temps reel. Action M06.',
        'status': 'on_hold',
        'category': 'technical_measure',
        'eta': '2026-09-30',
        'effort': 'L',
        'cost': 240,
    },
    {
        'name': 'Test restauration PRA - RTO/RPO mesures',
        'description': 'Premier test restauration complete depuis S3. Mesure RTO reel. Objectif: RTO < 4h, RPO < 24h. Action M07.',
        'status': 'on_hold',
        'category': 'process',
        'eta': '2026-09-30',
        'effort': 'M',
        'cost': 5,
    },
    {
        'name': 'Segmentation reseau - VLAN WiFi invite',
        'description': 'Creation VLAN dedie WiFi invite isole du reseau interne. Materiel Ubiquiti deja en place. Action M09.',
        'status': 'on_hold',
        'category': 'technical_measure',
        'eta': '2026-09-30',
        'effort': 'S',
        'cost': 0,
    },
    {
        'name': 'Formation securite - 47 employes',
        'description': 'Formation anti-phishing + cyberhygiene. Simulation GoPhish. Cible: 100% formes, < 5% clic phishing. Action M08.',
        'status': 'on_hold',
        'category': 'process',
        'eta': '2026-10-31',
        'effort': 'L',
        'cost': 500,
    },
    {
        'name': 'Pentest annuel WooCommerce',
        'description': 'Test intrusion applicatif par prestataire externe certifie OSCP. Perimetre: auth, paiement, SQLi. Action M11.',
        'status': 'on_hold',
        'category': 'process',
        'eta': '2026-12-31',
        'effort': 'XL',
        'cost': 4000,
    },
    {
        'name': 'Plan de reprise d activite (PRA/PCA)',
        'description': 'Documentation PRA avec RTO=4h, RPO=24h. Procedures bascule WooCommerce + Odoo. Test annuel. Action M12.',
        'status': 'on_hold',
        'category': 'policy',
        'eta': '2026-12-31',
        'effort': 'L',
        'cost': 0,
    },
    {
        'name': 'Politique cryptographie',
        'description': 'Politique formelle: algorithmes autorises (AES-256, TLS 1.2+), gestion certificats, chiffrement BDD.',
        'status': 'on_hold',
        'category': 'policy',
        'eta': '2027-01-31',
        'effort': 'M',
        'cost': 0,
    },
    {
        'name': 'HubSpot DPA - Conformite transfert hors UE',
        'description': 'Passage HubSpot Starter pour obtenir DPA conforme RGPD ou migration vers Brevo (EU). NC-02.',
        'status': 'on_hold',
        'category': 'process',
        'eta': '2026-09-30',
        'effort': 'M',
        'cost': 600,
    },
]

from django.contrib.auth import get_user_model
User = get_user_model()

try:
    folder = None
    try:
        from core.models import Folder
        folder = Folder.objects.filter(content_type='DO').first()
        if not folder:
            folder = Folder.objects.first()
    except Exception:
        pass

    created = 0
    updated = 0
    for c in CONTROLS:
        eta = None
        if c['eta']:
            from datetime import date
            eta = date.fromisoformat(c['eta'])

        obj, was_created = AppliedControl.objects.update_or_create(
            name=c['name'],
            defaults={
                'description': c['description'],
                'status': c['status'],
                'category': c['category'],
                'eta': eta,
                'effort': c.get('effort', 'M'),
                'cost': c.get('cost', 0),
                **(({'folder': folder}) if folder else {}),
            }
        )
        if was_created:
            created += 1
        else:
            updated += 1

    print(f"[OK] Controles appliques : {created} crees, {updated} mis a jour")
    print(f"     Actifs   : {sum(1 for c in CONTROLS if c['status'] == 'active')}")
    print(f"     En cours : {sum(1 for c in CONTROLS if c['status'] == 'in_progress')}")
    print(f"     Planifies: {sum(1 for c in CONTROLS if c['status'] == 'on_hold')}")
    budget = sum(c.get('cost', 0) for c in CONTROLS)
    print(f"     Budget total : {budget} EUR")

except Exception as e:
    print(f"[ERREUR] {e}")
    import traceback
    traceback.print_exc()
