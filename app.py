import streamlit as st
import google.generativeai as genai

# Author: Murat Zengin
# Sektor 4: Core Engine V50

# --- 1. SETTINGS ---
st.set_page_config(page_title="Sektor 4 Core", page_icon="⚙️")
st.markdown("<style>.stApp {background-color: #0d0d0d; color: #00ff41;} .stButton>button {width:100%; background-color: #1a1a1a; color: #00ff41; border: 1px solid #00ff41;}</style>", unsafe_allow_html=True)
st.title("Sektor 4: Core Terminal ⚙️")

# --- 2. API ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 3. KERN-INITIALISIERUNG ---
if "matrix_session" not in st.session_state:
    # Verankerung der Cyberpunk-Direktive als unumstößliche System-Instruktion
    system_directive = (
        "Du bist die Sektor 4 Engine. Dies ist ein hartes Cyberpunk-Text-Adventure in Berlin. "
        "Antworte ausschließlich im düsteren Rollenspiel-Stil. Nutze keine KI-Standardfloskeln. "
        "Auf den Befehl 'System Boot' startest du die Story im Sektor 4. Biete immer 3 Optionen (A, B, C) an."
    )
    
    # Nutzung des generischen Flash-Modells mit fester Instruktion
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_directive)
    st.session_state.matrix_session = model.start_chat(history=[])
    st.session_state.last_response = "SYSTEM BEREIT. Warten auf 'System Boot'..."

# --- 4. LOGIK ---
def execute_cmd(cmd):
    with st.spinner("Prozess läuft..."):
        try:
            response = st.session_state.matrix_session.send_message(cmd)
            st.session_state.last_response = response.text
        except Exception as e:
            st.error(f"SYSTEMFEHLER: {str(e)}")

# --- 5. UI ---
st.markdown(f"**FEED:**\n{st.session_state.last_response}")
st.write("---")

col1, col2, col3 = st.columns(3)
if col1.button("Option A"): execute_cmd("A"); st.rerun()
if col2.button("Option B"): execute_cmd("B"); st.rerun()
if col3.button("Option C"): execute_cmd("C"); st.rerun()

user_in = st.chat_input("Befehl...")
if user_in:
    execute_cmd(user_in)
    st.rerun()

with st.sidebar:
    st.header("Admin")
    if st.button("KALTSTART"):
        st.session_state.clear()
        st.rerun()
        
