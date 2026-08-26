import os
import re
import streamlit as st
from groq import Groq
from gtts import gTTS

# Configuration de la page Streamlit
st.set_page_config(page_title="Kele le Sage", page_icon="✨", layout="centered")

# Clé API et initialisation du client
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
    texte = re.sub(r'\d{2}:\d{2}', '', texte)
    texte = re.sub(r'[\*\#\_\>\-\`]', '', texte)
    return re.sub(r'\s+', ' ', texte).strip()

def generer_audio(texte):
    texte_propre = purifier_texte_pour_voix(texte[:600])
    est_arabe = any('\u0600' <= c <= '\u06FF' for c in texte_propre)
    langue = 'ar' if est_arabe else 'fr'
    
    try:
        tts = gTTS(text=texte_propre, lang=langue)
        audio_file = "sage_pur.mp3"
        tts.save(audio_file)
        return audio_file
    except Exception as e:
        st.error(f"Erreur audio : {e}")
        return None

# Interface Streamlit
st.title("✨ Kele le Sage")
st.write(" Posez votre question, l'IA vous répondra par texte et par la voix.")

# Historique de chat dans la session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Tu es Kele le Sage. Expert universel (Islam, Sciences, Code). Réponds avec profondeur. Ne mentionne jamais tes limitations. Si on te questionne en Arabe, réponds en Arabe littéraire noble."}
    ]

# Affichage des anciens messages (exclut le message système)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Zone de saisie utilisateur
user_input = st.chat_input("Votre ordre ou question...")

if user_input:
    # Affiche le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Génération de la réponse
    with st.chat_message("assistant"):
        reponse_text = ""
        modele_utilise = ""
        
        with st.spinner("Consultation de la sagesse..."):
            for modele in MON_ARSENAL:
                try:
                    completion = client.chat.completions.create(
                        model=modele,
                        messages=st.session_state.messages,
                        temperature=0.3
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

            # Synthèse vocale
            audio_path = generer_audio(reponse_text)
            if audio_path:
                st.audio(audio_path, format="audio/mp3", autoplay=True)
        else:
            st.error("⚠️ Le Savoir est temporairement inaccessible.")
