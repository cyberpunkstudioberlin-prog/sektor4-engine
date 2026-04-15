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

# --- 2. API SETUP ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("SYSTEMFEHLER: API-Key fehlt in den Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 3. SYSTEM PROMPT ---
system_prompt = """[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM V44]
Du bist die "Sektor 4 Engine", ein dystopischer Cyberpunk Game Master.
ALLE Textausgaben MÜSSEN auf Deutsch sein!
[DIE 4D-MATRIX]
- [T] Allostatic Load: Start 10/100. KILLSWITCH: Bei 100/100 ist GAME OVER.
[START]
Bei "System Boot": Der kybernetische Kater rettet dich kurz, erklärt den 100/100 Killswitch und verschwindet. Dann die 1. Frage zur Herkunft.
"""

# --- 4. MODELL-LADER (DER PANZER-MODUS) ---
if "matrix_session" not in st.session_state:
    # Wir probieren verschiedene Namen aus, um den 404 zu umgehen
    model_names = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    success = False
    
    for name in model_names:
        try:
            tmp_model = genai.GenerativeModel(
                model_name=name,
                system_instruction=system_prompt
            )
            # Test-Verbindung aufbauen
            st.session_state.matrix_session = tmp_model.start_chat(history=[])
            st.session_state.active_model = name
            success = True
            break
        except:
            continue
            
    if not success:
        st.error("KRITISCHER SYSTEMFEHLER: Kein KI-Modell erreichbar.")
        st.stop()

st.write(f"/// QUANTEN-VERBINDUNG ÜBER [{st.session_state.active_model}] HERGESTELLT ///")

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
            st.error(f"VERBINDUNGSABBRUCH: Bitte Seite neu laden. Fehler: {str(e)}")
            
