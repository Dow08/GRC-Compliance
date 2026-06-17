#!/usr/bin/env python3
"""
cyber_compliance_agent.py

A Parser-to-Reasoner automated compliance auditor (Enterprise DevSecOps Edition).
Ingests technical configurations, maps them to GRC security standards
(ISO 27001, NIS2), reasons compliance via an LLM, and exports rich dashboards.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple, List, Optional

# =====================================================================
# B. The Mapping Matrix (GRC Security Standards mapping)
# =====================================================================
MAPPING_MATRIX: Dict[str, Dict[str, Any]] = {
    "SSH_HARDENING": {
        "asset_name": "SSH Server Hardening",
        "iso_controls": [
            "ISO 27001:2022 A.5.15 (Access Control)",
            "ISO 27001:2022 A.8.20 (Network Security)"
        ],
        "nis2_controls": [
            "NIS2 Article 21 (Cryptography & Access Policies)"
        ],
        "description": "Verification of SSH secure configurations: key authentication, cipher suites, password rules, and root login blocks."
    },
    "DB_HARDENING": {
        "asset_name": "Database Security Hardening",
        "iso_controls": [
            "ISO 27001:2022 A.8.24 (Use of Cryptography)",
            "ISO 27001:2022 A.8.15 (Logging)",
            "ISO 27001:2022 A.8.2 (User Access Rights)"
        ],
        "nis2_controls": [
            "NIS2 Article 21 (Data Security & Cryptography / Access Controls)"
        ],
        "description": "Verification of Database (PostgreSQL/MySQL) configurations: TLS/SSL encryption, listener bindings, root privilege limits, and credential protection."
    },
    "K8S_HARDENING": {
        "asset_name": "Kubernetes Cluster Hardening",
        "iso_controls": [
            "ISO 27001:2022 A.8.20 (Network Security)",
            "ISO 27001:2022 A.8.22 (Web Filtering)",
            "ISO 27001:2022 A.8.12 (Data Leakage Prevention)"
        ],
        "nis2_controls": [
            "NIS2 Article 21 (Network Isolation & Access Policies)"
        ],
        "description": "Verification of Kubernetes manifest configurations: RBAC policies, NetworkPolicies, non-root user execution, and container resource limits."
    }
}

# =====================================================================
# C. System Audit Prompt
# =====================================================================
SYSTEM_PROMPT = """You are an expert ISO 27001 / NIS2 Lead Auditor.
Analyze the provided Infrastructure-as-Code snippet against the target control.
CRITICAL SECURITY RULES:
1. Zero-Trust evaluation: If the proof is ambiguous or missing values, flag as NON_COMPLIANT.
2. Anti-Hallucination Guard: Do not invent configurations. Base your judgment ONLY on visible text.
3. CVE/CWE Mapping: You MUST attempt to map the identified security gaps to associated CVE classes (e.g. historical CVEs for similar issues) and specific CWE IDs (Common Weakness Enumeration, e.g., CWE-256 for plaintext passwords, CWE-319 for cleartext transmission, CWE-284 for open listener addresses, CWE-521 for weak passwords, etc.).
4. Output format: You must return a RAW JSON string. No text before, no text after.
Expected JSON Schema:
{
  "control_id": "string",
  "status": "COMPLIANT|PARTIALLY_COMPLIANT|NON_COMPLIANT",
  "risk_score_assigned": "LOW|MEDIUM|HIGH",
  "technical_gap": "string or null",
  "associated_cves_or_cwes": "string or null (comma-separated list of CWEs and/or representative historical CVEs, ex: CWE-256, CWE-284)",
  "remediation_command": "string (concrete bash/ansible command to fix it)"
}"""

# =====================================================================
# A. Defensive Environment Ingestion
# =====================================================================
def detect_provider() -> Tuple[str, str, str]:
    """
    Autodetects the active AI provider based on environment variables.
    Returns: (provider_name, config_value, default_model)
    """
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic", os.environ["ANTHROPIC_API_KEY"], "claude-3-5-sonnet-20241022"
    elif os.environ.get("OPENAI_API_KEY"):
        return "openai", os.environ["OPENAI_API_KEY"], "gpt-4o-mini"
    elif os.environ.get("GEMINI_API_KEY"):
        return "gemini", os.environ["GEMINI_API_KEY"], "gemini-1.5-flash"
    elif os.environ.get("OLLAMA_HOST"):
        return "ollama", os.environ["OLLAMA_HOST"], "gemma2:2b"
    
    # Fallback default if nothing is configured
    return "ollama", "http://localhost:11434", "gemma2:2b"

def read_iac_file(filepath: str) -> str:
    """
    Safely reads the target file, raising specific defensive exceptions on errors.
    """
    if not filepath:
        raise ValueError("File path cannot be empty.")
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Configuration file error: The target file was not found at '{filepath}'."
        ) from e
    except PermissionError as e:
        raise PermissionError(
            f"Access denied: Insufficient permissions to read the file at '{filepath}'."
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Unexpected error reading configuration file '{filepath}': {e}"
        ) from e

# =====================================================================
# C. Multi-Provider Native HTTP Client
# =====================================================================
def evaluate_compliance(
    config_snippet: str, 
    asset_key: str, 
    provider: str, 
    auth_val: str, 
    model: str, 
    timeout: int = 180
) -> str:
    """
    Performs standard HTTP POST requests natively without external SDK packages.
    """
    if asset_key not in MAPPING_MATRIX:
        raise KeyError(f"Asset key '{asset_key}' is not registered in the mapping matrix.")

    mapping_info = MAPPING_MATRIX[asset_key]
    iso_standards = ", ".join(mapping_info["iso_controls"])
    nis2_standards = ", ".join(mapping_info["nis2_controls"])

    # Build the rich user prompt containing GRC context
    user_prompt = (
        f"Target Control Asset: {asset_key} ({mapping_info['asset_name']})\n"
        f"ISO 27001 Mapping: {iso_standards}\n"
        f"NIS2 Mapping: {nis2_standards}\n\n"
        f"Infrastructure-as-Code Configuration Content:\n"
        f"```yaml\n"
        f"{config_snippet}\n"
        f"```\n\n"
        f"Perform strict audit verification. Return only the requested JSON."
    )

    headers = {"content-type": "application/json"}
    data = {}
    url = ""

    if provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers["x-api-key"] = auth_val
        headers["anthropic-version"] = "2023-06-01"
        data = {
            "model": model,
            "max_tokens": 1024,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_prompt}],
            "temperature": 0.0
        }
    elif provider == "openai":
        url = "https://api.openai.com/v1/chat/completions"
        headers["Authorization"] = f"Bearer {auth_val}"
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0
        }
    elif provider == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={auth_val}"
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": f"SYSTEM INSTRUCTION:\n{SYSTEM_PROMPT}\n\nUSER INSTRUCTION:\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.0,
                "responseMimeType": "application/json"
            }
        }
    else:  # ollama
        host = auth_val.rstrip("/")
        url = f"{host}/api/chat"
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "options": {"temperature": 0.0},
            "stream": False
        }

    req_body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=req_body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            
            if provider == "anthropic":
                return res_json["content"][0]["text"]
            elif provider == "openai":
                return res_json["choices"][0]["message"]["content"]
            elif provider == "gemini":
                return res_json["candidates"][0]["content"]["parts"][0]["text"]
            else:  # ollama
                return res_json["message"]["content"]
                
    except urllib.error.HTTPError as e:
        error_info = e.read().decode("utf-8") if e.fp else ""
        raise RuntimeError(f"LLM API returned HTTP {e.code}: {e.reason}. Details: {error_info}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to reach compliance reasoning model service: {e.reason}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected communication error with reasoning service: {e}") from e

# =====================================================================
# D. JSON Extraction & Cleaning Robustness
# =====================================================================
def extract_and_clean_json(raw_response: str) -> Dict[str, Any]:
    """
    Cleans Markdown fences and extracts the JSON block cleanly.
    """
    cleaned = raw_response.strip()
    
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        content_lines = [line for line in lines if not line.strip().startswith("```")]
        cleaned = "\n".join(content_lines).strip()
    
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    start_brace = cleaned.find("{")
    end_brace = cleaned.rfind("}")
    
    if start_brace != -1 and end_brace != -1:
        cleaned = cleaned[start_brace:end_brace + 1]

    try:
        parsed_data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"JSON Parse Error: The evaluation response could not be parsed as valid JSON.\n"
            f"Raw Response: {raw_response}\n"
            f"Extraction Error: {e}"
        ) from e

    required_keys = ["control_id", "status", "risk_score_assigned", "technical_gap", "associated_cves_or_cwes", "remediation_command"]
    for key in required_keys:
        if key not in parsed_data:
            raise KeyError(f"Compliance validation failed: Response missing expected key '{key}'.")

    return parsed_data

# =====================================================================
# E. Automatic Control Matching for Folders
# =====================================================================
def auto_detect_control(filename: str, content: str) -> Optional[str]:
    """
    Analyzes filename and content keywords to automatically match the best GRC control.
    """
    name_lower = filename.lower()
    content_lower = content.lower()
    
    # 1. Kubernetes detection
    if "kubernetes" in name_lower or "k8s" in name_lower or "apiversion:" in content_lower or "kind:" in content_lower:
        return "K8S_HARDENING"
        
    # 2. Database detection
    if any(keyword in name_lower for keyword in ["postgres", "mysql", "db_", "database", "sql"]):
        return "DB_HARDENING"
    if any(keyword in content_lower for keyword in ["postgresql", "mysql_user", "ssl =", "pg_hba"]):
        return "DB_HARDENING"
        
    # 3. SSH detection
    if "ssh" in name_lower or "sshd" in name_lower or "sshd_config" in content_lower or "passwordauthentication" in content_lower:
        return "SSH_HARDENING"
        
    return None

# =====================================================================
# F. Rich Report Generators (Single-File & Multi-File Dashboard)
# =====================================================================
def generate_markdown_report(report_data: Dict[str, Any], filepath: str, config_content: str, control_key: str):
    """
    Generates a clean Markdown (.md) compliance report.
    """
    mapping = MAPPING_MATRIX[control_key]
    iso_str = ", ".join(mapping["iso_controls"])
    nis2_str = ", ".join(mapping["nis2_controls"])
    
    status_emoji = "✅" if report_data["status"] == "COMPLIANT" else "⚠️" if report_data["status"] == "PARTIALLY_COMPLIANT" else "❌"
    
    content = f"""# Rapport d'Audit de Conformité GRC - {mapping['asset_name']}

