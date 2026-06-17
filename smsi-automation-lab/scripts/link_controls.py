import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ciso_assistant.settings')
django.setup()

from core.models import AppliedControl, RequirementAssessment, ComplianceAssessment

AUDIT_ID = 'bf24017b-d5bf-475b-b878-ed4eba7eb6b4'

# 1. Assigner csf_function a chaque controle applique
# Valeurs CISO Assistant : GV (Govern) / ID (Identify) / PR (Protect) / DE (Detect) / RS (Respond) / RC (Recover)

CSF_MAP = {
    'Cloudflare WAF - Protection applicative':            'PR',
    'TLS 1.3 - Chiffrement des communications':           'PR',
    'Sauvegardes AWS S3 eu-west-3':                       'RC',
    'VPN WireGuard - Acces administration securise':      'PR',
    'Supervision Grafana + Prometheus':                   'DE',
    'DPO designe - Sophie Blanc':                         'GV',
    'Inventaire des actifs informationnels':              'ID',
    'Analyse de risques EBIOS RM':                        'ID',
    'Hebergement OVH datacenter certifie ISO 27001':      'PR',
    'Stripe PCI-DSS SAQ A - Paiement securise':           'PR',
    'MFA Google Workspace - Deploiement tous comptes':    'PR',
    'Migration sauvegardes AWS eu-west-3 (RGPD)':         'PR',
    'Politique de securite de l information':             'GV',
    'Procedure offboarding securise':                     'PR',
    'Cloudflare WAF - Mode blocage OWASP':                'PR',
    'S3 Object Lock - Protection anti-ransomware':        'RC',
    'Audit plugins WordPress et politique patch':         'ID',
    'RBAC Odoo - Principe moindre privilege':             'PR',
    'EDR Wazuh - Detection menaces serveurs':             'DE',
    'Test restauration PRA - RTO/RPO mesures':            'RC',
    'Segmentation reseau - VLAN WiFi invite':             'PR',
    'Formation securite - 47 employes':                   'GV',
    'Pentest annuel WooCommerce':                         'ID',
    'Plan de reprise d activite (PRA/PCA)':               'RC',
    'Politique cryptographie':                            'PR',
    'HubSpot DPA - Conformite transfert hors UE':         'GV',
}

print('=== Etape 1 : Assignation CSF function ===')
updated_csf = 0
for name, csf in CSF_MAP.items():
    count = AppliedControl.objects.filter(name=name).update(csf_function=csf)
    if count:
        updated_csf += count
        print(f'  [{csf}] {name}')
    else:
        print(f'  [??] Non trouve: {name}')
print(f'Total CSF assignes: {updated_csf}')

# 2. Lier les controles appliques aux RequirementAssessments correspondants
# Mapping: ref_id du controle ISO -> nom du controle applique TechShop

