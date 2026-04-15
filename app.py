import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. DESIGN ---
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

# --- 2. API SETUP ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 3. AUTO-BILD-MODELL-SUCHE ---
if "image_model_name" not in st.session_state:
    try:
        # Wir suchen nach Modellen, die 'image' im Namen haben
        img_models = [m.name for m in genai.list_models() if 'generateimages' in m.supported_generation_methods or 'image' in m.name.lower()]
        # Wir nehmen das neueste Imagen (meistens das erste in der Liste)
        st.session_state.image_model_name = img_models[0] if img_models else "models/imagen-3.0-generate-001"
    except:
        st.session_state.image_model_name = "models/imagen-3.0-generate-001"

st.write(f"/// VISUAL-LINK: [{st.session_state.image_model_name}] ///")

# --- 4. ENGINE INITIALISIERUNG ---
if "matrix_session" not in st.session_state:
    text_model = genai.GenerativeModel("gemini-1.5-flash")
    st.session_state.matrix_session = text_model.start_chat(history=[])
    st.session_state.last_image = None
    st.session_state.last_text = ""

# --- 5. BILD-GENERATOR FUNKTION ---
def fetch_vision(text_response):
    if "📷 Kamera-Feed:" in text_response:
        start = text_response.find("📷 Kamera-Feed:") + len("📷 Kamera-Feed:")
        end = text_response.find("\n", start)
        scene = text_response[start:end].strip()
        
        # Cyberpunk-Stil-Vorgabe
        full_prompt = f"Cinematic cyberpunk style, neon lights, rainy Berlin street, gritty texture, highly detailed: {scene}"
        
        try:
            # Wichtig: In 2026 nutzen wir das gefundene Modell direkt
            img_gen = genai.ImageGenerationModel(st.session_state.image_model_name)
            result = img_gen.generate_images(prompt=full_prompt, number_of_images=1)
            return result.images[0].pil_image
        except Exception as e:
            st.warning(f"BILD-LINK UNTERBROCHEN: {str(e)}")
            return None
    return None

def process_step(input_text):
    with st.spinner("Matrix berechnet Visualisierung..."):
        response = st.session_state.matrix_session.send_message(input_text)
        st.session_state.last_text = response.text
        st.session_state.last_image = fetch_vision(response.text)

# --- 6. UI ---
if st.session_state.last_image:
    st.image(st.session_state.last_image, use_column_width=True)

for message in st.session_state.matrix_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Steuerung
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Option A"): process_step("A"); st.rerun()
with col2:
    if st.button("Option B"): process_step("B"); st.rerun()
with col3:
    if st.button("Option C"): process_step("C"); st.rerun()

user_input = st.chat_input("Befehl...")
if user_input:
    process_step(user_input)
    st.rerun()
    
