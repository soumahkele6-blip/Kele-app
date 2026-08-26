import os
import streamlit as st
from groq import Groq
from pypdf import PdfReader
import speech_recognition as sr

# --- CONFIGURATION PAGE STREAMLIT ---
st.set_page_config(page_title="KELE - Géant IA", page_icon="🤖", layout="wide")

st.title("🤖 KELE — Le Géant d'Intelligence")
st.caption("Sciences religieuses, Tajwid Coran, Enseignement global, Codage & Analyse Multimodale")

# --- CLE API GROQ (Stockée dans Streamlit Secrets ou saisie utilisateur) ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

# --- INITIALISATION DE L'HISTORIQUE & MÉMOIRE DE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- BOUTON NOUVEAU CHAT ---
with st.sidebar:
    st.header("⚙️ Options KELE")
    if st.button("🔄 Démarrer un nouveau chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Fonctionnalités incluses :**")
    st.markdown("- 📋 Copie en un clic\n- 📎 Analyse PDF / Audio / Image\n- 📖 Récitation & Correction Coran\n- 💻 Master Codage & Jeux")

# --- LECTURE FICHIERS MULTIMODAUX ---
def process_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return ""
    
    file_type = uploaded_file.name.split(".")[-1].lower()
    
    if file_type == "pdf":
        try:
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return f"\n[CONTENU PDF INCLUS]:\n{text[:4000]}"
        except Exception as e:
            return f"\n[Erreur PDF: {e}]"
            
    elif file_type in ["wav", "mp3", "m4a", "ogg"]:
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(uploaded_file) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data, language="ar-SA")
                except:
                    text = recognizer.recognize_google(audio_data, language="fr-FR")
                return f"\n[TRANSCRIPTION AUDIO DÉTECTÉE]: {text}"
        except Exception as e:
            return f"\n[Fichier Audio transmis : {uploaded_file.name}]"
            
    return f"\n[FICHIER JOINT]: {uploaded_file.name}"

# --- MOTEUR DE PENSÉE DE KELE ---
KELE_SYSTEM_PROMPT = """
Tu es KELE, un Maître Omniscient, Enseignant Supérieur et Expert Stratège.
- CORAN & TAJWID : Analyse rigoureuse des récitations audio, détection des fautes, Fiqh, Tafsir.
- ENSEIGNEMENT : Mode Maître-Élève pour tester la mémorisation et enseigner toutes les sciences.
- CODE & JEUX : Grand maître algorithmique, théorie des jeux.
- TON : Structuré, souverain, pédagogique et précis.
"""

# --- AFFICHAGE DES MESSAGES EXISTANTS ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- Saisie Utilisateur & Upload de fichier ---
file_input = st.file_uploader("📎 Ajouter un fichier (PDF, Audio, Image)", type=["pdf", "mp3", "wav", "m4a", "png", "jpg"])
user_prompt = st.chat_input("Posez votre question ou récitez votre verset à KELE...")

if user_prompt:
    # 1. Traitement du fichier joint s'il existe
    file_context = process_uploaded_file(file_input)
    full_user_query = f"{user_prompt} {file_context}".strip()

    # 2. Afficher le message utilisateur
    st.session_state.messages.append({"role": "user", "content": full_user_query})
    with st.chat_message("user"):
        st.write(full_user_query)

    # 3. Génération de la réponse avec l'architecture KELE (DeepSeek R1 + LLaMA 3.3)
    with st.chat_message("assistant"):
        with st.spinner("🧠 KELE analyse et formule son raisonnement..."):
            # Raisonnement interne (DeepSeek)
            thought_res = client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[
                    {"role": "system", "content": "Analyse logique et détection des erreurs / points clés."},
                    {"role": "user", "content": full_user_query}
                ],
                temperature=0.2
            )
            thought_process = thought_res.choices[0].message.content

            # Assemblage du contexte de conversation
            payload = [{"role": "system", "content": KELE_SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                payload.append({"role": m["role"], "content": m["content"]})
            payload.append({"role": "assistant", "content": f"[Analyse interne] {thought_process}"})

            # Réponse souveraine (LLaMA 3.3)
            final_res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=payload,
                temperature=0.4
            )
            response_text = final_res.choices[0].message.content
            
            st.write(response_text)
            
            # Stockage dans l'historique
            st.session_state.messages.append({"role": "assistant", "content": response_text})
