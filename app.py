import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. DESIGN ---
st.set_page_config(page_title="Sektor 4 Vision", page_icon="📷", layout="centered")

st.markdown("""
<style>
    .stApp {background-color: #050505; color: #00ff41;}
    h1, h2, h3, p, div {font-family: 'Courier New', monospace; color: #00ff41;}
    .stButton>button { width: 100%; background-color: #111; color: #00ff41; border: 1px solid #00ff41; }
    .stButton>button:hover { background-color: #00ff41; color: #000; border: 1px solid #00ff41; }
</style>
""", unsafe_allow_html=True)

st.title("Sektor 4: Vision Terminal 🦾")

# --- 2. API SETUP ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 3. BILD-MODELL-SUCHE (STABILER FALLBACK) ---
if "image_model_name" not in st.session_state:
    try:
        all_models = genai.list_models()
        # Suche erst nach Imagen 3 (stabilste Version), dann nach anderen
        img_models = [m.name for m in all_models if 'imagen-3' in m.name.lower()]
        if not img_models:
            img_models = [m.name for m in all_models if 'imagen' in m.name.lower()]
        
        st.session_state.image_model_name = img_models[0] if img_models else "models/imagen-3.0-generate-001"
    except:
        st.session_state.image_model_name = "models/imagen-3.0-generate-001"

st.write(f"/// VISUAL-LINK: [{st.session_state.image_model_name}] ///")

# --- 4. ENGINE INITIALISIERUNG ---
if "matrix_session" not in st.session_state:
    text_model = genai.GenerativeModel("gemini-1.5-flash") # Bleib beim stabilen Flash
    st.session_state.matrix_session = text_model.start_chat(history=[])
    st.session_state.last_image = None

# --- 5. BILD-GENERATOR (ABGESICHERT) ---
def fetch_vision(text_response):
    if "📷 Kamera-Feed:" in text_response:
        try:
            start = text_response.find("📷 Kamera-Feed:") + len("📷 Kamera-Feed:")
            end = text_response.find("\n", start)
            scene = text_response[start:end].strip() if end != -1 else text_response[start:].strip()
            
            prompt = f"Dark cyberpunk, cinematic neon, rainy Berlin, grit: {scene}"
            
            # Hier nutzen wir das Modell
            model = genai.ImageGenerationModel(st.session_state.image_model_name)
            result = model.generate_images(prompt=prompt, number_of_images=1)
            return result.images[0].pil_image
        except Exception as e:
            # Fehler wird nur in die Sidebar geschrieben, App läuft weiter!
            st.sidebar.warning(f"Kamera offline: {str(e)}")
            return None
    return None

def process_step(input_text):
    with st.spinner("Synchronisiere mit Matrix..."):
        try:
            response = st.session_state.matrix_session.send_message(input_text)
            # Bild im Hintergrund versuchen
            st.session_state.last_image = fetch_vision(response.text)
        except Exception as e:
            st.error(f"MATRIX-CRASH: {str(e)}")

# --- 6. UI ---
# Das Bild wird nur angezeigt, wenn es wirklich geladen wurde
if st.session_state.last_image:
    st.image(st.session_state.last_image, use_column_width=True)

# Chat-Verlauf (umgedreht, damit das Neueste oben ist, ist auf dem Handy oft besser)
for message in reversed(st.session_state.matrix_session.history):
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Steuerung (Ganz oben fixiert durch Streamlit-Logik)
st.write("---")
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
    
