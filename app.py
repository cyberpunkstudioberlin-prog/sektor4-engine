import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. CYBERPUNK DESIGN ---
st.set_page_config(page_title="Sektor 4 Vision", page_icon="📷", layout="centered")

st.markdown("""
<style>
    .stApp {background-color: #050505; color: #00ff41;}
    h1, h2, h3, p, div {font-family: 'Courier New', monospace; color: #00ff41;}
    .stButton>button { width: 100%; background-color: #111; color: #00ff41; border: 1px solid #00ff41; }
    .stButton>button:hover { background-color: #00ff41; color: #000; }
</style>
""", unsafe_allow_html=True)

st.title("Sektor 4: Vision Terminal 🦾")

# --- 2. API & MODELL-SUCHE ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

if "image_model_name" not in st.session_state:
    try:
        # Wir suchen gezielt nach IMAGEN Modellen
        all_models = genai.list_models()
        img_models = [m.name for m in all_models if 'imagen' in m.name.lower()]
        
        if img_models:
            # Wir nehmen das neueste Imagen
            st.session_state.image_model_name = img_models[0]
        else:
            # Fallback auf einen Standardnamen von 2026
            st.session_state.image_model_name = "models/imagen-3.0-generate-001"
    except:
        st.session_state.image_model_name = "models/imagen-3.0-generate-001"

st.write(f"/// VISUAL-LINK: [{st.session_state.image_model_name}] AKTIV ///")

# --- 3. ENGINE SETUP ---
if "matrix_session" not in st.session_state:
    text_model = genai.GenerativeModel("gemini-1.5-flash")
    st.session_state.matrix_session = text_model.start_chat(history=[])
    st.session_state.last_image = None

# --- 4. BILD-GENERATOR (ROBUST) ---
def fetch_vision(text_response):
    if "📷 Kamera-Feed:" in text_response:
        try:
            # Extrahiere Beschreibung
            start = text_response.find("📷 Kamera-Feed:") + len("📷 Kamera-Feed:")
            end = text_response.find("\n", start)
            if end == -1: end = len(text_response)
            scene = text_response[start:end].strip()
            
            # Prompt-Veredelung
            full_prompt = f"Gritty cyberpunk, cinematic neon lighting, high contrast, Sektor 4 Berlin aesthetic, photorealistic: {scene}"
            
            # Bild generieren
            model = genai.ImageGenerationModel(st.session_state.image_model_name)
            result = model.generate_images(prompt=full_prompt, number_of_images=1)
            return result.images[0].pil_image
        except Exception as e:
            # Wenn Bild scheitert, Spiel nicht crashen!
            st.sidebar.error(f"Bild-Fehler: {str(e)}")
            return None
    return None

def process_step(input_text):
    with st.spinner("Matrix lädt Daten..."):
        response = st.session_state.matrix_session.send_message(input_text)
        st.session_state.last_image = fetch_vision(response.text)

# --- 5. UI ---
if st.session_state.last_image:
    st.image(st.session_state.last_image, use_column_width=True)

for message in st.session_state.matrix_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Steuerung
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("A"): process_step("A"); st.rerun()
with col2:
    if st.button("B"): process_step("B"); st.rerun()
with col3:
    if st.button("C"): process_step("C"); st.rerun()

user_input = st.chat_input("Befehl...")
if user_input:
    process_step(user_input)
    st.rerun()
    
