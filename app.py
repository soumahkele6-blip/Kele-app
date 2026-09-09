from datetime import datetime, timedelta
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from duckduckgo_search import DDGS
from groq import Groq
import streamlit as st

st.set_page_config(
    page_title="IA Groq 120B + Recherche Web",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("IA Groq 120B + Web 🌐")

# Détection automatique du secret Streamlit ou saisie manuelle
groq_api_key = st.secrets.get("GROQ_API_KEY")

with st.sidebar:
    st.header("⚙️ Configuration")
    if not groq_api_key:
        groq_api_key = st.text_input(
            "Clé API Groq (gsk_...)", type="password", placeholder="gsk_..."
        )
    else:
        st.success("✓ Clé connectée automatiquement !")

    if st.button("🗑️ Nouvelle discussion", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# Fonction de nettoyage HTML
def clean_html(raw_html):
    cleanr = re.compile("<.*?>")
    return re.sub(cleanr, "", raw_html)


# Recherche optimisée avec conversion intelligente des dates
def recherche_web_intelligente(query):
    snippets = []

    # 1. Remplacement intelligent de "hier" et "aujourd'hui" par les vraies dates
    now = datetime.now()
    hier = now - timedelta(days=1)

    query_search = query.lower()
    query_search = query_search.replace("hier", hier.strftime("%d %B %Y"))
    query_search = query_search.replace(
        "aujourd'hui", now.strftime("%d %B %Y")
    )
    query_search = query_search.replace("ce soir", now.strftime("%d %B %Y"))

    # 2. Recherche sur Google Actualités (avec titre + résumé)
    try:
        encoded = urllib.parse.quote(query_search)
        url = f"https://news.google.com/rss/search?q={encoded}&hl=fr&gl=FR&ceid=FR:fr"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            root = ET.fromstring(resp.read())
            items = root.findall(".//item")[:5]
            for it in items:
                title = it.find("title").text if it.find("title") is not None else ""
                desc = it.find("description").text if it.find("description") is not None else ""
                clean_desc = clean_html(desc)
                if title:
                    snippets.append(f"• Titre : {title}\n  Détails : {clean_desc}")
    except Exception:
        pass

    # 3. Fallback DuckDuckGo si besoin
    if len(snippets) < 2:
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query_search, max_results=4):
                    snippets.append(f"• {r.get('title')} : {r.get('body')}")
        except Exception:
            pass

    return "\n\n".join(snippets) if snippets else ""


if prompt := st.chat_input("Posez une question, demandez un score ou du code..."):
    if not groq_api_key:
        st.error("⚠️ Veuillez entrer votre clé API Groq dans le menu à gauche (icône >).")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

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
        if besoin_web:
            with st.status("Recherche des résultats en direct...", expanded=False) as status:
                web_data = recherche_web_intelligente(prompt)
                status.update(
                    label="✓ Données du web trouvées !",
                    state="complete",
                    expanded=False,
                )

        now = datetime.now()
        date_hier = (now - timedelta(days=1)).strftime("%A %d %B %Y")
        date_jour = now.strftime("%A %d %B %Y")

        system_prompt = f"""Tu es un assistant IA direct, clair et concis.
DATE DU JOUR : {date_jour}.
DATE D'HIER : {date_hier}.
RÈGLE ABSOLUE :
Tu as reçu ci-dessous des résultats de recherche issus d'Internet en direct. Tu DOIS les utiliser pour donner les scores exacts et les résultats demandés dès la première phrase, sans jamais renvoyer l'utilisateur vers des sites externes et sans t'excuser.

RÉSULTATS DU WEB EN DIRECT :
\"\"\"
{web_data}
\"\"\""""

        api_messages = [{"role": "system", "content": system_prompt}]
        for m in st.session_state.messages:
            api_messages.append({"role": m["role"], "content": m["content"]})

        client = Groq(api_key=groq_api_key)

        def stream_generator():
            try:
                stream = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=api_messages,
                    temperature=0.3,
                    stream=True,
                )
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
            except Exception as e:
                yield f"Erreur Groq : {str(e)}"

        full_response = st.write_stream(stream_generator())

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )
