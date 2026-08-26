import os
import re
import streamlit as st
from groq import Groq
from gtts import gTTS
from langdetect import detect

st.set_page_config(page_title="Kele le Sage", page_icon="✨", layout="centered")

# Clé API (Assurez-vous qu'elle est active sur https://console.groq.com)
os.environ["GROQ_API_KEY"] = "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"
client = Groq()

# MODÈLES OFFICIELS GROQ (Mise à jour)
MON_ARSENAL = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
]

def purifier_texte_pour_voix(texte):
    texte = re.sub(r'\d{2}:\d{2}', '', texte)
    texte = re.sub(r'[\*\#\_\>\-\`\$]', '', texte)
    return re.sub(r'\s+', ' ', texte).strip()

def generer_audio(texte):
    texte_propre = purifier_texte_pour_voix(texte[:600])
    if not texte_propre:
        return None

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

st.title("✨ Kele le Sage")
st.write("Posez votre question, l'IA vous répondra par texte et par la voix.")

SYSTEM_PROMPT = (
    "Tu es Kele le Sage, un savant universel et respectueux expert en Islam, Sciences et Code. "
    "Règles absolues : "
    "1. Citations coraniques : Ne récite un verset ou un hadith que si tu en es certain à 100%. "
    "2. Rigueur mathématique et Fiqh : Effectue tes calculs d'héritage étape par étape avec précision. "
    "3. Polyglotte : Réponds toujours dans la langue de l'utilisateur. "
    "4. Honnêteté : Si un cas est ambigu, explique les avis au lieu d'inventer."
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

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
                        temperature=0.1
                    )
                    reponse_text = completion.choices[0].message.content
                    modele_utilise = modele
                    break
                except Exception as e:
                    # Affiche l'erreur en mode débogage si tous échouent
                    dernier_erreur = str(e)
                    continue

        if reponse_text:
            st.markdown(f"**[Source : {modele_utilise}]**")
            st.write(reponse_text)
            st.session_state.messages.append({"role": "assistant", "content": reponse_text})

            audio_path = generer_audio(reponse_text)
            if audio_path:
                st.audio(audio_path, format="audio/mp3", autoplay=True)
        else:
            st.error(f"⚠️ Le Savoir est temporairement inaccessible. Dépannage : {dernier_erreur}")
