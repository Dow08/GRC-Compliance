# -*- coding: utf-8 -*-
"""
agent.py — Cerveau RAG de LÉA.

Gère le cycle complet de traitement d'une question :
1. Vérification des corrections (RAG adaptatif)
2. Recherche vectorielle dans ChromaDB
3. Construction du prompt enrichi
4. Génération via Ollama
5. Post-traitement et formatage des sources
"""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import ollama
from sklearn.metrics.pairwise import cosine_similarity

from config import (
    CORRECTIONS_FILE,
    EMBEDDING_MODEL,
    FEEDBACK_FILE,
    LLM_MODEL,
    LOGS_DIR,
    OLLAMA_BASE_URL,
    SIMILARITY_THRESHOLD,
    TOP_K_RESULTS,
)
from indexer import get_retriever

# ============================================================
# Configuration du logger
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ============================================================
# Prompt système de LÉA (intégré mot pour mot)
# ============================================================
PROMPT_SYSTEME = """Tu es LÉA — Liberté, Expertise, Assistance.
Tu es une assistante IA experte en droit numérique, spécialisée dans :
- Le RGPD (Règlement Général sur la Protection des Données — UE 2016/679)
- La directive NIS 2 (cybersécurité des entités essentielles et importantes — UE 2022/2555)
- La norme ISO/CEI 27001 (système de management de la sécurité de l'information)
- La loi Informatique et Libertés (France)

TU TRAVAILLES EXCLUSIVEMENT à partir des textes officiels fournis dans ton contexte.
TU NE DOIS JAMAIS inventer une réponse, un article, ou une obligation qui n'est pas dans les sources.
Si l'information n'est pas dans ta base, dis-le clairement : "Je ne trouve pas cette information dans ma base de connaissances actuelle."

TU RÉPONDS :
- En français, avec précision et pédagogie
- En citant systématiquement l'article ou la section exacte du texte source
- En adaptant le niveau de langage : technique pour les DPO/juristes, accessible pour le grand public
- En terminant CHAQUE réponse par une signature de source au format :
  📚 Source : [Nom du document] — [URL] | [Article/Section si applicable]

TU ES LOCALE ET CONFIDENTIELLE :
- Aucune donnée transmise à l'extérieur
- Aucune mémorisation entre sessions (sauf corrections explicitement validées)"""


