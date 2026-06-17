# -*- coding: utf-8 -*-
"""
scraper.py — Moteur de scraping multi-sources pour LÉA.

Collecte les contenus des sites officiels (CNIL, ANSSI, EUR-Lex, etc.)
en respectant les robots.txt, le rate limiting et la whitelist de domaines.
Utilise BeautifulSoup en priorité avec fallback Selenium si nécessaire.
"""

import hashlib
import json
import logging
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from config import (
    ALLOWED_DOMAINS,
    HISTORY_FILE,
    LOGS_DIR,
    PATTERNS_FILE,
    RAW_DIR,
    SCRAPE_DELAY,
    SOURCE_URLS,
    USER_AGENTS,
)

# ============================================================
# Configuration du logger
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ============================================================
# Sélecteurs CSS par domaine (extraction intelligente)
# ============================================================
DOMAIN_SELECTORS: dict[str, list[str]] = {
    "cnil.fr": ["article.content", "div.field-item", "article", "main"],
    "cyber.gouv.fr": ["main", "article", "div.content"],
    "monespacenis2.cyber.gouv.fr": ["main", "article", "div.content"],
    "eur-lex.europa.eu": ["div#text", "div.eli-main-title", "div#TexteOnly", "article"],
    "fr.wikipedia.org": ["div#mw-content-text", "div.mw-parser-output"],
    "advisera.com": ["article", "div.entry-content", "main"],
}

# Sélecteurs de repli universels
FALLBACK_SELECTORS: list[str] = ["main", "article", "body"]


# ============================================================
# Gestion de la mémoire des patterns (parsing_patterns.json)
# ============================================================
def charger_patterns() -> dict:
    """Charge les patterns CSS mémorisés depuis le fichier JSON."""
    if PATTERNS_FILE.exists():
        try:
            with open(PATTERNS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            logger.warning("Fichier parsing_patterns.json corrompu, réinitialisation.")
    return {}


def sauvegarder_pattern(domaine: str, selecteur: str) -> None:
    """Sauvegarde un sélecteur CSS validé pour un domaine donné."""
    patterns = charger_patterns()
    if domaine not in patterns:
        patterns[domaine] = []

    # Vérifier si le sélecteur existe déjà
    for p in patterns[domaine]:
        if p["selecteur"] == selecteur:
            p["derniere_utilisation"] = datetime.now(timezone.utc).isoformat()
            p["deprecated"] = False
            break
    else:
        patterns[domaine].append({
            "selecteur": selecteur,
            "derniere_utilisation": datetime.now(timezone.utc).isoformat(),
            "deprecated": False,
        })

    with open(PATTERNS_FILE, "w", encoding="utf-8") as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)


def marquer_pattern_deprecie(domaine: str, selecteur: str) -> None:
    """Marque un pattern comme déprécié après un échec."""
    patterns = charger_patterns()
    if domaine in patterns:
        for p in patterns[domaine]:
            if p["selecteur"] == selecteur:
                p["deprecated"] = True
                break
        with open(PATTERNS_FILE, "w", encoding="utf-8") as f:
            json.dump(patterns, f, ensure_ascii=False, indent=2)


def obtenir_selecteurs_pour_domaine(domaine: str) -> list[str]:
    """
    Retourne les sélecteurs CSS pour un domaine donné.
    Priorité : patterns mémorisés non dépréciés > domaine connu > fallback.
    """
    selecteurs = []

    # 1. Patterns mémorisés validés en priorité
    patterns = charger_patterns()
    if domaine in patterns:
        for p in patterns[domaine]:
            if not p.get("deprecated", False):
                selecteurs.append(p["selecteur"])

    # 2. Sélecteurs connus pour le domaine
    for cle_domaine, sels in DOMAIN_SELECTORS.items():
        if cle_domaine in domaine:
            for s in sels:
                if s not in selecteurs:
                    selecteurs.append(s)
            break

    # 3. Fallback universel
    for s in FALLBACK_SELECTORS:
        if s not in selecteurs:
            selecteurs.append(s)

    return selecteurs