## Fiche d'Identité de l'Évaluation
* **Statut de Conformité** : {status_emoji} **{report_data['status']}**
* **Niveau de Risque Assigné** : ` {report_data['risk_score_assigned']} `
* **Référentiel ISO 27001** : {iso_str}
* **Référentiel NIS2** : {nis2_str}
* **CVEs / CWEs Associés** : `{report_data.get('associated_cves_or_cwes', 'Aucun')}`

---

## 1. Description du Fichier Évalué
* **Type de Configuration** : `{control_key}`
* **Description du Contrôle** : {mapping['description']}

---

## 2. Écarts Techniques Identifiés (Gaps)
> {report_data['technical_gap'] if report_data['technical_gap'] else "Aucun écart technique identifié. Le fichier est pleinement conforme."}

---

## 3. Plan de Remédiation Préconisé
Exécutez ou appliquez les instructions suivantes pour mettre la configuration en conformité :

```yaml
{report_data['remediation_command']}
```

---
*Généré automatiquement par l'analyseur autonome GRC Cybersecurity Compliance Auditor.*
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def generate_html_report(report_data: Dict[str, Any], filepath: str, config_content: str, control_key: str):
    """
    Generates a single-file premium HTML report.
    """
    mapping = MAPPING_MATRIX[control_key]
    iso_str = ", ".join(mapping["iso_controls"])
    nis2_str = ", ".join(mapping["nis2_controls"])
    
    status_class = "compliant" if report_data["status"] == "COMPLIANT" else "partial" if report_data["status"] == "PARTIALLY_COMPLIANT" else "non-compliant"
    status_text = "CONFORME" if report_data["status"] == "COMPLIANT" else "PARTIELLEMENT CONFORME" if report_data["status"] == "PARTIALLY_COMPLIANT" else "NON CONFORME"
    
    risk_class = "risk-low" if report_data["risk_score_assigned"] == "LOW" else "risk-medium" if report_data["risk_score_assigned"] == "MEDIUM" else "risk-high"
    risk_text = "RISQUE FAIBLE" if report_data["risk_score_assigned"] == "LOW" else "RISQUE MODÉRÉ" if report_data["risk_score_assigned"] == "MEDIUM" else "RISQUE ÉLEVÉ"

    escaped_config = config_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    remed_cmd = report_data.get("remediation_command") or ""
    escaped_remediation = remed_cmd.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport d'Audit GRC : {mapping['asset_name']}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: #151c2c;
            --border-color: #232d42;
            --text-color: #f3f4f6;
            --text-muted: #9ca3af;
            --success-color: #10b981;
            --success-glow: rgba(16, 185, 129, 0.15);
            --warning-color: #f59e0b;
            --warning-glow: rgba(245, 158, 11, 0.15);
            --error-color: #ef4444;
            --error-glow: rgba(239, 68, 68, 0.15);
            --code-bg: #070a13;
        }}
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 40px 20px;
            line-height: 1.6;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        header {{
            margin-bottom: 40px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        h1 {{ font-size: 28px; font-weight: 700; margin: 0 0 10px 0; letter-spacing: -0.5px; }}
        .subtitle {{ color: var(--text-muted); margin: 0; font-size: 16px; }}
        .badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 14px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        .compliant {{ background-color: var(--success-glow); color: var(--success-color); border: 1px solid var(--success-color); }}
        .partial {{ background-color: var(--warning-glow); color: var(--warning-color); border: 1px solid var(--warning-color); }}
        .non-compliant {{ background-color: var(--error-glow); color: var(--error-color); border: 1px solid var(--error-color); }}
        .grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 30px; margin-bottom: 30px; }}
        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }}
        .card h2 {{
            font-size: 18px; margin-top: 0; margin-bottom: 20px;
            border-bottom: 1px solid var(--border-color); padding-bottom: 10px;
        }}
        .meta-item {{ margin-bottom: 15px; }}
        .meta-label {{ font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; display: block; margin-bottom: 4px; }}
        .meta-value {{ font-size: 14px; font-weight: 500; }}
        .risk-badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 700; }}
        .risk-low {{ background-color: rgba(16, 185, 129, 0.2); color: var(--success-color); }}
        .risk-medium {{ background-color: rgba(245, 158, 11, 0.2); color: var(--warning-color); }}
        .risk-high {{ background-color: rgba(239, 68, 68, 0.2); color: var(--error-color); }}
        .gap-box {{
            background-color: rgba(239, 68, 68, 0.05); border-left: 4px solid var(--error-color);
            padding: 15px 20px; border-radius: 0 8px 8px 0; margin-bottom: 30px; font-size: 15px;
        }}
        .gap-box.compliant-box {{ border-left: 4px solid var(--success-color); background-color: rgba(16, 185, 129, 0.05); }}
        pre {{ background-color: var(--code-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 20px; overflow-x: auto; margin: 0; }}
        code {{ font-family: 'Courier New', Courier, monospace; font-size: 13.5px; color: #e5e7eb; }}
        .code-container {{ position: relative; }}
        .copy-btn {{
            position: absolute; top: 10px; right: 10px; background-color: var(--card-bg);
            border: 1px solid var(--border-color); color: var(--text-color); padding: 4px 8px;
            font-size: 11px; border-radius: 4px; cursor: pointer;
        }}
        footer {{ text-align: center; margin-top: 50px; color: var(--text-muted); font-size: 12px; border-top: 1px solid var(--border-color); padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Rapport d'Audit de Conformité GRC</h1>
                <p class="subtitle">Analyse automatisée de configuration de sécurité</p>
            </div>
            <div>
                <span class="badge {status_class}">{status_text}</span>
            </div>
        </header>
        <div class="grid">
            <div class="card">
                <h2>Rapport d'Audit Technique</h2>
                <div class="meta-label">Écarts techniques identifiés (Gaps)</div>
                <div class="gap-box {'compliant-box' if report_data['status'] == 'COMPLIANT' else ''}">
                    {report_data['technical_gap'] if report_data['technical_gap'] else "Aucun écart technique identifié. La configuration respecte les critères de sécurité."}
                </div>
                <div class="meta-label" style="margin-bottom: 8px;">Plan de Remédiation Technique Préconisé</div>
                <div class="code-container">
                    <button class="copy-btn" onclick="navigator.clipboard.writeText(document.getElementById('remediation-code').innerText)">Copier</button>
                    <pre><code id="remediation-code">{escaped_remediation}</code></pre>
                </div>
            </div>
            <div class="card">
                <h2>Métadonnées GRC</h2>
                <div class="meta-item">
                    <span class="meta-label">Actif Technologique</span>
                    <span class="meta-value">{mapping['asset_name']}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Niveau de Risque</span>
                    <span class="meta-value"><span class="risk-badge {risk_class}">{risk_text}</span></span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Règles ISO 27001</span>
                    <span class="meta-value">{iso_str}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Exigences NIS2</span>
                    <span class="meta-value">{nis2_str}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">CVEs / CWEs Associés</span>
                    <span class="meta-value" style="color: var(--warning-color); font-weight: bold;">{report_data.get('associated_cves_or_cwes', 'Non applicable / Aucun')}</span>
                </div>
            </div>
        </div>
        <div class="card" style="margin-top: 30px;">
            <h2>Configuration Source Évaluée</h2>
            <pre><code>{escaped_config}</code></pre>
        </div>
        <footer>
            <p>Généré automatiquement par l'analyseur autonome GRC Cybersecurity Compliance Auditor.</p>
        </footer>
    </div>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

def generate_consolidated_dashboard(reports: List[Dict[str, Any]], filepath: str, folder_path: str):
    """
    Generates a single premium HTML compliance dashboard consolidating results from multiple audited files.
    """
    total_files = len(reports)
    compliant_files = sum(1 for r in reports if r["report"]["status"] == "COMPLIANT")
    partial_files = sum(1 for r in reports if r["report"]["status"] == "PARTIALLY_COMPLIANT")
    non_compliant_files = sum(1 for r in reports if r["report"]["status"] == "NON_COMPLIANT")
    
    compliance_score = int((compliant_files / total_files) * 100) if total_files > 0 else 0
    score_color = "#10b981" if compliance_score >= 80 else "#f59e0b" if compliance_score >= 50 else "#ef4444"

    # Compile the table rows and interactive accordions
    rows_html = ""
    
    for idx, item in enumerate(reports):
        file_name = item["filename"]
        control_key = item["control_id"]
        rep = item["report"]
        config_content = item["content"]
        mapping = MAPPING_MATRIX[control_key]
        
        status_badge_class = "compliant" if rep["status"] == "COMPLIANT" else "partial" if rep["status"] == "PARTIALLY_COMPLIANT" else "non-compliant"
        status_text = "CONFORME" if rep["status"] == "COMPLIANT" else "PARTIEL" if rep["status"] == "PARTIALLY_COMPLIANT" else "NON CONFORME"
        
        risk_class = "risk-low" if rep["risk_score_assigned"] == "LOW" else "risk-medium" if rep["risk_score_assigned"] == "MEDIUM" else "risk-high"
        
        escaped_config = config_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        remed_cmd = rep.get("remediation_command") or ""
        escaped_remediation = remed_cmd.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # 1. Main table row and sub-row accordion
        border_color = "var(--success-color)" if rep["status"] == "COMPLIANT" else "var(--warning-color)" if rep["status"] == "PARTIALLY_COMPLIANT" else "var(--error-color)"
        rows_html += f"""
        <tr onclick="toggleAccordion({idx})" style="cursor: pointer; transition: background-color 0.2s;">
            <td style="font-weight: 600;">{file_name}</td>
            <td><span class="tech-badge">{mapping['asset_name']}</span></td>
            <td><span class="badge {status_badge_class}">{status_text}</span></td>
            <td><span class="risk-badge {risk_class}">{rep['risk_score_assigned']}</span></td>
            <td style="color: var(--text-muted); font-size: 13px; text-align: right; font-weight: 600;">
                <span class="open-label-{idx}" style="color: var(--success-color);">Cliquer pour ouvrir</span>
            </td>
        </tr>
        <tr id="accordion-{idx}" style="display: none;">
            <td colspan="5" style="padding: 0; border-bottom: 1px solid var(--border-color); background-color: rgba(7, 10, 19, 0.4);">
                <div style="padding: 25px 20px; border-left: 4px solid {border_color};">
                    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 25px;">
                        <div>
                            <h3 style="margin-top: 0; font-size: 14px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px;">Constats techniques de l'auditeur</h3>
                            <div class="gap-box {'compliant-box' if rep['status'] == 'COMPLIANT' else ''}" style="margin-bottom: 20px;">
                                {rep['technical_gap'] if rep['technical_gap'] else "La configuration respecte parfaitement les exigences de sécurité du référentiel GRC."}
                            </div>
                            
                            <h3 style="font-size: 14px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px; letter-spacing: 0.5px;">Action de Remédiation Recommandée</h3>
                            <div class="code-container">
                                <button class="copy-btn" onclick="navigator.clipboard.writeText(document.getElementById('remediation-{idx}').innerText); event.stopPropagation();">Copier</button>
                                <pre><code id="remediation-{idx}">{escaped_remediation}</code></pre>
                            </div>
                        </div>
                        <div>
                            <p style="margin: 0 0 12px 0; font-size: 13px;"><strong style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">Normes ISO 27001</strong><br>{", ".join(mapping["iso_controls"])}</p>
                            <p style="margin: 0 0 12px 0; font-size: 13px;"><strong style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">Directive NIS2</strong><br>{", ".join(mapping["nis2_controls"])}</p>
                            <p style="margin: 0; font-size: 13px;"><strong style="color: var(--text-muted); font-size: 11px; text-transform: uppercase;">CVEs / CWEs</strong><br><span style="color: var(--warning-color); font-weight: bold;">{rep.get('associated_cves_or_cwes', 'Aucun')}</span></p>
                        </div>
                    </div>
                    <div style="margin-top: 25px;">
                        <h3 style="font-size: 14px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px; letter-spacing: 0.5px;">Fichier source audité</h3>
                        <pre><code>{escaped_config}</code></pre>
                    </div>
                </div>
            </td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IAC-G.R.C-Auditor_ AGENT : Tableau de Bord</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: #151c2c;
            --border-color: #232d42;
            --text-color: #f3f4f6;
            --text-muted: #9ca3af;
            --success-color: #10b981;
            --success-glow: rgba(16, 185, 129, 0.15);
            --warning-color: #f59e0b;
            --warning-glow: rgba(245, 158, 11, 0.15);
            --error-color: #ef4444;
            --error-glow: rgba(239, 68, 68, 0.15);
            --code-bg: #070a13;
        }}
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 40px 20px;
            line-height: 1.6;
        }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        header {{
            margin-bottom: 40px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        h1 {{ font-size: 28px; font-weight: 700; margin: 0 0 10px 0; letter-spacing: -0.5px; }}
        .subtitle {{ color: var(--text-muted); margin: 0; font-size: 16px; }}
        
        .kpi-container {{
            display: grid;
            grid-template-columns: repeat(4, 1fr) 2fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .kpi-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .kpi-title {{
            font-size: 11px;
            text-transform: uppercase;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 5px;
        }}
        .kpi-value {{
            font-size: 32px;
            font-weight: 700;
        }}
        
        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }}
        .card h2 {{
            font-size: 18px; margin-top: 0; margin-bottom: 20px;
            border-bottom: 1px solid var(--border-color); padding-bottom: 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            text-align: left;
            padding: 12px;
            font-size: 12px;
            text-transform: uppercase;
            color: var(--text-muted);
            border-bottom: 2px solid var(--border-color);
        }}
        td {{
            padding: 16px 12px;
            border-bottom: 1px solid var(--border-color);
            font-size: 14px;
        }}
        tr:hover td {{
            background-color: rgba(255, 255, 255, 0.02);
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 11px;
            letter-spacing: 0.5px;
        }}
        .compliant {{ background-color: var(--success-glow); color: var(--success-color); border: 1px solid var(--success-color); }}
        .partial {{ background-color: var(--warning-glow); color: var(--warning-color); border: 1px solid var(--warning-color); }}
        .non-compliant {{ background-color: var(--error-glow); color: var(--error-color); border: 1px solid var(--error-color); }}
        
        .risk-badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; }}
        .risk-low {{ background-color: rgba(16, 185, 129, 0.2); color: var(--success-color); }}
        .risk-medium {{ background-color: rgba(245, 158, 11, 0.2); color: var(--warning-color); }}
        .risk-high {{ background-color: rgba(239, 68, 68, 0.2); color: var(--error-color); }}
        
        .tech-badge {{
            background-color: var(--code-bg);
            border: 1px solid var(--border-color);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-family: monospace;
        }}
        
        .gap-box {{
            background-color: rgba(239, 68, 68, 0.05); border-left: 4px solid var(--error-color);
            padding: 15px 20px; border-radius: 0 8px 8px 0; margin-bottom: 20px; font-size: 14px;
        }}
        .gap-box.compliant-box {{ border-left: 4px solid var(--success-color); background-color: rgba(16, 185, 129, 0.05); }}
        
        pre {{ background-color: var(--code-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 15px; overflow-x: auto; margin: 0; }}
        code {{ font-family: 'Courier New', Courier, monospace; font-size: 13.5px; color: #e5e7eb; }}
        .code-container {{ position: relative; }}
        .copy-btn {{
            position: absolute; top: 10px; right: 10px; background-color: var(--card-bg);
            border: 1px solid var(--border-color); color: var(--text-color); padding: 4px 8px;
            font-size: 11px; border-radius: 4px; cursor: pointer;
        }}
        footer {{ text-align: center; margin-top: 50px; color: var(--text-muted); font-size: 12px; border-top: 1px solid var(--border-color); padding-top: 20px; }}
        
        .score-circle {{
            width: 80px; height: 80px; border-radius: 50%;
            border: 6px solid #232d42; display: flex; align-items: center; justify-content: center;
            font-size: 20px; font-weight: 700; margin: 0 auto;
        }}
    </style>
    <script>
        function toggleAccordion(idx) {{
            var content = document.getElementById("accordion-" + idx);
            var label = document.querySelector(".open-label-" + idx);
            if (content.style.display === "none" || content.style.display === "") {{
                content.style.display = "table-row";
                if (label) label.textContent = "Fermer";
            }} else {{
                content.style.display = "none";
                if (label) label.textContent = "Cliquer pour ouvrir";
            }}
        }}
    </script>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Tableau de Bord : IAC-G.R.C-Auditor_ AGENT</h1>
                <p class="subtitle">Analyse de sécurité multi-fichiers : <code>{folder_path}</code></p>
            </div>
            <div>
                <div class="score-circle" style="border-color: {score_color}; color: {score_color};">
                    {compliance_score}%
                </div>
            </div>
        </header>
        
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-title">Fichiers Scannés</div>
                <div class="kpi-value">{total_files}</div>
            </div>
            <div class="kpi-card" style="border-bottom: 4px solid var(--success-color);">
                <div class="kpi-title">Conformes</div>
                <div class="kpi-value" style="color: var(--success-color);">{compliant_files}</div>
            </div>
            <div class="kpi-card" style="border-bottom: 4px solid var(--warning-color);">
                <div class="kpi-title">Partiels</div>
                <div class="kpi-value" style="color: var(--warning-color);">{partial_files}</div>
            </div>
            <div class="kpi-card" style="border-bottom: 4px solid var(--error-color);">
                <div class="kpi-title">Non Conformes</div>
                <div class="kpi-value" style="color: var(--error-color);">{non_compliant_files}</div>
            </div>
            <div class="kpi-card" style="text-align: left; display: flex; align-items: center; justify-content: center; font-size: 13.5px; color: var(--text-muted);">
                Ce tableau de bord consolidé regroupe l'audit préventif de sécurité de votre dépôt d'infrastructure par rapport à ISO 27001 et NIS2.
            </div>
        </div>
        
        <div class="card">
            <h2>Inventaire des Fichiers et États d'Audit</h2>
            <table>
                <thead>
                    <tr>
                        <th>Nom du Fichier</th>
                        <th>Type d'Actif</th>
                        <th>Statut GRC</th>
                        <th>Niveau de Risque</th>
                        <th style="text-align: right;">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>Généré automatiquement par l'analyseur autonome GRC Cybersecurity Compliance Auditor.</p>
        </footer>
    </div>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

# =====================================================================
# G. Concise Point-by-Point Pedagogical Intro
# =====================================================================
def print_pedagogical_intro():
    """
    Prints a highly concise, point-by-point educational introduction of the GRC tool.
    """
    print("\n====================================================================")
    print("                    IAC-G.R.C-Auditor_ AGENT")
    print("====================================================================")
    print("Cet outil est un AUDITEUR DE CONFORMITE CYBERSECURITE automatise.")
    print("Il permet de valider la securite de vos fichiers de configuration technique")
    print("AVANT leur deploiement sur vos serveurs en production (DevSecOps).")
    
    print("\n[+] CONCEPTS CLES (A QUOI SERT L'OUTIL ?) :")
    print("  1. Audit Preventif : Analyse les fichiers d'infrastructure (Ansible, Terraform, K8s).")
    print("  2. Traduction Reglementaire : Relie la technique brute aux exigences ISO 27001 et NIS2.")
    print("  3. Analyse Zero-Trust : Toute valeur manquante ou ambigue est declaree NON CONFORME.")
    print("  4. Aide a la Decision : Genere des explications detaillees et le code correctif exact.")
    print("  5. Blocage DevSecOps : Empeche l'integration de failles via vos pipelines de CI/CD.")
    
    print("\n[+] FONCTIONNEMENT INTERNE (PARSER-TO-REASONER) :")
    print("  - Etape 1 : Le PARSER (Python standard) extrait le code technique localement (100% prive).")
    print("  - Etape 2 : Le REASONER (IA locale/distante) juge la conformite semantique s'il y a un risque.")
    print("  - Etape 3 : Le REPORTER genere des explications detaillees et des rapports HTML interactifs.")
    
    print("\n[+] QUAND ET COMMENT L'IA INTERVIENT-ELLE (REASONER PHASE) ?")
    print("  L'IA est appelee precisement a l'Etape 3 (Le Raisonneur). Le script Python ne fait")
    print("  qu'extraire le texte technique (le Parser). L'IA intervient car les programmes standards")
    print("  (regex, linters) sont incapables de comprendre le contexte ou le but d'une regle de securite.")
    print("  L'IA lit sémantiquement votre configuration, comprend s'il y a un ecart par rapport aux normes,")
    print("  et etablit elle-meme le lien dynamique avec les failles CWE et CVE associees.")
    
    print("\n[+] INTERET MAJEUR POUR L'ANALYSE FORENSIC (POST-MORTEM) :")
    print("  Le script etablit une preuve d'audit de conformite datante et verifiee à chaque commit.")
    print("  En cas d'incident ou d'intrusion sur vos serveurs (analyse Forensic après attaque) :")
    print("  les enqueteurs peuvent remonter l'historique et identifier si les serveurs compromis ont")
    print("  ete deployes avec des configurations deviantes, quelles failles (CVE/CWE) y etaient presentes,")
    print("  et si des regles de securite avaient ete contournees lors de l'audit de build.")
    
    print("\n[+] CRITERES DE DECISION : POURQUOI UTILISER (OU NON) CE SCRIPT ?")
    print("  * POURQUOI L'UTILISER :")
    print("    - Pour automatiser les revues de securite longues et manuelles.")
    print("    - Pour bloquer de maniere infaillible l'introduction de failles connues en production.")
    print("    - Pour presenter des preuves tangibles de conformite pour les certifications ISO 27001.")
    print("  * QUAND NE PAS S'Y LIMITER :")
    print("    - L'outil fait de l'audit statique technique (sur le code de configuration avant deploiement).")
    print("    - Il ne verifie pas les modifications manuelles faites en direct sur la production (audit dynamique).")
    print("    - Il doit donc etre complete par des scans de vulnerabilites dynamiques periodiques.")
    
    print("\n[+] FONCTIONNALITES PRINCIPALES DISPONIBLES :")
    print("  * --file <fichier> : Scanne un fichier specifique (avec --control).")
    print("  * --dir <dossier>   : Parcourt recursivement tout un dossier pour un audit complet.")
    print("  * --strict         : Mode CI/CD. Echoue (code 1) en cas de faille, avec rapports verbeux.")
    print("  * --check-setup    : Diagnostique les variables et teste la connexion a l'IA locale.")
    print("  * --output <path>  : Exporte un rapport HTML sombre premium (imprimable en PDF) ou MD.")
    print("  * --info           : Affiche cette explication detaillee pedagogique.")
    print("====================================================================\n")

# =====================================================================
# Main Orchestrator CLI
# =====================================================================
def main():
    parser = argparse.ArgumentParser(
        description="GRC Cybersecurity Compliance Auditor (Parser-to-Reasoner)",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False # Disable standard help to show our pedagogical intro instead
    )
    # Custom help argument
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit.")
    parser.add_argument("--info", action="store_true", help="Print point-by-point pedagogical introduction.")
    parser.add_argument("--file", help="Path to the configuration file (Ansible, Terraform, etc.) to scan.")
    parser.add_argument(
        "--control", 
        choices=list(MAPPING_MATRIX.keys()), 
        help="Target control to evaluate against:\n"
             "  - SSH_HARDENING: Audit SSH secure configurations\n"
             "  - DB_HARDENING: Audit Database configurations\n"
             "  - K8S_HARDENING: Audit Kubernetes cluster settings"
    )
    parser.add_argument("--dir", help="Scan all configuration files recursively inside a target directory.")
    parser.add_argument("--provider", choices=["ollama", "anthropic", "openai", "gemini"], help="AI provider override.")
    parser.add_argument("--model", help="AI model name override (e.g. 'gemma2:2b', 'gpt-4o-mini').")
    parser.add_argument("--host", help="Custom host url for Ollama (e.g., http://localhost:11434).")
    parser.add_argument("--key", help="API key override for the chosen AI provider.")
    parser.add_argument("--output", help="Path to export the report (ends in .html or .md).")
    parser.add_argument("--strict", action="store_true", help="DevSecOps Mode: exit with error code (1) if non-compliant, with full diagnostics.")
    parser.add_argument("--check-setup", action="store_true", help="Diagnose current environment config and connection.")

    args = parser.parse_args()

    # 1. Custom help/info display
    if args.help or args.info:
        print_pedagogical_intro()
        return

    # 2. Setup diagnostic option
    if args.check_setup:
        print("====================================================================")
        print("             IAC-G.R.C-Auditor_ AGENT - DIAGNOSTIC")
        print("====================================================================")
        det_prov, det_val, det_model = detect_provider()
        print("\n[+] DIAGNOSTIC DU SYSTÈME D'AUDIT LOCAL :")
        print(f"    * Fournisseur détecté  : {det_prov.upper()}")
        print(f"    * Modèle par défaut    : {det_model}")
        
        if det_prov == "ollama":
            print(f"    * Hôte Ollama ciblé    : {det_val}")
            print("    * Test de connexion en cours...")
            try:
                with urllib.request.urlopen(f"{det_val.rstrip('/')}/api/tags", timeout=5) as response:
                    print("    * [OK] Le service Ollama est actif et répond sur le port local.")
            except Exception as e:
                print(f"    * [ALERTE] Échec de la connexion à Ollama : {e}")
                print("      Avez-vous démarré l'application Ollama ?")
        else:
            print("    * Clé d'API configurée : Oui (masquée pour sécurité)")
            
        print("\n[+] Contrôles GRC disponibles dans la matrice :")
        for key, details in MAPPING_MATRIX.items():
            print(f"    - {key} : {details['asset_name']}")
        return

    # 3. Dynamic setup of provider and model
    det_prov, det_val, det_model = detect_provider()
    provider = args.provider if args.provider else det_prov
    model = args.model if args.model else det_model
    
    auth_val = det_val
    if provider == "ollama" and args.host:
        auth_val = args.host
    elif provider != "ollama" and args.key:
        auth_val = args.key

    # Check if running in single-file, folder-scanning or demo mode
    all_evaluations: List[Dict[str, Any]] = []
    
    print("====================================================================")
    print("                IAC-G.R.C-Auditor_ AGENT - ENGINE")
    print("====================================================================")

    # CASE A: MULTI-FILE SCANNING
    if args.dir:
        target_dir = args.dir
        if not os.path.exists(target_dir):
            print(f"[!] Erreur : Le repertoire '{target_dir}' n'existe pas.")
            sys.exit(1)
            
        print(f"\n[Scan] Demarrage du scan recursif du dossier : '{target_dir}'")
        config_files: List[str] = []
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith((".yml", ".yaml", ".tf", ".conf")) and not file.startswith("mock_"):
                    config_files.append(os.path.join(root, file))
                    
        if not config_files:
            print("    [!] Aucun fichier de configuration technique trouve (.yml, .yaml, .tf, .conf).")
            sys.exit(0)
            
        print(f"    [+] {len(config_files)} fichier(s) de configuration detecte(s) pour audit.")
        
        for index, filepath in enumerate(config_files, 1):
            file_basename = os.path.basename(filepath)
            print(f"\n-------------------------------------------------------------")
            print(f"[{index}/{len(config_files)}] Audit en cours pour : '{file_basename}'")
            
            try:
                # Read
                content = read_iac_file(filepath)
                
                # Auto detect GRC control
                matched_control = auto_detect_control(file_basename, content)
                if not matched_control:
                    print("    [-] Impossible d'associer automatiquement ce fichier a la GRC. Fichier ignore.")
                    continue
                    
                print(f"    * Controle reglementaire identifie : {matched_control}")
                print("    * Envoi au raisonneur d'intelligence artificielle locale...")
                
                # Query LLM
                raw_response = evaluate_compliance(content, matched_control, provider, auth_val, model)
                report_data = extract_and_clean_json(raw_response)
                
                print(f"    * Resultat GRC : [{report_data['status']}] (Risque: {report_data['risk_score_assigned']})")
                
                all_evaluations.append({
                    "filename": file_basename,
                    "filepath": filepath,
                    "content": content,
                    "control_id": matched_control,
                    "report": report_data
                })
                
            except Exception as e:
                print(f"    [!] Echec de l'audit pour '{file_basename}' : {e}")

        # Post-scan analysis
        if not all_evaluations:
            print("\n[!] Aucun fichier n'a pu être audité avec succès.")
            sys.exit(1)
            
        total_audited = len(all_evaluations)
        compliant_count = sum(1 for e in all_evaluations if e["report"]["status"] == "COMPLIANT")
        partial_count = sum(1 for e in all_evaluations if e["report"]["status"] == "PARTIALLY_COMPLIANT")
        non_compliant_count = sum(1 for e in all_evaluations if e["report"]["status"] == "NON_COMPLIANT")
        score = int((compliant_count / total_audited) * 100)
        
        print("\n====================================================================")
        print("                  BILAN GLOBAL DE L'AUDIT DE DOSSIER")
        print("====================================================================")
        print(f"Dossier Scanne        : {target_dir}")
        print(f"Fichiers Traites      : {total_audited}")
        print(f"Score de Conformité   : {score}%")
        print(f"  - Conformes         : {compliant_count}")
        print(f"  - Partiels          : {partial_count}")
        print(f"  - Non Conformes     : {non_compliant_count}")
        print("====================================================================")

        # Output consolidated Dashboard
        out_dashboard = args.output if args.output else "dashboard_conformite.html"
        if out_dashboard:
            print(f"\n[Export] Generation du Tableau de Bord global...")
            generate_consolidated_dashboard(all_evaluations, out_dashboard, target_dir)
            print(f"    [+] Tableau de Bord interactif disponible : '{out_dashboard}'")

        # CI/CD Strict enforcement
        if args.strict and (non_compliant_count > 0 or any(e["report"]["risk_score_assigned"] == "HIGH" for e in all_evaluations)):
            print("\n[!] DevSecOps CI/CD : Blocage de deploiement en cours (Score insuffisant ou risque High).")
            print("    Les fichiers suivants comportent des failles critiques :")
            for e in all_evaluations:
                if e["report"]["status"] == "NON_COMPLIANT" or e["report"]["risk_score_assigned"] == "HIGH":
                    print(f"      - {e['filename']} (Risque: {e['report']['risk_score_assigned']})")
                    print(f"        CVEs / CWEs Associes : {e['report'].get('associated_cves_or_cwes', 'Aucun')}")
                    print(f"        Gap : {e['report']['technical_gap']}")
                    print(f"        Fix : {e['report']['remediation_command']}\n")
            sys.exit(1)
        else:
            print("\n[+] Validation DevSecOps : Aucun blocage requis.")
            sys.exit(0)

    # CASE B: SINGLE FILE AUDIT or DEFAULT DEMO Mode
    else:
        is_demo_mode = False
        if args.file:
            if not args.control:
                print("[!] Erreur : Vous devez spécifier un contrôle (--control) pour analyser un fichier.")
                sys.exit(1)
            target_file = args.file
            control_key = args.control
        else:
            # Launch default DEMO / TUTORIAL mode
            print("\n[*] Aucun fichier spécifié. Lancement du MODE DÉMONSTRATION / TUTORIEL.")
            print("[*] Génération d'un fichier de test Ansible vulnérable...")
            target_file = "mock_vulnerable_playbook.yml"
            control_key = "SSH_HARDENING"
            is_demo_mode = True
            
            mock_yaml = """# VULNERABLE CONFIGURATION FOR TESTING
- name: Deploy Legacy Web App
  hosts: webservers
  tasks:
    - name: Ensure SSH is running
      ansible.builtin.service:
        name: sshd
        state: started
    # FAILLE : Authentification par mot de passe autorisée
    - name: Allow password auth for ease of access
      ansible.builtin.lineinfile:
        path: /etc/ssh/sshd_config
        line: "PasswordAuthentication yes"
"""
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(mock_yaml)

        # Execution verbose
        try:
            print(f"\n[Etape 1/5] Ingestion du fichier cible : '{target_file}'")
            config_content = read_iac_file(target_file)
            print("    [+] Fichier charge avec succes et extrait en memoire.")

            print(f"[Etape 2/5] Liaison avec la matrice reglementaire GRC : '{control_key}'")
            mapping = MAPPING_MATRIX[control_key]
            print(f"    * Actif vise  : {mapping['asset_name']}")
            print(f"    * Normes ISO  : {', '.join(mapping['iso_controls'])}")
            print(f"    * Norme NIS2  : {', '.join(mapping['nis2_controls'])}")

            print(f"[Etape 3/5] Envoi au raisonneur d'intelligence artificielle ({provider.upper()} - Modele: {model})")
            print("    * Analyse en cours (cette etape sur CPU peut prendre quelques secondes)...")
            
            raw_evaluation = evaluate_compliance(config_content, control_key, provider, auth_val, model)
            
            print("[Etape 4/5] Nettoyage et validation du format JSON retourne")
            compliance_report = extract_and_clean_json(raw_evaluation)
            print("    [+] Rapport d'audit extrait et valide avec succes par rapport au schema.")

            print("[Etape 5/5] Analyse du statut de conformité et des ecarts")
            print("\n====================================================================")
            print("                 RESULTAT DE L'AUDIT DE CONFORMITE")
            print("====================================================================")
            
            status_color = "[CONFORME]" if compliance_report["status"] == "COMPLIANT" else "[PARTIELLEMENT CONFORME]" if compliance_report["status"] == "PARTIALLY_COMPLIANT" else "[NON CONFORME]"
            print(f"Statut Global : {status_color}")
            print(f"Niveau de Risque : {compliance_report['risk_score_assigned']}")
            print(f"CVEs / CWEs Associes : {compliance_report.get('associated_cves_or_cwes', 'Aucun')}")
            print(f"\nDescription de la Faille (Gap) :\n{compliance_report['technical_gap']}")
            print(f"\nInstruction de Remediation preconisee :\n{compliance_report['remediation_command']}")
            print("====================================================================")

            # Output formatting
            out_file = args.output if args.output else "rapport_demo_ssh.html" if is_demo_mode else None

            if out_file:
                print(f"\n[Export] Generation du rapport d'audit ecrit...")
                if out_file.endswith(".html"):
                    generate_html_report(compliance_report, out_file, config_content, control_key)
                    print(f"    [+] Rapport HTML interactif genere a l'emplacement : '{out_file}'")
                else:
                    if not out_file.endswith(".md"):
                        out_file = out_file + ".md"
                    generate_markdown_report(compliance_report, out_file, config_content, control_key)
                    print(f"    [+] Rapport Markdown genere a l'emplacement : '{out_file}'")

            # CI/CD enforcement
            if args.strict and (compliance_report["status"] == "NON_COMPLIANT" or compliance_report["risk_score_assigned"] == "HIGH"):
                print("\n[!] DevSecOps CI/CD : Blocage de deploiement en cours (Risque High ou Non Conforme).")
                print(f"    Fichier concerne : {target_file}")
                print(f"    CVEs / CWEs Associes : {compliance_report.get('associated_cves_or_cwes', 'Aucun')}")
                print(f"    Faille technique : {compliance_report['technical_gap']}")
                print(f"    Fix : {compliance_report['remediation_command']}")
                sys.exit(1)
            else:
                if args.strict:
                    print("\n[+] Validation DevSecOps : Aucun blocage requis.")
                sys.exit(0)

        except Exception as e:
            print(f"\n[!] ERREUR lors de l'execution du pipeline d'audit : {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        finally:
            if is_demo_mode and os.path.exists("mock_vulnerable_playbook.yml"):
                try:
                    os.remove("mock_vulnerable_playbook.yml")
                    print("\n[*] Fichier temporaire de demonstration nettoye.")
                except Exception:
                    pass

if __name__ == "__main__":
    main()
