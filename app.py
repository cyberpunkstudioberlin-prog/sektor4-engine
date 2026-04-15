import streamlit as st
import google.generativeai as genai

# --- 1. CYBERPUNK TERMINAL DESIGN ---
st.set_page_config(page_title="Sektor 4 Terminal", page_icon="🦾", layout="centered")

st.markdown("""
<style>
    .stApp {background-color: #050505; color: #00ff41;}
    h1, h2, h3, p, div {font-family: 'Courier New', monospace;}
    .stChatInputContainer textarea {
        background-color: #111 !important; color: #00ff41 !important; border: 1px solid #00ff41 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Sektor 4: Mainframe 🦾")

# --- 2. API INITIALISIERUNG ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("FEHLER: API-Key fehlt.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 3. AUTO-MODELL-SUCHE (DER ENTSCHEIDENDE FIX) ---
if "active_model" not in st.session_state:
    try:
        # Wir fragen Google nach allen verfügbaren Modellen
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Wir suchen bevorzugt nach 'flash', dann nach 'pro'
        target_model = next((m for m in available_models if 'flash' in m.lower()), None)
        if not target_model:
            target_model = next((m for m in available_models if 'pro' in m.lower()), "models/gemini-pro")
        
        st.session_state.active_model = target_model
    except Exception as e:
        st.error(f"VERBINDUNGSFEHLER: {str(e)}")
        st.stop()

st.write(f"/// QUANTEN-LINK ÜBER [{st.session_state.active_model}] AKTIV ///")

# --- 4. SYSTEM PROMPT & ENGINE ---
system_prompt = """[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM V44]
Du bist die 'Sektor 4 Engine', ein dystopischer Cyberpunk Game Master.
Sprache: Deutsch. 
Mechanik: T-Load startet bei 10/100. Bei 100/100 ist GAME OVER.
Start: Bei 'System Boot' rettet der kybernetische Kater den Spieler kurz und verschwindet."""

if "matrix_session" not in st.session_state:
    model = genai.GenerativeModel(
        model_name=st.session_state.active_model,
        system_instruction=system_prompt
    )
    st.session_state.matrix_session = model.start_chat(history=[])

# --- 5. INTERFACE ---
for message in st.session_state.matrix_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Reset Button für Notfälle
if st.button("System Reset"):
    st.session_state.clear()
    st.rerun()

user_input = st.chat_input("Tippe 'System Boot'...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        try:
            response = st.session_state.matrix_session.send_message(user_input)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Sektor 4 Absturz: {str(e)}")
            
