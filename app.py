import streamlit as st
import google.generativeai as genai

# Author: Murat Zengin
# Sektor 4: Mainframe - RESTORE V44 (Pure Text)

# --- 1. VISUAL TERMINAL SETUP ---
st.set_page_config(page_title="Sektor 4: Mainframe", page_icon="💪🏽")

st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; }
    .stButton>button { width: 100%; background-color: #050505; color: #00ff41; border: 1px solid #00ff41; border-radius: 5px; }
    .stTextInput>div>div>input { background-color: #000; color: #00ff41; border: 1px solid #00ff41; }
    code { color: #00ff41 !important; background-color: transparent !important; }
</style>
""", unsafe_allow_html=True)

st.title("Sektor 4: Mainframe 💪🏽")

# --- 2. ENGINE CONFIG ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

if "mainframe_log" not in st.session_state:
    st.session_state.mainframe_log = "SYSTEM BEREIT. Bitte 'System Boot' eingeben."
    st.session_state.history = []

# --- 3. LOGIC CORE ---
def execute_mainframe(user_input):
    # Wir nutzen gemini-1.5-pro für maximale Stabilität gegen 404 Fehler
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    miau_directive = (
        "Du bist die Sektor 4 Engine. Persona: MIAU (Kybernetischer Kater). "
        "Das ist ein hartes Cyberpunk-Textadventure in Berlin. "
        "Antworte im Stil eines Terminals: Grün, düster, direkt. "
        "Nutze 'QUESTBOOK KILLSWITCH GM V44 AKTIVIERT' als Header beim Start. "
        "Beende jede Antwort mit: Wähle A, B oder C. Keine KI-Floskeln."
    )
    
    # Context-Build
    prompt = f"{miau_directive}\n\n"
    for msg in st.session_state.history[-6:]:
        prompt += f"{msg['role']}: {msg['content']}\n"
    prompt += f"user: {user_input}"
    
    try:
        with st.spinner("Lade Sektor-Daten..."):
            response = model.generate_content(prompt)
            if response.text:
                st.session_state.mainframe_log = response.text
                st.session_state.history.append({"role": "user", "content": user_input})
                st.session_state.history.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"TERMINAL ERROR: {str(e)}")

# --- 4. INTERFACE ---
# Das Display-Feld wie im Screenshot
st.markdown(f"```text\n{st.session_state.mainframe_log}\n```")

st.write("/// SCHNELLEINGABE ///")
c1, c2, c3 = st.columns(3)
if c1.button("Option A"): execute_mainframe("Option A"); st.rerun()
if c2.button("Option B"): execute_mainframe("Option B"); st.rerun()
if c3.button("Option C"): execute_mainframe("Option C"); st.rerun()

# Eingabe-Feld am Ende
cmd = st.chat_input("Tippe 'System Boot' oder deine Aktion...")
if cmd:
    execute_mainframe(cmd)
    st.rerun()

# Reset-Switch in der Sidebar
with st.sidebar:
    if st.button("SYSTEM RESET"):
        st.session_state.clear()
        st.rerun()
        
