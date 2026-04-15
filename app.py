import streamlit as st
import google.generativeai as genai
import io

# --- 1. CYBERPUNK TERMINAL DESIGN ---
st.set_page_config(page_title="Sektor 4 Vision", page_icon="📷", layout="centered")

st.markdown("""
<style>
    .stApp {background-color: #050505; color: #00ff41;}
    h1, h2, h3, p, div {font-family: 'Courier New', monospace; color: #00ff41;}
    .stButton>button {
        width: 100%; background-color: #111; color: #00ff41; border: 1px solid #00ff41;
    }
    .stButton>button:hover { background-color: #00ff41; color: #000; }
</style>
""", unsafe_allow_html=True)

st.title("Sektor 4: Vision Terminal 🦾")

# --- 2. API & MODELL SETUP ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

if "matrix_session" not in st.session_state:
    # Initialisierung der beiden Gehirne: Text (Gemini) und Bild (Imagen)
    text_model = genai.GenerativeModel("gemini-1.5-flash")
    # Wir laden Imagen für die Visualisierungen
    try:
        st.session_state.image_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
    except:
        st.session_state.image_model = None
    
    system_prompt = "[Sektor 4 Engine V45] Erzeuge IMMER einen '📷 Kamera-Feed: [Beschreibung]' am Anfang."
    st.session_state.matrix_session = text_model.start_chat(history=[])
    st.session_state.last_image = None

# --- 3. BILD-GENERATOR FUNKTION ---
def fetch_vision(text_response):
    if "📷 Kamera-Feed:" in text_response and st.session_state.image_model:
        # Extrahiere die Beschreibung für Imagen
        start = text_response.find("📷 Kamera-Feed:") + len("📷 Kamera-Feed:")
        end = text_response.find("\n", start)
        scene_description = text_response[start:end].strip()
        
        # Cyberpunk-Stil erzwingen
        style_prompt = f"Cyberpunk aesthetic, cinematic lighting, neon grime, Sektor 4 Berlin style: {scene_description}"
        
        try:
            result = st.session_state.image_model.generate_images(prompt=style_prompt, number_of_images=1)
            return result.images[0]
        except:
            return None
    return None

# --- 4. ENGINE LOGIK ---
def process_step(input_text):
    with st.spinner("Verbindung zur Matrix..."):
        response = st.session_state.matrix_session.send_message(input_text)
        st.session_state.last_text = response.text
        # Bild generieren basierend auf dem neuen Text
        st.session_state.last_image = fetch_vision(response.text)

# --- 5. INTERFACE ---
# Letztes generiertes Bild ganz oben anzeigen
if st.session_state.last_image:
    st.image(st.session_state.last_image.pil_image, use_column_width=True)

# Chat-Verlauf
for message in st.session_state.matrix_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Steuerung
user_input = st.chat_input("Befehl eingeben...")
if user_input:
    process_step(user_input)
    st.rerun()

# Buttons für A, B, C (wie gehabt)
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("A"):
        process_step("A")
        st.rerun()
# ... (B und C analog)
