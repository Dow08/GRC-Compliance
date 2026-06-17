# -*- coding: utf-8 -*-
"""
indexer.py — Pipeline d'indexation pour LÉA.

Lit les fichiers Markdown scrapés, les découpe en chunks,
génère les embeddings via Ollama (nomic-embed-text) et les stocke
dans ChromaDB pour la recherche vectorielle.
"""

import hashlib
import json
import traceback
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import chromadb
import numpy as np
import ollama

from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    LOGS_DIR,
    OLLAMA_BASE_URL,
    RAW_DIR,
    TOP_K_RESULTS,
    VECTORSTORE_DIR,
)

# ============================================================
# Configuration du logger
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / f"indexer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ============================================================
# Nom de la collection ChromaDB
# ============================================================
COLLECTION_NAME = "lea_rgpd"

# Fichier de suivi des hashs pour l'indexation incrémentale
HASHES_FILE = VECTORSTORE_DIR / "indexed_hashes.json"

# Limite de taille du texte brut avant chunking (200 000 caractères ≈ 100 pages)
# Les fichiers EUR-Lex peuvent faire 900 Ko, ce qui provoque un MemoryError
# lors du nettoyage regex. On tronque pour rester dans des limites raisonnables.
MAX_RAW_CHARS = 100_000


# ============================================================
# Parsing de l'en-tête YAML des fichiers Markdown
# ============================================================
def _extraire_metadonnees(contenu: str) -> tuple[dict, str]:
    """
    Extrait les métadonnées de l'en-tête YAML d'un fichier Markdown.

    Args:
        contenu: Contenu brut du fichier Markdown.

    Returns:
        Tuple (métadonnées, corps_du_texte).
    """
    metadonnees = {
        "title": "",
        "source": "",
        "domain": "",
        "category": "",
        "scraped_at": "",
    }

    # Recherche du bloc YAML entre ---
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", contenu, re.DOTALL)
    if match:
        bloc_yaml = match.group(1)
        corps = contenu[match.end():]

        for ligne in bloc_yaml.split("\n"):
            ligne = ligne.strip()
            if ":" in ligne:
                cle, valeur = ligne.split(":", 1)
                cle = cle.strip().strip('"').strip("'")
                valeur = valeur.strip().strip('"').strip("'")
                if cle in metadonnees:
                    metadonnees[cle] = valeur

        return metadonnees, corps

    return metadonnees, contenu


# ============================================================
# Nettoyage du texte
# ============================================================
def _nettoyer_contenu(texte: str) -> str:
    """
    Nettoie le texte avant le chunking :
    - Tronque à MAX_RAW_CHARS pour éviter les MemoryError
    - Supprime les balises HTML résiduelles
    - Normalise les espaces
    - Supprime les caractères spéciaux inutiles
    """
    # Tronquer le texte si trop long pour éviter MemoryError sur les regex
    if len(texte) > MAX_RAW_CHARS:
        logger.warning(f"Texte tronqué de {len(texte)} à {MAX_RAW_CHARS} caractères avant nettoyage.")
        texte = texte[:MAX_RAW_CHARS]

    try:
        # Suppression des balises HTML résiduelles
        texte = re.sub(r"<[^>]+>", "", texte)
        # Remplacement des tabulations par des espaces
        texte = texte.replace("\t", " ")
        # Normalisation des espaces multiples
        texte = re.sub(r" {2,}", " ", texte)
        # Normalisation des sauts de ligne multiples
        texte = re.sub(r"\n{3,}", "\n\n", texte)
    except MemoryError:
        logger.warning("MemoryError pendant le nettoyage, retour du texte brut tronqué.")
        texte = texte[:MAX_RAW_CHARS]
    return texte.strip()


