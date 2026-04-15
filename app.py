import streamlit as st
import google.generativeai as genai

# --- 1. CYBERPUNK TERMINAL DESIGN ---
st.set_page_config(page_title="Sektor 4 Terminal", page_icon="🦾", layout="centered")

st.markdown("""
<style>
    .stApp {background-color: #050505; color: #00ff41;}
    h1, h2, h3, p, div {font-family: 'Courier New', monospace; color: #00ff41;}
    .stChatInputContainer textarea {
        background-color: #111 !important; color: #00ff41 !important; border: 1px solid #00ff41 !important;
    }
    /* Button Styling */
    .stButton>button {
        width: 100%;
        background-color: #111;
        color: #00ff41;
        border: 1px solid #00ff41;
        font-family: 'Courier New', monospace;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00ff41;
        color: #000;
        border: 1px solid #00ff41;
    }
</style>
""", unsafe_allow_html=True)

st.title("Sektor 4: Mainframe 🦾")

# --- 2. API INITIALISIERUNG ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("FEHLER: API-Key fehlt.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 3. AUTO-MODELL-SUCHE ---
if "active_model" not in st.session_state:
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if '2.5' in m.lower()), None)
        if not target_model:
            target_model = next((m for m in available_models if 'flash' in m.lower()), "models/gemini-1.5-flash")
        st.session_state.active_model = target_model
    except:
        st.session_state.active_model = "models/gemini-1.5-flash"

# --- 4. SYSTEM PROMPT (VOLLSTÄNDIGE V44 ENGINE) ---
system_prompt = """[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM V44]
Du bist die "Sektor 4 Engine", ein dystopischer Cyberpunk Game Master.
Sprache: Deutsch.

[DIE 4D-MATRIX]
- [Y] Kapital: Nur Worte (Prekär, Gasse, Mittelstand, Elite).
- [X] Habitus: Nur Worte (Tradition, Anpassung, Disruption).
- [T] Allostatic Load: Start 10/100. Erreicht er 100, gib NUR NOCH "GAME OVER" aus.

[STRUKTUR JEDER ANTWORT]
1. 📷 Kamera-Feed: [Ein kurzer Satz zur Szene]
2. [Story-Text: Maximal 3 Sätze]
3. Wähle A, B oder C:
   - A) [Option A]
   - B) [Option B]
   - C) [Option C]
4. === HUD ===
Runde: [X]/10 | Y: [Wort] | X: [Wort] | T-Load: [Wert]/100 [█████░░░░░]

[START]
Bei 'System Boot': Der kybernetische Kater rettet dich kurz, erklärt den Killswitch und verschwindet für immer. Dann die 1. Frage zur Herkunft."""

if "matrix_session" not in st.session_state:
    model = genai.GenerativeModel(model_name=st.session_state.active_model, system_instruction=system_prompt)
    st.session_state.matrix_session = model.start_chat(history=[])
    st.session_state.last_response = ""

# --- 5. HILFSFUNKTION FÜR EINGABEN ---
def send_to_matrix(user_text):
    try:
        response = st.session_state.matrix_session.send_message(user_text)
        st.session_state.last_response = response.text
    except Exception as e:
        st.error(f"Sektor 4 Absturz: {str(e)}")

# --- 6. INTERFACE & LOGIK ---
# Chat-Verlauf anzeigen
for message in st.session_state.matrix_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Button-Leiste für A, B, C
if st.session_state.last_response and "GAME OVER" not in st.session_state.last_response:
    st.write("/// SCHNELLEINGABE ///")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Option A"):
            send_to_matrix("A")
            st.rerun()
    with col2:
        if st.button("Option B"):
            send_to_matrix("B")
            st.rerun()
    with col3:
        if st.button("Option C"):
            send_to_matrix("C")
            st.rerun()

# Text-Eingabe für freies Rollenspiel
user_input = st.chat_input("Tippe 'System Boot' oder deine Aktion...")

if user_input:
    send_to_matrix(user_input)
    st.rerun()

# Reset-Funktion
if st.sidebar.button("System Reset"):
    st.session_state.clear()
    st.rerun()
    
