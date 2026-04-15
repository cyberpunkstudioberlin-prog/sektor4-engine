import streamlit as st
import google.generativeai as genai

# --- 1. DESIGN & TERMINAL LOOK ---
st.set_page_config(page_title="Sektor 4 Vision", page_icon="🦾", layout="centered")

st.markdown("""
<style>
    .stApp {background-color: #050505; color: #00ff41;}
    h1, h2, h3, p, div {font-family: 'Courier New', monospace; color: #00ff41;}
    .stButton>button { width: 100%; background-color: #111; color: #00ff41; border: 1px solid #00ff41; }
    .stButton>button:hover { background-color: #00ff41; color: #000; }
</style>
""", unsafe_allow_html=True)

st.title("Sektor 4: Final Terminal 🦾")

# --- 2. API SETUP ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 3. SESSION INITIALISIERUNG (ANTI-HANG FIX) ---
if "matrix_session" not in st.session_state:
    # Wir nehmen das absolut stabilste Modell von 2026
    text_model = genai.GenerativeModel("gemini-1.5-flash")
    st.session_state.matrix_session = text_model.start_chat(history=[])
    st.session_state.last_image = None
    st.session_state.last_text = ""

# --- 4. BILD-GENERATOR (PASSIV-MODUS) ---
def fetch_vision(text_response):
    # Wir probieren Imagen nur, wenn der Text wirklich da ist
    if "📷 Kamera-Feed:" in text_response:
        try:
            start = text_response.find("📷 Kamera-Feed:") + len("📷 Kamera-Feed:")
            end = text_response.find("\n", start)
            scene = text_response[start:end].strip() if end != -1 else text_response[start:].strip()
            
            # Wir erzwingen Imagen 3.0 (die stabilste Version laut deinen Logs)
            img_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
            result = img_model.generate_images(prompt=f"Cyberpunk, neon, grit: {scene}", number_of_images=1)
            return result.images[0].pil_image
        except:
            return None # Lautloser Fehler, damit das Spiel nicht stoppt
    return None

# --- 5. ZENTRALE LOGIK (REAKTIONS-FIX) ---
def process_step(user_input):
    try:
        # 1. Text holen (Muss klappen!)
        response = st.session_state.matrix_session.send_message(user_input)
        st.session_state.last_text = response.text
        
        # 2. Bild versuchen (Darf scheitern!)
        st.session_state.last_image = fetch_vision(response.text)
    except Exception as e:
        st.error(f"VERBINDUNGSABBRUCH: {str(e)}")

# --- 6. UI ANZEIGE ---
# Bild (falls vorhanden)
if st.session_state.last_image:
    st.image(st.session_state.last_image, use_column_width=True)

# Letzte Nachricht (Groß und deutlich)
if st.session_state.last_text:
    st.markdown(st.session_state.last_text)

# Chat-Verlauf (Zusammengeklappt in der Sidebar für Übersicht)
with st.sidebar:
    st.header("System-Log")
    if st.button("SYSTEM RESET / CACHE LEEREN"):
        st.session_state.clear()
        st.rerun()
    for msg in st.session_state.matrix_session.history:
        st.write(f"**{msg.role}:** {msg.parts[0].text[:50]}...")

# Steuerung (Buttons triggern sofort)
st.write("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Option A"): process_step("A"); st.rerun()
with col2:
    if st.button("Option B"): process_step("B"); st.rerun()
with col3:
    if st.button("Option C"): process_step("C"); st.rerun()

user_input = st.chat_input("Tippe 'System Boot'...")
if user_input:
    process_step(user_input)
    st.rerun()
    
