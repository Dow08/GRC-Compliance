import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ciso_assistant.settings')
django.setup()

from core.models import AppliedControl
from django.db.models import Count

# Remapping ISO 27001 Annex A -> NIST CSF
# Logique :
#   GV (Govern)   : Gouvernance, politiques, risques, conformite, chaine appro
#   ID (Identify)  : Inventaire actifs, gestion risques, vulnerabilites
#   PR (Protect)   : Controle acces, formation, chiffrement, maintenance, reseau
#   DE (Detect)    : Logs, surveillance, anomalies
#   RS (Respond)   : Incidents, communication de crise
#   RC (Recover)   : Backup, continuite, PRA

# Mapping par nom de controle (correspondance partielle sur mots-cles)
KEYWORD_CSF = [
    # GOVERN
    (['politique', 'policy', 'gouvern', 'conform', 'legal', 'reglementaire',
      'responsabilite', 'responsabilit', 'charte', 'audit interne',
      'revue direction', 'fournisseur', 'supplier', 'contrat', 'tiers',
      'propriete intellectuelle', 'droits', 'autorite', 'groupe interet',
      'perimetre', 'contexte', 'smsi', 'isms'], 'govern'),

    # IDENTIFY
    (['inventaire', 'inventory', 'actif', 'asset', 'classification',
      'risque', 'risk', 'vulnerabilit', 'menace', 'threat',
      'intelligence', 'pentest', 'audit plugin', 'wpscan',
      'analyse', 'evaluation', 'cartographie'], 'identify'),

    # PROTECT
    (['acces', 'access', 'authentification', 'authentication', 'mfa',
      'mot de passe', 'password', 'privilege', 'identit',
      'chiffrement', 'encrypt', 'crypto', 'tls', 'ssl',
      'vpn', 'wireguard', 'reseau', 'network', 'segmentation', 'vlan',
      'firewall', 'waf', 'cloudflare', 'filtrage',
      'formation', 'sensibilis', 'awareness', 'training',
      'offboarding', 'separation', 'maintenance', 'patch', 'mise a jour',
      'sauvegarde', 'backup', 'object lock', 'rbac', 'role',
      'physique', 'physical', 'bureau propre', 'clean desk',
      'pci', 'stripe', 'ovh', 'hebergement', 'datacenter',
      'migration', 'rgpd', 'dpa', 'transfert', 'dpo'], 'protect'),

    # DETECT
    (['supervision', 'monitoring', 'grafana', 'prometheus', 'log',
      'journalis', 'surveillance', 'edr', 'wazuh', 'detection',
      'alerte', 'alert', 'siem', 'anomalie', 'ids', 'ips'], 'detect'),

    # RESPOND
    (['incident', 'reponse', 'response', 'gestion crise', 'cnil',
      'notification', 'playbook', 'escalade', 'communication',
      'signalement', 'breach'], 'respond'),

    # RECOVER
    (['restauration', 'recover', 'pra', 'pca', 'continuite',
      'reprise', 'rto', 'rpo', 'redondance', 'resilience'], 'recover'),
]

def guess_csf(name, description=''):
    text = (name + ' ' + (description or '')).lower()
    scores = {csf: 0 for csf in ['govern', 'identify', 'protect', 'detect', 'respond', 'recover']}
    for keywords, csf in KEYWORD_CSF:
        for kw in keywords:
            if kw in text:
                scores[csf] += 1
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return 'govern'
    return best

print('=== Remapping NIST CSF des controles existants ===\n')

# Stats avant
before = dict(AppliedControl.objects.values('csf_function').annotate(n=Count('id')).values_list('csf_function', 'n'))
print('Distribution actuelle:')
for csf, n in sorted(before.items(), key=lambda x: -x[1]):
    print(f"  {csf or '(vide)'}: {n}")

print()

# Remapping
updated = 0
unchanged = 0
by_csf = {csf: 0 for csf in ['govern', 'identify', 'protect', 'detect', 'respond', 'recover']}

for ac in AppliedControl.objects.all():
    new_csf = guess_csf(ac.name, ac.description)
    if ac.csf_function != new_csf:
        ac.csf_function = new_csf
        ac.save(update_fields=['csf_function'])
        updated += 1
    else:
        unchanged += 1
    by_csf[new_csf] = by_csf.get(new_csf, 0) + 1

print(f'Controles remappes  : {updated}')
print(f'Controles inchanges : {unchanged}')

print('\nDistribution finale:')
total = sum(by_csf.values())
for csf in ['govern', 'identify', 'protect', 'detect', 'respond', 'recover']:
    n = by_csf.get(csf, 0)
    bar = '█' * int(n * 30 / max(total, 1))
    pct = n * 100 / max(total, 1)
    print(f"  {csf:<10} {bar:<30} {n:3d} ({pct:.0f}%)")

print('\n[OK] Remapping termine — Rafraichir le dashboard CISO Assistant')