CONTROL_LINKS = {
    # Govern
    'a.5.1':  ['Politique de securite de l information'],
    'a.5.2':  ['Politique de securite de l information'],
    'a.5.4':  ['Politique de securite de l information'],
    'a.5.9':  ['Inventaire des actifs informationnels'],
    'a.5.10': ['Inventaire des actifs informationnels'],
    'a.5.12': ['Inventaire des actifs informationnels'],
    'a.5.19': ['HubSpot DPA - Conformite transfert hors UE'],
    'a.5.31': ['DPO designe - Sophie Blanc'],
    'a.5.34': ['DPO designe - Sophie Blanc', 'Migration sauvegardes AWS eu-west-3 (RGPD)'],
    'a.6.3':  ['Formation securite - 47 employes'],
    'a.6.5':  ['Procedure offboarding securise'],

    # Identify
    'a.5.7':  ['Audit plugins WordPress et politique patch'],
    'a.5.8':  ['Analyse de risques EBIOS RM'],
    'a.8.8':  ['Audit plugins WordPress et politique patch', 'Pentest annuel WooCommerce'],

    # Protect
    'a.5.14': ['TLS 1.3 - Chiffrement des communications', 'VPN WireGuard - Acces administration securise'],
    'a.5.15': ['RBAC Odoo - Principe moindre privilege', 'MFA Google Workspace - Deploiement tous comptes'],
    'a.5.16': ['MFA Google Workspace - Deploiement tous comptes', 'Procedure offboarding securise'],
    'a.5.17': ['MFA Google Workspace - Deploiement tous comptes'],
    'a.5.18': ['RBAC Odoo - Principe moindre privilege', 'Procedure offboarding securise'],
    'a.5.23': ['Sauvegardes AWS S3 eu-west-3', 'Cloudflare WAF - Protection applicative'],
    'a.5.33': ['Sauvegardes AWS S3 eu-west-3', 'Migration sauvegardes AWS eu-west-3 (RGPD)'],
    'a.7.8':  ['Hebergement OVH datacenter certifie ISO 27001'],
    'a.7.11': ['Hebergement OVH datacenter certifie ISO 27001'],
    'a.8.2':  ['RBAC Odoo - Principe moindre privilege', 'VPN WireGuard - Acces administration securise'],
    'a.8.3':  ['RBAC Odoo - Principe moindre privilege'],
    'a.8.5':  ['MFA Google Workspace - Deploiement tous comptes'],
    'a.8.7':  ['EDR Wazuh - Detection menaces serveurs', 'Cloudflare WAF - Protection applicative'],
    'a.8.20': ['VPN WireGuard - Acces administration securise', 'Segmentation reseau - VLAN WiFi invite'],
    'a.8.22': ['Cloudflare WAF - Mode blocage OWASP', 'Segmentation reseau - VLAN WiFi invite'],
    'a.8.23': ['TLS 1.3 - Chiffrement des communications'],
    'a.8.24': ['TLS 1.3 - Chiffrement des communications', 'Politique cryptographie'],
    'a.8.28': ['Cloudflare WAF - Mode blocage OWASP'],

    # Detect
    'a.8.15': ['Supervision Grafana + Prometheus'],
    'a.8.16': ['Supervision Grafana + Prometheus', 'EDR Wazuh - Detection menaces serveurs'],

    # Recover
    'a.5.29': ['Plan de reprise d activite (PRA/PCA)', 'Test restauration PRA - RTO/RPO mesures'],
    'a.5.30': ['Plan de reprise d activite (PRA/PCA)'],
    'a.8.13': ['Sauvegardes AWS S3 eu-west-3', 'S3 Object Lock - Protection anti-ransomware'],
    'a.8.14': ['Plan de reprise d activite (PRA/PCA)', 'Hebergement OVH datacenter certifie ISO 27001'],

    # Respond
    'a.5.24': ['Supervision Grafana + Prometheus'],
    'a.5.26': ['EDR Wazuh - Detection menaces serveurs'],
}

print('\n=== Etape 2 : Liaison controles -> exigences ===')
try:
    audit = ComplianceAssessment.objects.get(id=AUDIT_ID)
except Exception as e:
    print(f'Audit non trouve: {e}')
    exit(1)

linked = 0
not_found_ra = 0
not_found_ac = 0

for ref_id, control_names in CONTROL_LINKS.items():
    # Trouver le RequirementAssessment
    ra_qs = RequirementAssessment.objects.filter(
        compliance_assessment=audit,
        requirement__ref_id__iexact=ref_id
    )
    if not ra_qs.exists():
        print(f'  [RA?] Non trouve: {ref_id}')
        not_found_ra += 1
        continue

    ra = ra_qs.first()

    for ctrl_name in control_names:
        ac_qs = AppliedControl.objects.filter(name=ctrl_name)
        if not ac_qs.exists():
            print(f'  [AC?] Non trouve: {ctrl_name}')
            not_found_ac += 1
            continue
        ac = ac_qs.first()
        ra.applied_controls.add(ac)
        linked += 1

print(f'\nLiaisons creees : {linked}')
print(f'RA non trouves  : {not_found_ra}')
print(f'AC non trouves  : {not_found_ac}')
print('\n[OK] Script termine - Rafraichir le dashboard CISO Assistant')
