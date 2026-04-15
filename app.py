import streamlit as st
import google.generativeai as genai

# --- 1. DESIGN ---
st.set_page_config(page_title="Sektor 4 Terminal", page_icon="🦾", layout="centered")

st.markdown("""
<style>
    .stApp {background-color: #050505; color: #00ff41;}
    h1, h2, h3, p, div {font-family: 'Courier New', monospace;}
    .stChatInputContainer textarea {
        background-color: #111 !important; 
        color: #00ff41 !important; 
        border: 1px solid #00ff41 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Sektor 4: Mainframe 🦾")
st.write("/// INITIALISIERE QUANTEN-VERBINDUNG... ///")

# --- 2. API SETUP ---
try:
    # Wir ziehen den Key aus den Secrets
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"SYSTEMFEHLER: API-Key nicht konfiguriert oder ungültig.")
    st.stop()

# --- 3. SYSTEM PROMPT ---
system_prompt = """[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM V44]
Du bist die "Sektor 4 Engine", ein dystopischer Cyberpunk Game Master.
ALLE Textausgaben MÜSSEN auf Deutsch sein!

[DIE 4D-MATRIX]
- [T] Allostatic Load: Start 10/100.
- KILLSWITCH: Bei 100/100 ist GAME OVER.

[START]
Bei "System Boot": Der kybernetische Kater rettet dich kurz, erklärt den 100/100 Killswitch und verschwindet. Dann die 1. Frage zur Herkunft.
"""

# --- 4. MODELL-INITIALISIERUNG (DER FIX) ---
# Wir nutzen hier den stabilsten Identifikator
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt
    )
    # Test-Aufruf um zu sehen ob das Modell existiert
    if "matrix_session" not in st.session_state:
        st.session_state.matrix_session = model.start_chat(history=[])
except Exception as e:
    st.error(f"MATRIX-FEHLER: Modell nicht erreichbar. Versuche alternative Route...")
    # Notfall-Route falls Flash nicht geht
    model = genai.GenerativeModel(model_name="gemini-pro")
    if "matrix_session" not in st.session_state:
        st.session_state.matrix_session = model.start_chat(history=[])

# --- 5. CHAT ANZEIGE ---
for message in st.session_state.matrix_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# --- 6. EINGABE ---
user_input = st.chat_input("Tippe 'System Boot'...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        try:
            response = st.session_state.matrix_session.send_message(user_input)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"VERBINDUNGSABBRUCH: {str(e)}")
            
