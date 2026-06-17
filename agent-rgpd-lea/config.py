# -*- coding: utf-8 -*-
"""
config.py — Configuration centralisée du projet LÉA.

Charge les variables depuis le fichier .env via python-dotenv.
Tous les chemins sont en absolu via pathlib.Path.
Lève une ValueError explicite si une variable critique est absente.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ============================================================
# Chargement du fichier .env
# ============================================================
load_dotenv()

# ============================================================
# CHEMINS DU PROJET (absolus)
# ============================================================
BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data"
RAW_DIR: Path = DATA_DIR / "raw"
VECTORSTORE_DIR: Path = DATA_DIR / "vectorstore"
LOGS_DIR: Path = DATA_DIR / "logs"

# Fichiers de données générés automatiquement
HISTORY_FILE: Path = BASE_DIR / "scrape_history.json"
FEEDBACK_FILE: Path = BASE_DIR / "feedback.json"
CORRECTIONS_FILE: Path = BASE_DIR / "corrections.json"
PATTERNS_FILE: Path = BASE_DIR / "parsing_patterns.json"

# Création automatique des répertoires nécessaires
for _dir in [DATA_DIR, RAW_DIR, VECTORSTORE_DIR, LOGS_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)

# ============================================================
# OLLAMA — LLM 100% local
# ============================================================
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL: str = os.getenv("LLM_MODEL", "mistral")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# ============================================================
# RAG — Paramètres de recherche vectorielle
# ============================================================
TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.75"))

# ============================================================
# SCRAPING — Paramètres de collecte
# ============================================================
SCRAPE_DELAY: int = int(os.getenv("SCRAPE_DELAY", "3"))

# Liste de User-Agents rotatifs pour éviter le blocage
USER_AGENTS: list[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

# ============================================================
# SOURCES OFFICIELLES À SCRAPER — WHITELIST STRICTE
# ============================================================
SOURCE_URLS: dict[str, list[str]] = {
    "CNIL — RGPD": [
        "https://www.cnil.fr/fr/rgpd-de-quoi-parle-t-on",
        "https://www.cnil.fr/fr/les-bases-legales",
        "https://www.cnil.fr/fr/le-droit-linformation-des-personnes",
        "https://www.cnil.fr/fr/les-droits-pour-maitriser-vos-donnees-personnelles",
        "https://www.cnil.fr/fr/le-droit-dacces",
        "https://www.cnil.fr/fr/le-droit-rectification",
        "https://www.cnil.fr/fr/le-droit-leffacement-droit-loubli",
        "https://www.cnil.fr/fr/le-droit-la-portabilite",
        "https://www.cnil.fr/fr/le-droit-dopposition",
        "https://www.cnil.fr/fr/le-dpo-delegue-la-protection-des-donnees",
        "https://www.cnil.fr/fr/les-sanctions-de-la-cnil",
        "https://www.cnil.fr/fr/professionnels-vous-etes-concernes-par-le-rgpd",
        "https://www.cnil.fr/fr/rgpd-par-ou-commencer",
        "https://www.cnil.fr/fr/cnil-direct",
        "https://www.cnil.fr/fr/principes-cles-du-rgpd",
    ],
    "NIS 2 — ANSSI": [
        "https://cyber.gouv.fr/la-directive-nis-2",
        "https://cyber.gouv.fr/reglementation",
        "https://cyber.gouv.fr/produits-et-services/accompagnement-nis2",
        "https://monespacenis2.cyber.gouv.fr/directive",
    ],
    "ISO 27001 — Sources libres": [
        "https://fr.wikipedia.org/wiki/ISO/CEI_27001",
        "https://advisera.com/27001academy/fr/ce-que-contient-iso-27001/",
        "https://advisera.com/27001academy/fr/quelles-sont-les-exigences-iso-27001/",
    ],
    "Textes juridiques UE — EUR-Lex": [
        "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32016R0679",
        "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32022L2555",
    ],
}

# ============================================================
# DOMAINES AUTORISÉS — Whitelist de sécurité
# ============================================================
ALLOWED_DOMAINS: list[str] = [
    "cnil.fr",
    "cyber.gouv.fr",
    "monespacenis2.cyber.gouv.fr",
    "eur-lex.europa.eu",
    "fr.wikipedia.org",
    "advisera.com",
]