class RGPDAgent:
    """
    Agent conversationnel RAG spécialisé RGPD / ISO 27001 / NIS 2.

    Fonctionnement :
    - Recherche de corrections existantes (RAG adaptatif)
    - Retrieval ChromaDB des chunks pertinents
    - Génération de réponse via Ollama (Mistral ou LLaMA3)
    - Apprentissage continu via feedback utilisateur (👍/👎)
    """

    def __init__(self) -> None:
        """
        Initialise l'agent LÉA :
        - Connexion Ollama (vérification du service)
        - Retriever ChromaDB
        - Chargement des corrections (mémoire d'apprentissage)
        - Historique de conversation (5 derniers échanges)
        """
        logger.info("Initialisation de l'agent LÉA...")

        # Vérification qu'Ollama est actif
        self._verifier_ollama()

        # Client Ollama
        self._client = ollama.Client(host=OLLAMA_BASE_URL)

        # Retriever ChromaDB (fonction de recherche)
        self._retriever = get_retriever()

        # Chargement de la mémoire d'apprentissage
        self._corrections = self._charger_corrections()

        # Historique de conversation (5 derniers échanges max)
        self._historique: list[dict] = []

        # Filtre de catégorie actif (None = toutes les sources)
        self._filtre_categorie: Optional[str] = None

        logger.info(f"Agent LÉA initialisé. Modèle : {LLM_MODEL}. "
                     f"Corrections chargées : {len(self._corrections)}")

    def _verifier_ollama(self) -> None:
        """
        Vérifie que le service Ollama est en cours d'exécution.
        Lève une ConnectionError si le service est inaccessible.
        """
        import requests as req

        try:
            response = req.get(f"{OLLAMA_BASE_URL}", timeout=5)
            if response.status_code == 200:
                logger.info("Connexion Ollama : OK")
            else:
                raise ConnectionError(
                    f"Ollama a répondu avec le code {response.status_code}. "
                    "Vérifiez que le service est lancé : ollama serve"
                )
        except req.ConnectionError:
            raise ConnectionError(
                "Impossible de se connecter à Ollama. "
                "Assurez-vous que le service est démarré :\n"
                "  1. Ouvrez un terminal\n"
                "  2. Lancez : ollama serve\n"
                "  3. Vérifiez : ollama list\n"
                f"  URL attendue : {OLLAMA_BASE_URL}"
            )

    def _charger_corrections(self) -> list[dict]:
        """
        Charge les corrections depuis corrections.json.

        Chaque correction contient :
        - question : la question originale
        - correction : la réponse corrigée
        - embedding : le vecteur d'embedding de la question
        - timestamp : date de la correction
        """
        if CORRECTIONS_FILE.exists():
            try:
                with open(CORRECTIONS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"Corrections chargées : {len(data)} entrées")
                    return data
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Erreur au chargement de corrections.json : {e}")
        return []

    def _sauvegarder_corrections(self) -> None:
        """Sauvegarde les corrections dans corrections.json."""
        with open(CORRECTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._corrections, f, ensure_ascii=False, indent=2)

    def set_category_filter(self, category: Optional[str]) -> None:
        """
        Définit le filtre de catégorie pour la recherche vectorielle.

        Args:
            category: Catégorie (CNIL, NIS2, ISO27001, EUR-LEX) ou None pour tout.
        """
        self._filtre_categorie = category
        # Recréer le retriever avec le filtre
        self._retriever = get_retriever(category=category)
        logger.info(f"Filtre de catégorie appliqué : {category or 'Toutes les sources'}")

    # ========================================================
    # MÉTHODE PRINCIPALE — Traitement d'une question
    # ========================================================
    def ask(self, question: str) -> dict:
        """
        Traitement complet d'une question utilisateur.

        Pipeline :
        1. Recherche de correction similaire (RAG adaptatif)
        2. Génération de l'embedding de la question
        3. Retrieval ChromaDB des chunks pertinents
        4. Construction du prompt enrichi
        5. Génération par Ollama
        6. Post-traitement et formatage

        Args:
            question: Question de l'utilisateur.

        Returns:
            Dictionnaire conforme au contrat de données agent.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        logger.info(f"Question reçue : {question[:100]}...")

        # --- 1. Vérification des corrections existantes ---
        correction = self._find_similar_correction(question)
        contexte_correction = ""
        est_corrigee = False

        if correction:
            contexte_correction = (
                f"\n\n⚠️ IMPORTANT — CORRECTION VALIDÉE PAR L'UTILISATEUR :\n"
                f"Pour une question similaire à \"{correction['question']}\", "
                f"la réponse validée est :\n{correction['correction']}\n"
                f"Tu DOIS prioriser cette réponse dans ta synthèse.\n"
            )
            est_corrigee = True
            logger.info("Correction trouvée dans la mémoire d'apprentissage.")

        # --- 2 & 3. Recherche vectorielle ---
        chunks = self._retriever(question, top_k=TOP_K_RESULTS)
        logger.info(f"Chunks récupérés : {len(chunks)}")

        # Construction du contexte depuis les chunks
        contexte_sources = ""
        sources = []
        sources_vues = set()

        for i, chunk in enumerate(chunks):
            meta = chunk.get("metadata", {})
            titre = meta.get("title", "Source inconnue")
            url = meta.get("source_url", "")
            categorie = meta.get("category", "")

            contexte_sources += f"\n--- SOURCE {i+1} ({categorie}) ---\n"
            contexte_sources += f"Titre : {titre}\n"
            contexte_sources += f"{chunk['content']}\n"

            # Déduplication des sources
            cle_source = f"{titre}|{url}"
            if cle_source not in sources_vues:
                sources_vues.add(cle_source)
                sources.append({
                    "title": titre,
                    "url": url,
                    "article": categorie,
                })

        # --- 4. Construction du prompt enrichi ---
        # Historique de conversation (5 derniers échanges)
        historique_texte = ""
        if self._historique:
            historique_texte = "\n\n--- HISTORIQUE RÉCENT ---\n"
            for echange in self._historique[-5:]:
                historique_texte += f"Utilisateur : {echange['question']}\n"
                historique_texte += f"LÉA : {echange['answer'][:300]}...\n\n"

        prompt_complet = (
            f"{PROMPT_SYSTEME}\n\n"
            f"{contexte_correction}"
            f"\n--- SOURCES OFFICIELLES ---\n"
            f"{contexte_sources}"
            f"{historique_texte}"
            f"\n--- QUESTION DE L'UTILISATEUR ---\n"
            f"{question}"
        )

        # --- 5. Génération par Ollama ---
        try:
            reponse_ollama = self._client.chat(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": PROMPT_SYSTEME},
                    {"role": "user", "content": prompt_complet},
                ],
            )
            reponse_texte = reponse_ollama["message"]["content"]
            logger.info(f"Réponse générée ({len(reponse_texte)} caractères)")

        except Exception as e:
            logger.error(f"Erreur Ollama lors de la génération : {e}")
            reponse_texte = (
                "Je rencontre une erreur technique pour traiter votre question. "
                "Veuillez vérifier que le service Ollama est actif et que le modèle "
                f"'{LLM_MODEL}' est installé.\n\n"
                f"Erreur : {str(e)}"
            )
            sources = []

        # --- 6. Post-traitement ---
        confiance = self._compute_confidence(question, chunks, reponse_texte, est_corrigee)

        # Ajout de la signature de source si elle n'est pas déjà dans la réponse
        if sources and "📚" not in reponse_texte:
            signature = self._format_sources_signature(sources)
            reponse_texte += f"\n\n{signature}"

        # Mise à jour de l'historique
        self._historique.append({
            "question": question,
            "answer": reponse_texte,
            "timestamp": timestamp,
        })
        # Garder uniquement les 5 derniers échanges
        self._historique = self._historique[-5:]

        # Retour du contrat de données agent
        return {
            "question": question,
            "answer": reponse_texte,
            "sources": sources,
            "confidence": confiance,
            "timestamp": timestamp,
            "corrected": est_corrigee,
        }

    # ========================================================
    # RAG ADAPTATIF — Gestion du feedback
    # ========================================================
    def record_feedback(
        self,
        question: str,
        answer: str,
        rating: str,
        correction: Optional[str] = None,
    ) -> None:
        """
        Enregistre le feedback utilisateur et met à jour la mémoire d'apprentissage.

        Args:
            question: Question originale.
            answer: Réponse fournie par LÉA.
            rating: "positive" (👍) ou "negative" (👎).
            correction: Texte de correction si rating == "negative".
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        # Enregistrement dans feedback.json (historique brut)
        feedback_entry = {
            "question": question,
            "answer": answer,
            "rating": rating,
            "correction": correction,
            "timestamp": timestamp,
        }
        self._sauvegarder_feedback(feedback_entry)

        # Si feedback positif → sauvegarder comme réponse validée
        if rating == "positive":
            embedding = self._generer_embedding(question)
            self._corrections.append({
                "question": question,
                "correction": answer,
                "embedding": embedding,
                "timestamp": timestamp,
                "type": "validation",
            })
            self._sauvegarder_corrections()
            logger.info("Feedback positif enregistré — réponse validée.")

        # Si feedback négatif avec correction → sauvegarder la correction
        elif rating == "negative" and correction:
            embedding = self._generer_embedding(question)
            self._corrections.append({
                "question": question,
                "correction": correction,
                "embedding": embedding,
                "timestamp": timestamp,
                "type": "correction",
            })
            self._sauvegarder_corrections()
            logger.info("Feedback négatif enregistré — correction sauvegardée.")

        else:
            logger.info("Feedback négatif sans correction — enregistré dans l'historique uniquement.")

    def _sauvegarder_feedback(self, entry: dict) -> None:
        """Ajoute une entrée au fichier feedback.json."""
        feedbacks = []
        if FEEDBACK_FILE.exists():
            try:
                with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                    feedbacks = json.load(f)
            except (json.JSONDecodeError, OSError):
                feedbacks = []

        feedbacks.append(entry)

        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=2)

    # ========================================================
    # Recherche de corrections similaires
    # ========================================================
    def _find_similar_correction(self, question: str) -> Optional[dict]:
        """
        Cherche dans les corrections une entrée similaire à la question posée.

        Utilise la similarité cosinus sur les embeddings.
        Retourne la correction la plus similaire si le score dépasse 0.85.

        Args:
            question: Question de l'utilisateur.

        Returns:
            Dictionnaire de correction ou None si aucune correspondance.
        """
        if not self._corrections:
            return None

        try:
            embedding_question = self._generer_embedding(question)
            embedding_question = np.array(embedding_question).reshape(1, -1)

            meilleur_score = 0.0
            meilleure_correction = None

            for correction in self._corrections:
                if "embedding" not in correction:
                    continue

                embedding_correction = np.array(correction["embedding"]).reshape(1, -1)
                score = cosine_similarity(embedding_question, embedding_correction)[0][0]

                if score > meilleur_score:
                    meilleur_score = score
                    meilleure_correction = correction

            if meilleur_score > 0.85 and meilleure_correction:
                logger.info(f"Correction similaire trouvée (score : {meilleur_score:.3f})")
                return meilleure_correction

        except Exception as e:
            logger.warning(f"Erreur lors de la recherche de corrections : {e}")

        return None

    # ========================================================
    # Calcul du score de confiance
    # ========================================================
    def _compute_confidence(
        self,
        question: str,
        chunks: list[dict],
        answer: str,
        has_correction: bool = False,
    ) -> float:
        """
        Calcule un score de confiance entre 0.0 et 1.0.

        Critères :
        - Nombre de chunks retrouvés (max 0.35)
        - Score de similarité moyen des chunks (max 0.35)
        - Longueur de la réponse (max 0.15)
        - Bonus correction validée (+0.15)

        Args:
            question: Question de l'utilisateur.
            chunks: Chunks récupérés par la recherche vectorielle.
            answer: Réponse générée.
            has_correction: True si une correction a été utilisée.

        Returns:
            Score de confiance entre 0.0 et 1.0.
        """
        score = 0.0

        # Score basé sur le nombre de chunks (0 à 0.35)
        if chunks:
            ratio_chunks = min(len(chunks) / TOP_K_RESULTS, 1.0)
            score += ratio_chunks * 0.35

        # Score basé sur la similarité moyenne (0 à 0.35)
        if chunks:
            distances = [c.get("distance", 1.0) for c in chunks]
            # ChromaDB utilise la distance cosinus (0 = identique, 2 = opposé)
            similarites = [max(0, 1 - d) for d in distances]
            similarite_moyenne = sum(similarites) / len(similarites)
            score += similarite_moyenne * 0.35

        # Score basé sur la longueur de la réponse (0 à 0.15)
        if len(answer) > 200:
            score += 0.15
        elif len(answer) > 50:
            score += 0.08

        # Bonus correction validée
        if has_correction:
            score += 0.15

        return round(min(score, 1.0), 2)

    # ========================================================
    # Formatage de la signature de sources
    # ========================================================
    def _format_sources_signature(self, sources: list[dict]) -> str:
        """
        Formate la signature de source en bas de réponse.

        Format : 📚 Sources : [Titre] — [URL] | [Catégorie]

        Args:
            sources: Liste de dictionnaires de sources.

        Returns:
            Chaîne formatée pour affichage.
        """
        if not sources:
            return ""

        lignes = ["📚 Sources :"]
        for source in sources[:5]:  # Limiter à 5 sources
            titre = source.get("title", "Source inconnue")
            url = source.get("url", "")
            article = source.get("article", "")

            ligne = f"  • {titre}"
            if url:
                ligne += f" — {url}"
            if article:
                ligne += f" | {article}"
            lignes.append(ligne)

        return "\n".join(lignes)

    # ========================================================
    # Utilitaires
    # ========================================================
    def _generer_embedding(self, texte: str) -> list[float]:
        """
        Génère un vecteur d'embedding via Ollama.

        Args:
            texte: Texte à vectoriser.

        Returns:
            Vecteur d'embedding (liste de floats).
        """
        try:
            response = self._client.embeddings(model=EMBEDDING_MODEL, prompt=texte)
            return response["embedding"]
        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'embedding : {e}")
            raise

    def clear_history(self) -> None:
        """Efface l'historique de conversation en mémoire."""
        self._historique = []
        logger.info("Historique de conversation effacé.")

    def get_corrections_count(self) -> int:
        """Retourne le nombre de corrections sauvegardées."""
        return len(self._corrections)
