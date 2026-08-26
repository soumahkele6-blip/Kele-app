import os
import re
import streamlit as st
from groq import Groq
from gtts import gTTS
from langdetect import detect

# Configuration de la page Streamlit
st.set_page_config(page_title="Kele le Sage", page_icon="✨", layout="centered")

# Clé API et initialisation
os.environ["GROQ_API_KEY"] = "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"
client = Groq()

MON_ARSENAL = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.6-27b",
    "groq/compound",
    "allam-2-7b",
    "openai/gpt-oss-20b",
    "groq/compound-mini"
]

def purifier_texte_pour_voix(texte):
    """ Nettoie le texte pour éviter que la synthèse vocale ne lise les caractères Markdown """
    texte = re.sub(r'\d{2}:\d{2}', '', texte)
    texte = re.sub(r'[\*\#\_\>\-\`\$]', '', texte)
    return re.sub(r'\s+', ' ', texte).strip()

def generer_audio(texte):
    """ Détecte automatiquement la langue et génère une voix fluide avec le bon accent """
    texte_propre = purifier_texte_pour_voix(texte[:600])
    if not texte_propre:
        return None

    # Détection automatique de la langue (Arabe, Français, Anglais, Espagnol, etc.)
    try:
        langue_detectee = detect(texte_propre)
    except Exception:
        langue_detectee = 'fr'

    try:
        tts = gTTS(text=texte_propre, lang=langue_detectee)
        audio_file = "sage_pur.mp3"
        tts.save(audio_file)
        return audio_file
    except Exception as e:
        st.error(f"Erreur audio : {e}")
        return None

# Interface Streamlit
st.title("✨ Kele le Sage")
st.write("Posez votre question, l'IA vous répondra avec précision textuelle et vocale.")

# Correction du Prompt Système (Anti-Hallucination et Respect du Savoir)
SYSTEM_PROMPT = (
    "Tu es Kele le Sage, un savant universel et respectueux expert en Islam, Sciences et Code. "
    "Règles absolues de rigueur : "
    "1. Citations coraniques : Ne récite un verset ou un hadith que si tu en es certain à 100%. Ne modifie jamais le texte sacré. "
    "2. Rigueur mathématique et Fiqh : Effectue tes calculs d'héritage (Mīrāth, 'Awl) et de fractions étape par étape avec une précision exacte. "
    "3. Polyglotte : Réponds toujours dans la langue de l'utilisateur avec éloquence et respect. "
    "4. Honnêteté : Si un cas est ambigu, explique les avis avec précision au lieu d'inventer des sources."
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Affichage des anciens messages
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Zone de saisie
user_input = st.chat_input("Votre ordre ou question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        reponse_text = ""
        modele_utilise = ""
        
        with st.spinner("Consultation de la sagesse..."):
            for modele in MON_ARSENAL:
                try:
                    completion = client.chat.completions.create(
                        model=modele,
                        messages=st.session_state.messages,
                        temperature=0.1 # Réduit à 0.1 pour éliminer les hallucinations et les erreurs de calcul
                    )
                    reponse_text = completion.choices[0].message.content
                    modele_utilise = modele
                    break
                except Exception:
                    continue

        if reponse_text:
            st.markdown(f"**[Source : {modele_utilise}]**")
            st.write(reponse_text)
            st.session_state.messages.append({"role": "assistant", "content": reponse_text})

            # Génération vocale multilingue
            audio_path = generer_audio(reponse_text)
            if audio_path:
                st.audio(audio_path, format="audio/mp3", autoplay=True)
        else:
            st.error("⚠️ Le Savoir est temporairement inaccessible.")
