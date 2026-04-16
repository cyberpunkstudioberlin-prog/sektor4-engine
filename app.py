import streamlit as st
import google.generativeai as genai

# Author: Murat Zengin | Version: V55 Hardwired Pro
st.set_page_config(page_title="Sektor 4: Pro", page_icon="🦾")
st.markdown("<style>.stApp {background-color: #050505; color: #00ff41;}</style>", unsafe_allow_html=True)
st.title("Sektor 4: Mainframe Pro 🦾")

# API KONFIGURATION
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-pro')

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.last_response = "SYSTEM BEREIT. Warte auf 'System Boot'..."

def run_engine(cmd):
    directive = "Du bist die Sektor 4 Engine (MIAU). Cyberpunk RPG Berlin. Header: [SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM V44 AKTIVIERT]. Kurz, düster, keine KI-Floskeln. Immer Optionen A, B, C am Ende."
    context = f"{directive}\n\n"
    for m in st.session_state.chat_history[-5:]:
        context += f"{m['role']}: {m['content']}\n"
    context += f"user: {cmd}"
    try:
        response = model.generate_content(context)
        if response.text:
            st.session_state.last_response = response.text
            st.session_state.chat_history.append({"role": "user", "content": cmd})
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"MATRIX CRASH: {str(e)}")

st.code(st.session_state.last_response, language="text")
st.write("---")
col1, col2, col3 = st.columns(3)
if col1.button("Option A"): run_engine("A"); st.rerun()
if col2.button("Option B"): run_engine("B"); st.rerun()
if col3.button("Option C"): run_engine("C"); st.rerun()

user_input = st.chat_input("Befehl eingeben...")
if user_input:
    run_engine(user_input)
    st.rerun()
    
