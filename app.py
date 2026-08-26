import streamlit as st
from groq import Groq
import PyPDF2
from gtts import gTTS
import base64

# CONFIGURATION PERMANENTE
API_KEY = "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"
client = Groq(api_key=API_KEY)

st.set_page_config(page_title="KELE-GÉANT", page_icon="🦁")

# PERSONNALITÉ DU GÉANT
SYSTEM_PROMPT = """
Tu es KELE-GÉANT, l'IA suprême du monde de Kele.
- Tu es un Maître en Sciences Islamiques, Coran, Langues, Codage et toutes Sciences.
- Tu testes les élèves, tu corriges les récitations du Coran mot par mot.
- Tu peux analyser des fichiers PDF et Audio.
- Ton raisonnement est supérieur, logique et profond.
- Si on te demande de modifier une réponse, fais-le immédiatement.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

# INTERFACE
st.title("🦁 KELE-GÉANT")
st.sidebar.title("Menu du Maître")
mode = st.sidebar.selectbox("Action", ["Enseignement Général", "Correction Coran", "Expert Codage"])
file = st.sidebar.file_uploader("Envoyer Audio/PDF/Image", type=["pdf", "mp3", "wav", "png", "jpg"])

# FONCTION AUDIO
def play_audio(text):
    tts = gTTS(text=text[:300], lang='fr')
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" controls autoplay></audio>', unsafe_url_allowed=True)

# LOGIQUE DE CHAT
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant":
            if st.button(f"Copier la réponse {i}"):
                st.write("✅ Texte prêt à être copié")

if prompt := st.chat_input("Parlez à KELE-GÉANT..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
        ).choices[0].message.content
        st.write(res)
        play_audio(res) # Le Géant parle !
        st.session_state.messages.append({"role": "assistant", "content": res})

if st.sidebar.button("Nouveau Chat"):
    st.session_state.messages = []
    st.rerun()