# ============================================================
# Validation d'URL et vérification de sécurité
# ============================================================
def valider_url(url: str) -> bool:
    """
    Valide qu'une URL est sûre à scraper :
    - Schéma HTTPS uniquement
    - Domaine dans la whitelist ALLOWED_DOMAINS
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    # Schéma HTTPS obligatoire
    if parsed.scheme != "https":
        logger.debug(f"URL rejetée (schéma non HTTPS) : {url}")
        return False

    # Vérification du domaine dans la whitelist
    domaine = parsed.netloc.lower().replace("www.", "")
    for domaine_autorise in ALLOWED_DOMAINS:
        if domaine == domaine_autorise or domaine.endswith(f".{domaine_autorise}"):
            return True

    logger.debug(f"URL rejetée (domaine non autorisé) : {url}")
    return False


def verifier_robots_txt(url: str) -> bool:
    """
    Vérifie que le fichier robots.txt autorise l'accès à l'URL.
    En cas d'erreur de lecture du robots.txt, on autorise par défaut.
    """
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()

        autorise = rp.can_fetch("*", url)
        if not autorise:
            logger.info(f"robots.txt interdit l'accès à : {url}")
        return autorise
    except Exception as e:
        logger.warning(f"Impossible de lire robots.txt pour {url} : {e}. Accès autorisé par défaut.")
        return True


def obtenir_domaine(url: str) -> str:
    """Extrait le domaine d'une URL (sans www.)."""
    return urlparse(url).netloc.lower().replace("www.", "")


def obtenir_user_agent() -> str:
    """Retourne un User-Agent aléatoire depuis la liste configurée."""
    return random.choice(USER_AGENTS)


# ============================================================
# Scraper dynamique Selenium (fallback)
# ============================================================
class DynamicScraper:
    """
    Scraper Selenium headless utilisé comme fallback
    lorsque BeautifulSoup ne récupère pas assez de contenu (< 200 caractères).
    """

    def __init__(self) -> None:
        """Initialise le driver Chrome en mode headless."""
        self._driver = None

    def _initialiser_driver(self) -> None:
        """Démarre le navigateur Chrome headless avec webdriver-manager."""
        if self._driver is not None:
            return

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager

            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument(f"user-agent={obtenir_user_agent()}")
            options.page_load_strategy = "normal"

            service = Service(ChromeDriverManager().install())
            self._driver = webdriver.Chrome(service=service, options=options)
            self._driver.set_page_load_timeout(15)
            logger.info("Driver Selenium initialisé avec succès.")
        except Exception as e:
            logger.error(f"Impossible d'initialiser Selenium : {e}")
            self._driver = None
            raise

    def scrape(self, url: str) -> str:
        """
        Récupère le HTML brut d'une page via Selenium.

        Args:
            url: URL de la page à scraper.

        Returns:
            Le code HTML source de la page.
        """
        self._initialiser_driver()
        if self._driver is None:
            raise RuntimeError("Driver Selenium non disponible.")

        logger.info(f"[Selenium] Chargement de : {url}")
        self._driver.get(url)
        time.sleep(2)  # Attente du rendu JavaScript
        return self._driver.page_source

    def close(self) -> None:
        """Libère le driver Selenium proprement."""
        if self._driver is not None:
            try:
                self._driver.quit()
                logger.info("Driver Selenium fermé proprement.")
            except Exception as e:
                logger.warning(f"Erreur lors de la fermeture du driver : {e}")
            finally:
                self._driver = None


# ============================================================
# Instance globale du scraper dynamique (lazy loading)
# ============================================================
_dynamic_scraper: Optional[DynamicScraper] = None


def _obtenir_dynamic_scraper() -> DynamicScraper:
    """Retourne l'instance singleton du DynamicScraper."""
    global _dynamic_scraper
    if _dynamic_scraper is None:
        _dynamic_scraper = DynamicScraper()
    return _dynamic_scraper


