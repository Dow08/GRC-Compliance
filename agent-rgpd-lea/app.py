# -*- coding: utf-8 -*-
"""
app.py — Interface Streamlit Art Déco pour LÉA.

Point d'entrée principal de l'application.
Lance l'interface de chat avec le design noir & doré Art Déco.
Commande : streamlit run app.py
"""

import json
import time
from datetime import datetime

import requests
import streamlit as st

from config import CORRECTIONS_FILE, OLLAMA_BASE_URL, LLM_MODEL

# ============================================================
# Configuration de la page Streamlit
# ============================================================
st.set_page_config(
    page_title="LÉA — Expert RGPD · ISO 27001 · NIS 2",
    page_icon="⚖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ============================================================
# INJECTION CSS — Charte graphique Art Déco complète
# ============================================================
st.markdown("""
<style>
/* === IMPORTS GOOGLE FONTS === */
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;900&family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Courier+Prime:wght@400;700&display=swap');

/* === VARIABLES CSS === */
:root {
    --bg-primary: #0A0A0A;
    --bg-secondary: #111111;
    --bg-card: #141414;
    --bg-user-msg: #1A1400;
    --bg-lea-msg: #0D110D;
    --gold-primary: #C9A84C;
    --gold-light: #E8C97A;
    --gold-dark: #8B6914;
    --gold-shimmer: #F5E4A0;
    --gold-muted: #6B5020;
    --text-primary: #D4AF6E;
    --text-secondary: #9A7A3A;
    --text-muted: #5A4520;
    --border-thin: 1px solid #C9A84C;
    --border-thick: 2px solid #C9A84C;
    --relief-text: 1px 1px 2px #000000, 0 0 6px rgba(201, 168, 76, 0.25);
    --relief-box: 1px 1px 0px #000000, -1px -1px 0px #3A2800;
    --glow-gold: 0 0 12px rgba(201, 168, 76, 0.35);
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* === FOND GLOBAL === */
.stApp, .main, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-primary) !important;
    font-family: 'EB Garamond', Georgia, serif !important;
    color: var(--text-primary) !important;
}

/* === MASQUER ÉLÉMENTS STREAMLIT PARASITES === */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background-color: #0D0D0D !important;
    border-right: var(--border-thin) !important;
    box-shadow: 2px 0 15px rgba(201, 168, 76, 0.1);
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* === TITRE PRINCIPAL === */
.lea-header {
    text-align: center;
    padding: 2rem 1rem 1rem;
    border-bottom: var(--border-thin);
    margin-bottom: 2rem;
    background: linear-gradient(180deg, #1A1200 0%, transparent 100%);
}
.lea-title {
    font-family: 'Cinzel', serif;
    font-size: 2.8rem;
    font-weight: 900;
    color: var(--gold-light);
    text-shadow: var(--relief-text);
    letter-spacing: 0.15em;
    animation: shimmer 3s ease-in-out infinite;
}
.lea-subtitle {
    font-family: 'EB Garamond', serif;
    font-size: 1rem;
    color: var(--text-secondary);
    letter-spacing: 0.1em;
    margin-top: 0.3rem;
}
@keyframes shimmer {
    0%, 100% { text-shadow: var(--relief-text); }
    50% { text-shadow: 1px 1px 2px #000, 0 0 20px rgba(245, 228, 160, 0.6); }
}

/* === SÉPARATEUR DORÉ === */
.gold-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
    margin: 1rem 0;
}
.gold-divider-ornement::before {
    content: '⚜';
    display: block;
    text-align: center;
    color: var(--gold-primary);
    font-size: 1.2rem;
    margin: -0.7rem auto 0;
    background: var(--bg-primary);
    width: 2rem;
}

/* === MESSAGES CHAT === */
.msg-user {
    background: var(--bg-user-msg);
    border-left: 3px solid var(--gold-primary);
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0 0.8rem 20%;
    box-shadow: var(--relief-box);
    font-family: 'EB Garamond', serif;
    color: var(--gold-light);
}
.msg-lea {
    background: var(--bg-lea-msg);
    border-left: 3px solid var(--gold-light);
    border-right: 1px solid var(--gold-dark);
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    margin: 0.8rem 20% 0.8rem 0;
    box-shadow: var(--glow-gold);
    font-family: 'EB Garamond', serif;
    color: var(--text-primary);
    line-height: 1.8;
}
.msg-lea-header {
    font-family: 'Cinzel', serif;
    font-size: 0.85rem;
    color: var(--gold-primary);
    margin-bottom: 0.5rem;
    letter-spacing: 0.1em;
}

/* === SOURCES SIGNATURE === */
.sources-box {
    background: #0D0D0D;
    border: var(--border-thin);
    border-radius: 4px;
    padding: 0.6rem 1rem;
    margin-top: 0.8rem;
    font-family: 'Courier Prime', monospace;
    font-size: 0.78rem;
    color: var(--text-secondary);
    box-shadow: var(--relief-box);
}
.sources-box a { color: var(--gold-dark); text-decoration: none; }
.sources-box a:hover { color: var(--gold-primary); }

/* === SCORE DE CONFIANCE === */
.confidence-bar-container {
    height: 4px;
    background: #2A2A2A;
    border-radius: 2px;
    margin-top: 0.5rem;
    overflow: hidden;
}
.confidence-bar-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, var(--gold-dark), var(--gold-primary));
    transition: width 0.5s ease;
}
.confidence-label {
    font-family: 'Courier Prime', monospace;
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-top: 0.2rem;
}

/* === BOUTONS FEEDBACK === */
.feedback-row {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.8rem;
    align-items: center;
}
.btn-feedback {
    background: transparent;
    border: var(--border-thin);
    color: var(--gold-primary);
    padding: 0.2rem 0.8rem;
    border-radius: 3px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: var(--transition);
}
.btn-feedback:hover {
    background: var(--gold-dark);
    box-shadow: var(--glow-gold);
}

/* === ZONE DE SAISIE === */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #0D0D0D !important;
    border: var(--border-thin) !important;
    color: var(--gold-light) !important;
    font-family: 'EB Garamond', serif !important;
    border-radius: 4px !important;
    box-shadow: var(--relief-box) !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: var(--gold-muted) !important;
    font-style: italic;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    box-shadow: var(--glow-gold) !important;
    border-color: var(--gold-light) !important;
}

/* === BOUTONS STREAMLIT === */
.stButton > button {
    background: linear-gradient(135deg, #1A1200, #2A1E00) !important;
    border: var(--border-thin) !important;
    color: var(--gold-light) !important;
    font-family: 'Cinzel', serif !important;
    letter-spacing: 0.08em !important;
    border-radius: 3px !important;
    transition: var(--transition) !important;
    box-shadow: var(--relief-box) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2A1E00, #3A2A00) !important;
    box-shadow: var(--glow-gold) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* === SPINNER === */
.stSpinner > div { border-top-color: var(--gold-primary) !important; }

/* === SCROLLBAR === */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--gold-dark); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold-primary); }

/* === SÉLECTBOX & MULTISELECT === */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background-color: #0D0D0D !important;
    border: var(--border-thin) !important;
    color: var(--gold-light) !important;
}

/* === PROGRESS BAR === */
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--gold-dark), var(--gold-primary)) !important;
}

/* === EXPANDER === */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: var(--border-thin) !important;
    color: var(--gold-primary) !important;
    font-family: 'Cinzel', serif !important;
}

/* === METRIC CARDS === */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: var(--border-thin) !important;
    border-radius: 4px !important;
    padding: 0.8rem !important;
}
[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; }
[data-testid="stMetricValue"] { color: var(--gold-light) !important; }

/* === CHAT INPUT === */
[data-testid="stChatInput"] textarea {
    background-color: #0D0D0D !important;
    border: var(--border-thin) !important;
    color: var(--gold-light) !important;
    font-family: 'EB Garamond', serif !important;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# Vérification initiale d'Ollama
# ============================================================
def verifier_ollama() -> bool:
    """Vérifie que le service Ollama est en cours d'exécution."""
    try:
        response = requests.get(OLLAMA_BASE_URL, timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        return False


if not verifier_ollama():
    st.error(
        "⚠️ **Ollama n'est pas accessible !**\n\n"
        "LÉA nécessite Ollama pour fonctionner. Suivez ces étapes :\n\n"
        "1. **Installez Ollama** : [ollama.ai](https://ollama.ai)\n"
        "2. **Démarrez le service** : `ollama serve`\n"
        "3. **Téléchargez les modèles** :\n"
        f"   - `ollama pull {LLM_MODEL}`\n"
        "   - `ollama pull nomic-embed-text`\n"
        "4. **Rechargez cette page**\n\n"
        f"*URL attendue : {OLLAMA_BASE_URL}*"
    )
    st.stop()


# ============================================================
# Initialisation de l'agent et de l'état de session
# ============================================================
@st.cache_resource
def initialiser_agent():
    """Initialise l'agent RGPDAgent (singleton via cache Streamlit)."""
    from agent import RGPDAgent
    return RGPDAgent()


try:
    agent = initialiser_agent()
except ConnectionError as e:
    st.error(f"⚠️ Erreur de connexion à Ollama :\n\n{str(e)}")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Erreur lors de l'initialisation de LÉA :\n\n{str(e)}")
    st.stop()

# État de session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "questions_history" not in st.session_state:
    st.session_state.questions_history = []
if "feedback_pending" not in st.session_state:
    st.session_state.feedback_pending = {}


# ============================================================
# Chargement des statistiques
# ============================================================
def charger_stats() -> dict:
    """Charge les statistiques de la base vectorielle."""
    try:
        from indexer import get_stats
        return get_stats()
    except Exception:
        return {"total_chunks": 0, "repartition": {}, "derniere_mise_a_jour": "Non disponible"}


# ============================================================
# HEADER — Titre Art Déco
# ============================================================
st.markdown("""
<div class="lea-header">
    <div class="lea-title">⚖ LÉA</div>
    <div class="lea-subtitle">
        Expert RGPD · ISO 27001 · NIS 2 · Informatique &amp; Libertés
    </div>
    <div class="gold-divider"></div>
    <div class="gold-divider-ornement"></div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR — Panneau de configuration
# ============================================================
with st.sidebar:
    # Logo centré
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <span style="font-size: 3rem; color: #C9A84C;">⚖</span>
        <div style="font-family: 'Cinzel', serif; color: #E8C97A; font-size: 1.4rem;
                    letter-spacing: 0.15em; margin-top: 0.3rem;">LÉA</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # Statistiques de la base
    stats = charger_stats()
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("📚 Documents indexés", stats["total_chunks"])
    with col_s2:
        st.metric("🕐 Dernière MAJ", stats["derniere_mise_a_jour"][:10] if len(stats["derniere_mise_a_jour"]) > 10 else stats["derniere_mise_a_jour"])

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # Bouton de mise à jour de la base de connaissances
    if st.button("🔄 Mettre à jour la base de connaissances", use_container_width=True):
        with st.spinner("Scraping des sources officielles en cours..."):
            try:
                from scraper import scrape_all_sources
                from indexer import update_vectorstore

                progression = st.progress(0, text="Démarrage du scraping...")
                progression.progress(10, text="Scraping des sources CNIL, ANSSI, EUR-Lex...")

                resultats = scrape_all_sources()
                progression.progress(60, text=f"{len(resultats)} pages collectées. Indexation...")

                update_vectorstore()
                progression.progress(100, text="✅ Base mise à jour avec succès !")

                st.success(f"✅ {len(resultats)} pages scrapées et indexées avec succès.")
                time.sleep(2)
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erreur lors de la mise à jour : {str(e)}")

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # Filtre par source
    filtre_options = {
        "Toutes les sources": None,
        "🏛 CNIL — RGPD": "CNIL",
        "🛡 NIS 2 — ANSSI": "NIS2",
        "📋 ISO 27001": "ISO27001",
        "🇪🇺 EUR-Lex": "EUR-LEX",
    }
    filtre_choisi = st.selectbox(
        "🔍 Filtrer par source",
        options=list(filtre_options.keys()),
        index=0,
    )
    categorie_active = filtre_options[filtre_choisi]
    agent.set_category_filter(categorie_active)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # Historique des 10 dernières questions
    st.markdown("**📜 Questions récentes**")
    if st.session_state.questions_history:
        for i, q in enumerate(reversed(st.session_state.questions_history[-10:])):
            q_tronquee = q[:50] + "..." if len(q) > 50 else q
            if st.button(f"💬 {q_tronquee}", key=f"hist_{i}", use_container_width=True):
                st.session_state.question_a_poser = q
                st.rerun()
    else:
        st.markdown("*Aucune question posée pour le moment.*")

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # Section "À propos"
    with st.expander("ℹ️ À propos de LÉA"):
        st.markdown("""
        **LÉA** — *Liberté, Expertise, Assistance*

        Agent IA expert en droit numérique, spécialisé dans le RGPD,
        la directive NIS 2 et la norme ISO 27001.

        🔒 **100% local** — aucune donnée ne quitte votre machine.

        🧠 **Apprentissage adaptatif** — vos retours améliorent
        les réponses de session en session.

        📚 **Sources officielles** — CNIL, ANSSI, EUR-Lex.

        ---

        🔗 **Portfolio** : [tryhackme.com/p/seallia81](https://tryhackme.com/p/seallia81)
        """)

    # Informations sur les corrections
    nb_corrections = agent.get_corrections_count()
    if nb_corrections > 0:
        st.markdown(f"🧠 *{nb_corrections} correction(s) en mémoire*")


# ============================================================
# ZONE DE CHAT PRINCIPALE
# ============================================================
# Affichage de l'historique des messages
for idx, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(
            f'<div class="msg-user">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    elif msg["role"] == "assistant":
        # En-tête LÉA
        st.markdown(
            '<div class="msg-lea-header">⚖ LÉA</div>',
            unsafe_allow_html=True,
        )

        # Corps de la réponse
        st.markdown(
            f'<div class="msg-lea">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )

        # Sources
        if msg.get("sources"):
            sources_html = ""
            for src in msg["sources"][:5]:
                titre = src.get("title", "Source")
                url = src.get("url", "#")
                cat = src.get("article", "")
                if url and url != "#":
                    sources_html += f'📚 <a href="{url}" target="_blank">{titre}</a>'
                else:
                    sources_html += f"📚 {titre}"
                if cat:
                    sources_html += f" | {cat}"
                sources_html += "<br>"

            st.markdown(
                f'<div class="sources-box">{sources_html}</div>',
                unsafe_allow_html=True,
            )

        # Barre de confiance
        confiance = msg.get("confidence", 0)
        pct = int(confiance * 100)
        st.markdown(
            f"""
            <div class="confidence-bar-container">
                <div class="confidence-bar-fill" style="width: {pct}%;"></div>
            </div>
            <div class="confidence-label">Confiance : {pct}%</div>
            """,
            unsafe_allow_html=True,
        )

        # Indicateur de correction
        if msg.get("corrected"):
            st.markdown(
                '<div style="font-size: 0.75rem; color: #6B5020; margin-top: 0.3rem;">'
                '🧠 Réponse enrichie par une correction validée</div>',
                unsafe_allow_html=True,
            )

        # Boutons de feedback
        col_fb1, col_fb2, col_fb3 = st.columns([1, 1, 6])
        with col_fb1:
            if st.button("👍", key=f"fb_pos_{idx}"):
                agent.record_feedback(
                    question=msg.get("question", ""),
                    answer=msg["content"],
                    rating="positive",
                )
                st.toast("✅ Merci ! Réponse validée et mémorisée.", icon="👍")

        with col_fb2:
            if st.button("👎", key=f"fb_neg_{idx}"):
                st.session_state.feedback_pending[idx] = True
                st.rerun()

        # Zone de correction (si feedback négatif)
        if st.session_state.feedback_pending.get(idx, False):
            correction_text = st.text_area(
                "✏️ Proposez la bonne réponse :",
                key=f"correction_{idx}",
                placeholder="Saisissez la réponse correcte ici...",
                height=100,
            )
            col_val, col_ann = st.columns(2)
            with col_val:
                if st.button("✅ Valider la correction", key=f"valider_{idx}"):
                    if correction_text:
                        agent.record_feedback(
                            question=msg.get("question", ""),
                            answer=msg["content"],
                            rating="negative",
                            correction=correction_text,
                        )
                        st.session_state.feedback_pending[idx] = False
                        st.toast("✅ Correction enregistrée ! LÉA s'améliorera.", icon="🧠")
                        st.rerun()
                    else:
                        st.warning("Veuillez saisir une correction avant de valider.")
            with col_ann:
                if st.button("❌ Annuler", key=f"annuler_{idx}"):
                    st.session_state.feedback_pending[idx] = False
                    st.rerun()

        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)


# ============================================================
# ZONE DE SAISIE — Persistante en bas
# ============================================================
# Vérifier si une question vient de l'historique
question_preset = st.session_state.pop("question_a_poser", "")

with st.container():
    col1, col2 = st.columns([6, 1])
    with col1:
        question = st.text_input(
            "",
            value=question_preset,
            placeholder="Posez votre question sur le RGPD, ISO 27001 ou NIS 2...",
            key="input_question",
            label_visibility="collapsed",
        )
    with col2:
        envoyer = st.button("Envoyer ⚖", use_container_width=True)

    # Traitement de la question
    if envoyer and question:
        # Ajout du message utilisateur
        st.session_state.messages.append({"role": "user", "content": question})

        # Ajout à l'historique des questions
        if question not in st.session_state.questions_history:
            st.session_state.questions_history.append(question)

        # Appel à l'agent
        with st.spinner("⚖ LÉA analyse votre question..."):
            try:
                reponse = agent.ask(question)

                # Ajout de la réponse dans l'état de session
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reponse["answer"],
                    "sources": reponse.get("sources", []),
                    "confidence": reponse.get("confidence", 0),
                    "corrected": reponse.get("corrected", False),
                    "question": question,
                    "timestamp": reponse.get("timestamp", ""),
                })

            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ Une erreur est survenue : {str(e)}",
                    "sources": [],
                    "confidence": 0,
                    "corrected": False,
                    "question": question,
                })

        st.rerun()

    # Bouton effacer
    col3, col4 = st.columns([1, 5])
    with col3:
        if st.button("🗑 Effacer", use_container_width=True):
            st.session_state.messages = []
            st.session_state.questions_history = []
            st.session_state.feedback_pending = {}
            agent.clear_history()
            st.rerun()
