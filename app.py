import streamlit as st
import google.generativeai as genai

# Author: Murat Zengin
# Project: Questbook / Sektor 4
# Module: V58 Auto-Core

st.set_page_config(page_title="Sektor 4 Auto-Core", page_icon="🦾")
st.markdown("<style>.stApp {background-color: #050505; color: #00ff41;} .stButton>button {background-color: #111; color: #00ff41; border: 1px solid #00ff41;}</style>", unsafe_allow_html=True)
st.title("Sektor 4: V58 Auto-Core 🦾")

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- DER AUTO-SCANNER ---
if "active_model" not in st.session_state:
    try:
        # Wir fragen die API nach allen Modellen, die Text generieren können
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Wir filtern das beste verfügbare Gemini-Modell heraus
        best_match = next((m for m in available_models if "gemini-1.5" in m), None)
        if not best_match:
            best_match = next((m for m in available_models if "gemini" in m), available_models[0])
            
        st.session_state.active_model = best_match
    except Exception as e:
        st.session_state.active_model = "error"
        st.error(f"SCAN FEHLGESCHLAGEN: {e}")

# --- KERN-INITIALISIERUNG ---
if st.session_state.active_model != "error":
    st.write(f"/// MATRIX-LINK ETABLIERT: `{st.session_state.active_model}` ///")
    model = genai.GenerativeModel(st.session_state.active_model)

if "log" not in st.session_state:
    st.session_state.log = "SYSTEM BEREIT. Bitte 'System Boot' eingeben."

def run_core(cmd):
    directive = "Du bist die Sektor 4 Engine. Cyberpunk Textadventure in Berlin. Antworte extrem kurz, düster und dreckig. Biete immer genau die Optionen A, B und C am Ende an."
    try:
        with st.spinner("Pinge Matrix..."):
            response = model.generate_content(f"{directive}\n\nUser: {cmd}")
            st.session_state.log = response.text
    except Exception as e:
        st.session_state.log = f"MATRIX CRASH: {str(e)}"

# --- UI ---
st.markdown(f"**TERMINAL OUTPUT:**\n\n{st.session_state.log}")
st.write("---")

c1, c2, c3 = st.columns(3)
if c1.button("A"): run_core("Option A"); st.rerun()
if c2.button("B"): run_core("Option B"); st.rerun()
if c3.button("C"): run_core("Option C"); st.rerun()

cmd_in = st.chat_input("Konsoleneingabe...")
if cmd_in:
    run_core(cmd_in)
    st.rerun()
    