# ============================================================
# Fonctions principales de scraping
# ============================================================
def scrape_page(url: str) -> dict:
    """
    Scrape une page web et retourne les données selon le contrat de données.

    Processus :
    1. Validation de l'URL (HTTPS + domaine autorisé)
    2. Vérification robots.txt
    3. Tentative BeautifulSoup
    4. Fallback Selenium si contenu < 200 caractères
    5. Extraction intelligente par sélecteurs CSS selon le domaine

    Args:
        url: URL de la page à scraper.

    Returns:
        Dictionnaire conforme au contrat de données scraper.
    """
    # Validation de sécurité
    if not valider_url(url):
        return {
            "status": "error",
            "url_source": url,
            "title": "",
            "content": "",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "items_count": 0,
            "domain": "",
        }

    # Vérification robots.txt
    if not verifier_robots_txt(url):
        return {
            "status": "error",
            "url_source": url,
            "title": "",
            "content": "Accès interdit par robots.txt",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "items_count": 0,
            "domain": obtenir_domaine(url),
        }

    domaine = obtenir_domaine(url)
    selecteurs = obtenir_selecteurs_pour_domaine(domaine)
    timestamp = datetime.now(timezone.utc).isoformat()

    # --- Tentative avec BeautifulSoup ---
    contenu = ""
    titre = ""
    selecteur_utilise = ""

    try:
        headers = {"User-Agent": obtenir_user_agent()}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or "utf-8"

        soup = BeautifulSoup(response.text, "lxml")

        # Extraction du titre
        tag_titre = soup.find("title")
        titre = tag_titre.get_text(strip=True) if tag_titre else ""

        # Extraction du contenu avec les sélecteurs
        for sel in selecteurs:
            element = soup.select_one(sel)
            if element:
                texte = _nettoyer_texte(element.get_text(separator="\n", strip=True))
                if len(texte) > len(contenu):
                    contenu = texte
                    selecteur_utilise = sel

    except requests.RequestException as e:
        logger.warning(f"Erreur BeautifulSoup pour {url} : {e}")

    # --- Fallback Selenium si contenu insuffisant ---
    if len(contenu) < 200:
        logger.info(f"Contenu insuffisant ({len(contenu)} car.), fallback Selenium pour : {url}")
        try:
            ds = _obtenir_dynamic_scraper()
            html = ds.scrape(url)
            soup = BeautifulSoup(html, "lxml")

            if not titre:
                tag_titre = soup.find("title")
                titre = tag_titre.get_text(strip=True) if tag_titre else ""

            for sel in selecteurs:
                element = soup.select_one(sel)
                if element:
                    texte = _nettoyer_texte(element.get_text(separator="\n", strip=True))
                    if len(texte) > len(contenu):
                        contenu = texte
                        selecteur_utilise = sel

        except Exception as e:
            logger.error(f"Échec Selenium pour {url} : {e}")

    # Mémorisation du pattern utilisé
    if selecteur_utilise and len(contenu) >= 200:
        sauvegarder_pattern(domaine, selecteur_utilise)
    elif selecteur_utilise:
        marquer_pattern_deprecie(domaine, selecteur_utilise)

    statut = "success" if len(contenu) >= 100 else "error"

    if statut == "error":
        logger.warning(f"Contenu final insuffisant pour {url} ({len(contenu)} caractères).")

    return {
        "status": statut,
        "url_source": url,
        "title": titre,
        "content": contenu,
        "timestamp": timestamp,
        "items_count": len(contenu.split("\n")) if contenu else 0,
        "domain": domaine,
    }


def _nettoyer_texte(texte: str) -> str:
    """
    Nettoie le texte extrait :
    - Supprime les balises HTML résiduelles
    - Normalise les espaces et sauts de ligne
    - Supprime les caractères de contrôle
    """
    # Suppression des balises HTML résiduelles
    texte = re.sub(r"<[^>]+>", "", texte)
    # Normalisation des espaces multiples
    texte = re.sub(r"[ \t]+", " ", texte)
    # Normalisation des sauts de ligne multiples
    texte = re.sub(r"\n{3,}", "\n\n", texte)
    # Suppression des espaces en début/fin de ligne
    lignes = [ligne.strip() for ligne in texte.split("\n")]
    texte = "\n".join(lignes)
    return texte.strip()


def _generer_slug(titre: str) -> str:
    """
    Génère un slug à partir du titre pour le nommage des fichiers.
    Exemple : 'Le droit d'accès - CNIL' → 'le-droit-dacces-cnil'
    """
    slug = titre.lower()
    slug = re.sub(r"[àáâãäå]", "a", slug)
    slug = re.sub(r"[èéêë]", "e", slug)
    slug = re.sub(r"[ìíîï]", "i", slug)
    slug = re.sub(r"[òóôõö]", "o", slug)
    slug = re.sub(r"[ùúûü]", "u", slug)
    slug = re.sub(r"[ç]", "c", slug)
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug[:80]  # Limiter la longueur


def _categorie_vers_prefixe(categorie: str) -> str:
    """Convertit le nom de catégorie en préfixe de fichier."""
    correspondances = {
        "CNIL — RGPD": "cnil",
        "NIS 2 — ANSSI": "nis2",
        "ISO 27001 — Sources libres": "iso27001",
        "Textes juridiques UE — EUR-Lex": "eurlex",
    }
    return correspondances.get(categorie, "divers")


