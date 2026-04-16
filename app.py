import streamlit as st
import google.generativeai as genai

# Author: Murat Zengin
# Project: Questbook / Sektor 4
# Module: Pure Text Engine V51

# --- 1. SYSTEM CONFIG ---
st.set_page_config(page_title="Sektor 4 Text-Core", page_icon="🖲️")
st.markdown("<style>.stApp {background-color: #050505; color: #00ff41;} .stButton>button {width:100%; background-color: #111; color: #00ff41; border: 1px solid #00ff41; font-family: 'Courier New', monospace;}</style>", unsafe_allow_html=True)
st.title("Sektor 4: Text-Core 🖲️")

# --- 2. API LINK ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 3. CORE LOGIC ---
if "rpg_session" not in st.session_state:
    # No Bullshit Routine: Feste Rollenspiel-Parameter
    directive = (
        "Du bist die Sektor 4 Engine. Dies ist ein hartes, düsteres Cyberpunk-Text-Adventure in Berlin. "
        "Autorun und Autosave sind aktiviert. Keine KI-Floskeln. "
        "Antworte ausschließlich in der Welt des Spiels. Reagiere auf 'System Boot' mit dem Start der Story. "
        "Beende jede Ausgabe zwingend mit 3 konkreten Handlungsoptionen (A, B, C)."
    )
    
    # Text-Exklusives Modell
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=directive)
    st.session_state.rpg_session = model.start_chat(history=[])
    st.session_state.feed = "SYSTEM BEREIT. Bildgenerator offline. Text-Modus exklusiv. Warten auf 'System Boot'..."

# --- 4. EXECUTION ---
def process_command(cmd):
    with st.spinner("Autorun läuft..."):
        try:
            response = st.session_state.rpg_session.send_message(cmd)
            st.session_state.feed = response.text
        except Exception as e:
            st.error(f"ENGINE FEHLER: {str(e)}")

# --- 5. INTERFACE ---
st.markdown(f"**DATEN-LOG:**\n\n{st.session_state.feed}")
st.write("---")

c1, c2, c3 = st.columns(3)
if c1.button("Option A"): process_command("A"); st.rerun()
if c2.button("Option B"): process_command("B"); st.rerun()
if c3.button("Option C"): process_command("C"); st.rerun()

cmd_input = st.chat_input("Konsoleneingabe...")
if cmd_input:
    process_command(cmd_input)
    st.rerun()

# --- 6. ADMIN ---
with st.sidebar:
    if st.button("KALTSTART (RESET)"):
        st.session_state.clear()
        st.rerun()
        