# ============================================================
# Chunking du texte
# ============================================================
def chunk_document(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Découpe un texte en chunks de taille fixe avec chevauchement.

    Le découpage se fait par mots pour éviter de couper au milieu d'un mot.
    Le chevauchement assure la continuité sémantique entre les chunks.

    Args:
        text: Texte à découper.
        chunk_size: Nombre approximatif de caractères par chunk.
        chunk_overlap: Nombre de caractères de chevauchement entre chunks.

    Returns:
        Liste de chunks textuels.
    """
    texte = _nettoyer_contenu(text)

    if not texte:
        return []

    # Si le texte est plus court qu'un chunk, le retourner tel quel
    if len(texte) <= chunk_size:
        return [texte]

    chunks = []
    debut = 0
    pas_minimum = max(chunk_size - chunk_overlap, 1)  # Avancement minimum garanti

    while debut < len(texte):
        fin = min(debut + chunk_size, len(texte))

        # Chercher la fin de phrase la plus proche (seulement si on n'est pas à la fin)
        if fin < len(texte):
            # On cherche une coupure naturelle dans la 2e moitié du chunk uniquement
            # pour éviter de trouver un point trop proche de debut
            zone_recherche_debut = debut + (chunk_size // 2)
            meilleure_coupure = texte.rfind(".", zone_recherche_debut, fin)
            if meilleure_coupure == -1:
                meilleure_coupure = texte.rfind("\n", zone_recherche_debut, fin)
            if meilleure_coupure == -1:
                meilleure_coupure = texte.rfind(" ", zone_recherche_debut, fin)
            if meilleure_coupure > debut:
                fin = meilleure_coupure + 1

        chunk = texte[debut:fin].strip()
        if chunk:
            chunks.append(chunk)

        # Toujours avancer d'au moins pas_minimum pour éviter les boucles infinies
        prochain_debut = fin - chunk_overlap
        debut = max(prochain_debut, debut + pas_minimum)

        if fin >= len(texte):
            break

    return chunks


# ============================================================
# Calcul de hash MD5 pour l'indexation incrémentale
# ============================================================
def compute_hash(filepath: Path) -> str:
    """
    Calcule le hash MD5 d'un fichier pour détecter les modifications.

    Args:
        filepath: Chemin du fichier.

    Returns:
        Hash MD5 en hexadécimal.
    """
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        for bloc in iter(lambda: f.read(8192), b""):
            hasher.update(bloc)
    return hasher.hexdigest()


# ============================================================
# Gestion des hashs indexés
# ============================================================
def _charger_hashes() -> dict[str, str]:
    """Charge le fichier de suivi des hashs déjà indexés."""
    if HASHES_FILE.exists():
        try:
            with open(HASHES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _sauvegarder_hashes(hashes: dict[str, str]) -> None:
    """Sauvegarde le fichier de suivi des hashs."""
    with open(HASHES_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, ensure_ascii=False, indent=2)


# ============================================================
# Génération d'embeddings via Ollama
# ============================================================
# Limite de caractères pour nomic-embed-text (~8192 tokens ≈ 28000 chars max)
# On tronque à 8000 chars par sécurité pour rester dans la fenêtre de contexte
MAX_EMBED_CHARS = 8000

# Nombre de tentatives et timeout pour l'API Ollama
EMBED_TIMEOUT = 120  # secondes
EMBED_RETRIES = 3


def _generer_embedding(texte: str) -> list[float]:
    """
    Génère un vecteur d'embedding pour un texte donné via Ollama.

    Inclut :
    - Tronquage automatique si le texte dépasse MAX_EMBED_CHARS
    - Timeout de 120 secondes
    - 3 tentatives avec backoff exponentiel

    Args:
        texte: Texte à vectoriser.

    Returns:
        Vecteur d'embedding (liste de floats).
    """
    # Tronquer le texte si nécessaire
    if len(texte) > MAX_EMBED_CHARS:
        texte = texte[:MAX_EMBED_CHARS]
        logger.debug(f"Texte tronqué à {MAX_EMBED_CHARS} caractères pour l'embedding.")

    derniere_erreur = None
    for tentative in range(1, EMBED_RETRIES + 1):
        try:
            client = ollama.Client(host=OLLAMA_BASE_URL, timeout=EMBED_TIMEOUT)
            response = client.embeddings(model=EMBEDDING_MODEL, prompt=texte)
            return response["embedding"]
        except Exception as e:
            derniere_erreur = e
            logger.warning(
                f"Tentative {tentative}/{EMBED_RETRIES} échouée : {type(e).__name__}: {repr(e)}"
            )
            if tentative < EMBED_RETRIES:
                time.sleep(2 ** tentative)  # Backoff exponentiel : 2s, 4s

    logger.error(f"Échec après {EMBED_RETRIES} tentatives : {repr(derniere_erreur)}")
    raise derniere_erreur


def _generer_embeddings_batch(textes: list[str]) -> list[list[float]]:
    """
    Génère des embeddings pour un lot de textes.

    Args:
        textes: Liste de textes à vectoriser.

    Returns:
        Liste de vecteurs d'embedding.
    """
    embeddings = []
    for i, texte in enumerate(textes):
        try:
            embedding = _generer_embedding(texte)
            embeddings.append(embedding)
        except Exception as e:
            logger.error(f"  ⚠ Chunk {i} ignoré (embedding impossible) : {repr(e)}")
            # Vecteur nul en fallback pour ne pas casser le batch
            embeddings.append(None)
    return embeddings


# ============================================================
# Initialisation du client ChromaDB
# ============================================================
def _obtenir_client_chroma() -> chromadb.PersistentClient:
    """Retourne une instance du client ChromaDB persistant."""
    return chromadb.PersistentClient(path=str(VECTORSTORE_DIR))


def _obtenir_collection() -> chromadb.Collection:
    """
    Retourne la collection ChromaDB pour LÉA.
    La crée si elle n'existe pas encore.
    """
    client = _obtenir_client_chroma()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


# ============================================================
# Construction complète de la base vectorielle
# ============================================================
def build_vectorstore() -> None:
    """
    Construit la base vectorielle à partir de zéro.

    Processus :
    1. Lit tous les fichiers .md de /data/raw/
    2. Chunke chaque document
    3. Génère les embeddings via Ollama
    4. Stocke dans ChromaDB avec métadonnées
    5. Persiste les hashs pour l'indexation incrémentale

    Attention : cette opération supprime la collection existante !
    """
    logger.info("=" * 60)
    logger.info("CONSTRUCTION COMPLÈTE DE LA BASE VECTORIELLE")
    logger.info("=" * 60)

    debut = time.time()

    # Obtenir la liste des fichiers Markdown
    fichiers_md = sorted(RAW_DIR.glob("*.md"))
    if not fichiers_md:
        logger.warning("Aucun fichier Markdown trouvé dans /data/raw/. "
                        "Lancez d'abord le scraper : python scraper.py")
        return

    logger.info(f"Fichiers trouvés : {len(fichiers_md)}")

    # Supprimer la collection existante et en créer une nouvelle
    client = _obtenir_client_chroma()
    try:
        client.delete_collection(COLLECTION_NAME)
        logger.info("Collection existante supprimée.")
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    hashes = {}
    total_chunks = 0
    compteur_docs = 0

    for fichier in fichiers_md:
        try:
            contenu = fichier.read_text(encoding="utf-8")
            metadonnees, corps = _extraire_metadonnees(contenu)

            # Tronquer le corps avant chunking pour éviter les MemoryError
            if len(corps) > MAX_RAW_CHARS:
                logger.warning(f"  ⚠ {fichier.name} : corps tronqué de {len(corps):,} à {MAX_RAW_CHARS:,} caractères")
                corps = corps[:MAX_RAW_CHARS]

            chunks = chunk_document(corps)

            if not chunks:
                logger.warning(f"Aucun chunk créé pour : {fichier.name}")
                continue

            # Génération des embeddings
            embeddings = _generer_embeddings_batch(chunks)

            # Filtrer les chunks dont l'embedding a échoué (None)
            chunks_valides = []
            embeddings_valides = []
            for idx, (c, emb) in enumerate(zip(chunks, embeddings)):
                if emb is not None:
                    chunks_valides.append(c)
                    embeddings_valides.append(emb)

            if not chunks_valides:
                logger.warning(f"  ⚠ {fichier.name} : aucun chunk vectorisé, fichier ignoré.")
                continue

            # Préparation des données pour ChromaDB
            ids = [f"{fichier.stem}_chunk_{i}" for i in range(len(chunks_valides))]
            metadonnees_chunks = [
                {
                    "source_url": metadonnees.get("source", ""),
                    "category": metadonnees.get("category", ""),
                    "domain": metadonnees.get("domain", ""),
                    "title": metadonnees.get("title", ""),
                    "chunk_index": i,
                    "fichier_source": fichier.name,
                }
                for i in range(len(chunks_valides))
            ]

            # Insertion dans ChromaDB
            collection.add(
                ids=ids,
                documents=chunks_valides,
                embeddings=embeddings_valides,
                metadatas=metadonnees_chunks,
            )

            # Suivi du hash
            hashes[fichier.name] = compute_hash(fichier)
            total_chunks += len(chunks_valides)
            compteur_docs += 1

            logger.info(f"  ✅ {fichier.name} : {len(chunks_valides)} chunks indexés")

        except Exception as e:
            logger.error(f"  ❌ Erreur pour {fichier.name} : {type(e).__name__}: {repr(e)}")
            logger.debug(traceback.format_exc())

    # Sauvegarde des hashs
    _sauvegarder_hashes(hashes)

    duree = time.time() - debut
    logger.info(f"\n{'=' * 60}")
    logger.info(f"BASE VECTORIELLE CONSTRUITE")
    logger.info(f"  Documents traités : {compteur_docs}")
    logger.info(f"  Chunks créés     : {total_chunks}")
    logger.info(f"  Durée            : {duree:.1f} secondes")
    logger.info(f"{'=' * 60}")


# ============================================================
# Mise à jour incrémentale de la base vectorielle
# ============================================================
def update_vectorstore() -> None:
    """
    Met à jour la base vectorielle de manière incrémentale.

    Compare les hashs MD5 des fichiers actuels avec ceux déjà indexés.
    N'indexe que les fichiers nouveaux ou modifiés.
    Affiche le delta : +N nouveaux chunks, =M inchangés.
    """
    logger.info("=" * 60)
    logger.info("MISE À JOUR INCRÉMENTALE DE LA BASE VECTORIELLE")
    logger.info("=" * 60)

    debut = time.time()

    fichiers_md = sorted(RAW_DIR.glob("*.md"))
    if not fichiers_md:
        logger.warning("Aucun fichier Markdown trouvé dans /data/raw/.")
        return

    hashes_existants = _charger_hashes()
    collection = _obtenir_collection()

    nouveaux = 0
    inchanges = 0
    total_nouveaux_chunks = 0

    for fichier in fichiers_md:
        hash_actuel = compute_hash(fichier)
        hash_enregistre = hashes_existants.get(fichier.name)

        if hash_actuel == hash_enregistre:
            inchanges += 1
            continue

        # Fichier nouveau ou modifié → indexer
        try:
            contenu = fichier.read_text(encoding="utf-8")
            metadonnees, corps = _extraire_metadonnees(contenu)

            # Tronquer le corps avant chunking pour éviter les MemoryError
            if len(corps) > MAX_RAW_CHARS:
                logger.warning(f"  ⚠ {fichier.name} : corps tronqué de {len(corps):,} à {MAX_RAW_CHARS:,} caractères")
                corps = corps[:MAX_RAW_CHARS]

            chunks = chunk_document(corps)

            if not chunks:
                continue

            # Si le fichier existait déjà, supprimer les anciens chunks
            if hash_enregistre:
                try:
                    anciens_ids = [f"{fichier.stem}_chunk_{i}" for i in range(1000)]
                    collection.delete(ids=anciens_ids)
                except Exception:
                    pass  # Ignorer si les IDs n'existent pas

            # Génération des embeddings et insertion
            embeddings = _generer_embeddings_batch(chunks)

            # Filtrer les chunks dont l'embedding a échoué (None)
            chunks_valides = []
            embeddings_valides = []
            for idx, (c, emb) in enumerate(zip(chunks, embeddings)):
                if emb is not None:
                    chunks_valides.append(c)
                    embeddings_valides.append(emb)

            if not chunks_valides:
                logger.warning(f"  ⚠ {fichier.name} : aucun chunk n'a pu être vectorisé, fichier ignoré.")
                continue

            ids = [f"{fichier.stem}_chunk_{i}" for i in range(len(chunks_valides))]
            metadonnees_chunks = [
                {
                    "source_url": metadonnees.get("source", ""),
                    "category": metadonnees.get("category", ""),
                    "domain": metadonnees.get("domain", ""),
                    "title": metadonnees.get("title", ""),
                    "chunk_index": i,
                    "fichier_source": fichier.name,
                }
                for i in range(len(chunks_valides))
            ]

            collection.add(
                ids=ids,
                documents=chunks_valides,
                embeddings=embeddings_valides,
                metadatas=metadonnees_chunks,
            )

            hashes_existants[fichier.name] = hash_actuel
            nouveaux += 1
            total_nouveaux_chunks += len(chunks_valides)

            if len(chunks_valides) < len(chunks):
                logger.info(f"  ✅ {fichier.name} : {len(chunks_valides)}/{len(chunks)} chunks indexés (certains ignorés)")
            else:
                logger.info(f"  ✅ {fichier.name} : {len(chunks_valides)} chunks indexés (nouveau/modifié)")

        except Exception as e:
            logger.error(f"  ❌ Erreur pour {fichier.name} : {type(e).__name__}: {repr(e)}")
            logger.debug(traceback.format_exc())

    # Sauvegarde des hashs mis à jour
    _sauvegarder_hashes(hashes_existants)

    duree = time.time() - debut
    logger.info(f"\n{'=' * 60}")
    logger.info(f"MISE À JOUR TERMINÉE")
    logger.info(f"  +{total_nouveaux_chunks} nouveaux chunks ({nouveaux} fichiers)")
    logger.info(f"  ={inchanges} fichiers inchangés")
    logger.info(f"  Durée : {duree:.1f} secondes")
    logger.info(f"{'=' * 60}")


# ============================================================
# Retriever pour la recherche vectorielle
# ============================================================
def get_retriever(category: Optional[str] = None):
    """
    Retourne une fonction de recherche dans la base vectorielle.

    Args:
        category: Filtre optionnel par catégorie (CNIL, NIS2, ISO27001, EUR-LEX).

    Returns:
        Fonction de recherche qui prend une question et retourne les chunks pertinents.
    """
    collection = _obtenir_collection()

    def rechercher(question: str, top_k: int = TOP_K_RESULTS) -> list[dict]:
        """
        Recherche les chunks les plus pertinents pour une question.

        Args:
            question: Question de l'utilisateur.
            top_k: Nombre de résultats à retourner.

        Returns:
            Liste de dictionnaires avec le contenu, les métadonnées et le score.
        """
        try:
            embedding_question = _generer_embedding(question)

            # Préparer le filtre par catégorie si spécifié
            where_filter = None
            if category:
                where_filter = {"category": category}

            resultats = collection.query(
                query_embeddings=[embedding_question],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )

            # Formater les résultats
            chunks_trouves = []
            if resultats and resultats["documents"]:
                for i in range(len(resultats["documents"][0])):
                    chunks_trouves.append({
                        "content": resultats["documents"][0][i],
                        "metadata": resultats["metadatas"][0][i] if resultats["metadatas"] else {},
                        "distance": resultats["distances"][0][i] if resultats["distances"] else 1.0,
                    })

            return chunks_trouves

        except Exception as e:
            logger.error(f"Erreur lors de la recherche vectorielle : {e}")
            return []

    return rechercher


# ============================================================
# Statistiques de la base vectorielle
# ============================================================
def get_stats() -> dict:
    """
    Retourne les statistiques de la base vectorielle.

    Returns:
        Dictionnaire avec le nombre total de chunks, la répartition
        par catégorie et la date de dernière mise à jour.
    """
    try:
        collection = _obtenir_collection()
        total = collection.count()

        # Répartition par catégorie
        repartition = {}
        for categorie in ["CNIL", "NIS2", "ISO27001", "EUR-LEX"]:
            try:
                resultat = collection.get(
                    where={"category": categorie},
                    include=[],
                )
                repartition[categorie] = len(resultat["ids"]) if resultat["ids"] else 0
            except Exception:
                repartition[categorie] = 0

        # Date de dernière mise à jour
        derniere_maj = "Jamais"
        if HASHES_FILE.exists():
            derniere_maj = datetime.fromtimestamp(
                HASHES_FILE.stat().st_mtime, tz=timezone.utc
            ).strftime("%d/%m/%Y à %H:%M")

        return {
            "total_chunks": total,
            "repartition": repartition,
            "derniere_mise_a_jour": derniere_maj,
        }

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques : {e}")
        return {
            "total_chunks": 0,
            "repartition": {},
            "derniere_mise_a_jour": "Erreur",
        }


# ============================================================
# Point d'entrée pour exécution directe
# ============================================================
if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("📚 LÉA — Indexation de la base de connaissances")
    print("=" * 60)
    print()

    # Mode incrémental par défaut, --full pour reconstruire
    if "--full" in sys.argv:
        print("🔄 Mode : reconstruction complète")
        build_vectorstore()
    else:
        print("🔄 Mode : mise à jour incrémentale (--full pour tout reconstruire)")
        update_vectorstore()

    # Affichage des statistiques
    stats = get_stats()
    print()
    print(f"📊 Statistiques de la base :")
    print(f"   Total de chunks : {stats['total_chunks']}")
    for cat, nb in stats.get("repartition", {}).items():
        print(f"   {cat} : {nb} chunks")
    print(f"   Dernière mise à jour : {stats['derniere_mise_a_jour']}")