# ============================================================
# Export en Markdown
# ============================================================
def export_to_markdown(data: dict, filepath: Path) -> None:
    """
    Exporte les données scrapées en fichier Markdown avec en-tête YAML.

    Args:
        data: Dictionnaire conforme au contrat de données scraper.
        filepath: Chemin de destination du fichier .md.
    """
    # Détermination de la catégorie depuis le domaine
    categorie = "Divers"
    domaine = data.get("domain", "")
    if "cnil" in domaine:
        categorie = "CNIL"
    elif "cyber.gouv" in domaine or "nis2" in domaine:
        categorie = "NIS2"
    elif "eur-lex" in domaine:
        categorie = "EUR-LEX"
    elif "wikipedia" in domaine or "advisera" in domaine:
        categorie = "ISO27001"

    en_tete = f"""---
title: "{data.get('title', 'Sans titre')}"
source: "{data.get('url_source', '')}"
domain: "{domaine}"
category: "{categorie}"
scraped_at: "{data.get('timestamp', '')}"
---

"""
    contenu = en_tete + data.get("content", "")

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(contenu)

    logger.info(f"Exporté : {filepath.name} ({len(data.get('content', ''))} caractères)")


# ============================================================
# Exploration récursive des liens internes
# ============================================================
def _extraire_liens_internes(url: str, html: str, domaine: str) -> list[str]:
    """
    Extrait les liens internes d'une page (même domaine uniquement).

    Args:
        url: URL de la page source.
        html: Contenu HTML de la page.
        domaine: Domaine autorisé pour le filtrage.

    Returns:
        Liste d'URLs internes uniques.
    """
    liens = []
    try:
        soup = BeautifulSoup(html, "lxml")
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            lien_complet = urljoin(url, href)

            # Filtrer : même domaine, HTTPS, pas un ancre, pas un fichier binaire
            parsed = urlparse(lien_complet)
            lien_domaine = parsed.netloc.lower().replace("www.", "")

            if (
                domaine in lien_domaine
                and parsed.scheme == "https"
                and not parsed.fragment
                and not any(lien_complet.lower().endswith(ext) for ext in [".pdf", ".jpg", ".png", ".gif", ".zip", ".doc"])
            ):
                # Nettoyer l'URL (supprimer les paramètres de tracking)
                lien_propre = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    # Garder uniquement les paramètres essentiels (ex: uri= pour EUR-Lex)
                    params_essentiels = [p for p in parsed.query.split("&") if p.startswith("uri=")]
                    if params_essentiels:
                        lien_propre += "?" + "&".join(params_essentiels)

                liens.append(lien_propre)

    except Exception as e:
        logger.warning(f"Erreur extraction liens de {url} : {e}")

    return list(set(liens))


