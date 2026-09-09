from datetime import datetime
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from duckduckgo_search import DDGS
from groq import Groq
import streamlit as st

# 1. Configuration de la page
st.set_page_config(
    page_title="IA Groq 120B + Recherche Web",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("IA Groq 120B + Web 🌐")

# 2. Volet latéral pour la clé API et l'historique
with st.sidebar:
    st.header("⚙️ Configuration")
    groq_api_key = st.text_input(
        "Clé API Groq (gsk_...)",
        type="password",
        placeholder="gsk_...",
        help="Votre clé Groq gratuite.",
    )

    if st.button("🗑️ Nouvelle discussion", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Modèle actif : **openai/gpt-oss-120b**")
    st.caption("Moteur de recherche : **Google News + DuckDuckGo**")

# 3. Initialisation de l'historique de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Affichage des messages précédents
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# 5. Moteur de recherche web hybride (Google Actu + DuckDuckGo)
def recherche_web(query):
    snippets = []

    # Source 1 : Google Actualités (imbattable pour le sport et les scores récents)
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=fr&gl=FR&ceid=FR:fr"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            root = ET.fromstring(resp.read())
            items = root.findall(".//item")[:4]
            for it in items:
                title = it.find("title").text if it.find("title") is not None else ""
                pub_date = (
                    it.find("pubDate").text
                    if it.find("pubDate") is not None
                    else ""
                )
                if title:
                    snippets.append(
                        f"• [Actualité récente ({pub_date})] : {title}"
                    )
    except Exception:
        pass

    # Source 2 : DuckDuckGo (recherche web générale)
    if len(snippets) < 2:
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=3):
                    snippets.append(f"• [Web] {r.get('title')} : {r.get('body')}")
        except Exception:
            pass

    return "\n".join(snippets) if snippets else ""


# 6. Saisie utilisateur
if prompt := st.chat_input("Posez une question, demandez un score ou du code..."):
    if not groq_api_key:
        st.error("⚠️ Veuillez entrer votre clé API Groq dans le menu à gauche (icône >).")
        st.stop()

    # Ajout du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Détection automatique de besoin de recherche web
    mots_cles = [
        "hier",
        "aujourd'hui",
        "ce soir",
        "demain",
        "score",
        "match",
        "résultat",
        "classement",
        "gagné",
        "qui a",
        "actu",
        "actualité",
        "prix",
        "météo",
        "direct",
        "championnat",
    ]
    besoin_web = any(m in prompt.lower() for m in mots_cles)

    web_data = ""
    with st.chat_message("assistant"):
        # Étape 1 : Recherche si nécessaire
        if besoin_web:
            with st.status("Recherche sur Internet en direct...", expanded=False) as status:
                web_data = recherche_web(prompt)
                if web_data:
                    status.update(
                        label="✓ Données du web trouvées !",
                        state="complete",
                        expanded=False,
                    )
                else:
                    status.update(
                        label="Aucune info web récente trouvée",
                        state="complete",
                        expanded=False,
                    )

        # Date actuelle pour situer l'IA
        today = datetime.now().strftime("%A %d %B %Y")

        system_prompt = f"""Tu es un assistant IA chaleureux, concis, direct et humain.
DATE DU JOUR : {today}.
RÈGLES STRICTES :
1. N'utilise JAMAIS de tableaux bruts avec des barres '|'. Rédige avec des phrases fluides et des listes à puces aérées.
2. Si des informations du web sont fournies ci-dessous, donne les scores ou faits précis dès la première phrase.
{f'DONNÉES TROUVÉES EN DIRECT SUR LE WEB :\n{web_data}' if web_data else ''}"""

        # Préparation du fil de discussion
        api_messages = [{"role": "system", "content": system_prompt}]
        for m in st.session_state.messages:
            api_messages.append({"role": m["role"], "content": m["content"]})

        # Étape 2 : Rédaction et affichage mot par mot (Streaming)
        client = Groq(api_key=groq_api_key)

        def stream_generator():
            try:
                stream = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=api_messages,
                    temperature=0.5,
                    stream=True,
                )
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
            except Exception as e:
                yield f"Erreur Groq : {str(e)}"

        # Affichage direct à l'écran
        full_response = st.write_stream(stream_generator())

    # Sauvegarde dans la session
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
                    )