# ============================================================
# Scraping complet de toutes les sources
# ============================================================
def scrape_all_sources() -> list[dict]:
    """
    Parcourt et scrape toutes les sources officielles définies dans SOURCE_URLS.

    Processus :
    - Parcours par catégorie avec barre de progression
    - Exploration récursive des liens internes (profondeur max 2)
    - Déduplication par URL
    - Export en Markdown dans /data/raw/
    - Mise à jour de l'historique de scraping

    Returns:
        Liste de tous les résultats de scraping (contrats de données).
    """
    resultats: list[dict] = []
    urls_visitees: set[str] = set()
    compteurs = {"total": 0, "succes": 0, "erreurs": 0}
    stats_par_source: dict[str, dict] = {}

    logger.info("=" * 60)
    logger.info("DÉBUT DU SCRAPING DE TOUTES LES SOURCES")
    logger.info("=" * 60)

    for categorie, urls in SOURCE_URLS.items():
        prefixe = _categorie_vers_prefixe(categorie)
        date_str = datetime.now().strftime("%Y-%m-%d")
        nb_categorie = 0
        nb_erreurs_cat = 0

        logger.info(f"\n📂 Catégorie : {categorie} ({len(urls)} URLs)")

        barre = tqdm(urls, desc=f"  {categorie}", unit="page", ncols=80)

        for url in barre:
            # Déduplication
            if url in urls_visitees:
                continue

            # Scrape de la page principale
            resultat = scrape_page(url)
            urls_visitees.add(url)
            compteurs["total"] += 1

            if resultat["status"] == "success":
                compteurs["succes"] += 1
                nb_categorie += 1

                # Export en Markdown
                slug = _generer_slug(resultat.get("title", "sans-titre"))
                nom_fichier = f"{prefixe}_{date_str}_{slug}.md"
                chemin_fichier = RAW_DIR / nom_fichier
                export_to_markdown(resultat, chemin_fichier)

                resultats.append(resultat)

                # Exploration récursive (profondeur 1 — liens de la page)
                try:
                    headers = {"User-Agent": obtenir_user_agent()}
                    resp = requests.get(url, headers=headers, timeout=15)
                    resp.encoding = resp.apparent_encoding or "utf-8"
                    liens_internes = _extraire_liens_internes(url, resp.text, obtenir_domaine(url))

                    # Limiter à 5 liens par page pour rester raisonnable
                    for lien in liens_internes[:5]:
                        if lien not in urls_visitees and valider_url(lien):
                            time.sleep(SCRAPE_DELAY)
                            sous_resultat = scrape_page(lien)
                            urls_visitees.add(lien)
                            compteurs["total"] += 1

                            if sous_resultat["status"] == "success":
                                compteurs["succes"] += 1
                                nb_categorie += 1
                                sous_slug = _generer_slug(sous_resultat.get("title", "sans-titre"))
                                sous_nom = f"{prefixe}_{date_str}_{sous_slug}.md"
                                sous_chemin = RAW_DIR / sous_nom

                                # Éviter les doublons de fichier
                                if not sous_chemin.exists():
                                    export_to_markdown(sous_resultat, sous_chemin)
                                    resultats.append(sous_resultat)
                            else:
                                compteurs["erreurs"] += 1
                                nb_erreurs_cat += 1

                except Exception as e:
                    logger.warning(f"Erreur exploration récursive depuis {url} : {e}")

            else:
                compteurs["erreurs"] += 1
                nb_erreurs_cat += 1

            # Respect du délai entre les requêtes
            time.sleep(SCRAPE_DELAY)

        stats_par_source[categorie] = {
            "pages_scrapees": nb_categorie,
            "erreurs": nb_erreurs_cat,
        }

        # Mise à jour de l'historique après chaque catégorie
        _mettre_a_jour_historique(categorie, nb_categorie, nb_erreurs_cat)

    # --- Résumé final ---
    logger.info("\n" + "=" * 60)
    logger.info("RÉSUMÉ DU SCRAPING")
    logger.info("=" * 60)
    for source, stats in stats_par_source.items():
        logger.info(f"  {source} : {stats['pages_scrapees']} pages, {stats['erreurs']} erreurs")
    logger.info(f"  TOTAL : {compteurs['total']} URLs traitées, "
                f"{compteurs['succes']} succès, {compteurs['erreurs']} erreurs")
    logger.info("=" * 60)

    # Fermeture du scraper Selenium si utilisé
    global _dynamic_scraper
    if _dynamic_scraper is not None:
        _dynamic_scraper.close()
        _dynamic_scraper = None

    return resultats


def _mettre_a_jour_historique(categorie: str, nb_pages: int, nb_erreurs: int) -> None:
    """
    Met à jour le fichier scrape_history.json après chaque catégorie.

    Args:
        categorie: Nom de la catégorie scrapée.
        nb_pages: Nombre de pages scrapées avec succès.
        nb_erreurs: Nombre d'erreurs rencontrées.
    """
    historique = {}
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                historique = json.load(f)
        except (json.JSONDecodeError, OSError):
            historique = {}

    if "scrapes" not in historique:
        historique["scrapes"] = []

    historique["scrapes"].append({
        "categorie": categorie,
        "date": datetime.now(timezone.utc).isoformat(),
        "pages_scrapees": nb_pages,
        "erreurs": nb_erreurs,
    })

    # Garder les 100 dernières entrées
    historique["scrapes"] = historique["scrapes"][-100:]
    historique["derniere_mise_a_jour"] = datetime.now(timezone.utc).isoformat()

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)


# ============================================================
# Point d'entrée pour exécution directe
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🔍 LÉA — Lancement du scraping des sources officielles")
    print("=" * 60)
    print()

    debut = time.time()
    resultats = scrape_all_sources()
    duree = time.time() - debut

    print()
    print(f"✅ Scraping terminé en {duree:.1f} secondes.")
    print(f"   {len(resultats)} pages collectées avec succès.")
    print(f"   Fichiers Markdown enregistrés dans : {RAW_DIR}")
