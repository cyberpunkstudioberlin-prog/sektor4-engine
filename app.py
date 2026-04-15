import streamlit as st
import google.generativeai as genai

# --- 1. CYBERPUNK DESIGN ---
st.set_page_config(page_title="Sektor 4 Immortal", page_icon="🦾")
st.markdown("<style>.stApp {background-color: #050505; color: #00ff41;} h1,p,div{font-family: 'Courier New', monospace; color: #00ff41;}</style>", unsafe_allow_html=True)

st.title("Sektor 4: Immortal Terminal 🦾")

# --- 2. API SETUP ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 3. AUTO-MODELL-SCANNER ---
if "active_text_model" not in st.session_state:
    try:
        # Wir suchen das beste Modell (bevorzugt 2.5 oder 1.5 Flash)
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        best_model = next((m for m in available if "2.5" in m), 
                     next((m for m in available if "flash" in m), "models/gemini-1.5-flash"))
        st.session_state.active_text_model = best_model
    except:
        st.session_state.active_text_model = "models/gemini-1.5-flash"

st.write(f"/// SYSTEM-KERN: [{st.session_state.active_text_model}] AKTIV ///")

# --- 4. SESSION INITIALISIERUNG ---
if "matrix_session" not in st.session_state:
    model = genai.GenerativeModel(st.session_state.active_text_model)
    st.session_state.matrix_session = model.start_chat(history=[])
    st.session_state.last_text = "SYSTEM BEREIT. Bitte 'System Boot' eingeben."

# --- 5. ROBUSTE LOGIK MIT SPINNER ---
def run_action(user_input):
    with st.spinner("Signal wird durch die Matrix geroutet..."):
        try:
            response = st.session_state.matrix_session.send_message(user_input)
            st.session_state.last_text = response.text
        except Exception as e:
            st.error(f"VERBINDUNGSFEHLER: {str(e)}")
            # Falls das Modell abgestürzt ist, versuchen wir einen automatischen Reset
            if "not_found" in str(e).lower():
                st.session_state.clear()
                st.rerun()

# --- 6. INTERFACE ---
st.markdown(f"### AKTUELLER STATUS\n{st.session_state.last_text}")

st.write("---")
c1, c2, c3 = st.columns(3)
if c1.button("A"): run_action("A"); st.rerun()
if c2.button("B"): run_action("B"); st.rerun()
if c3.button("C"): run_action("C"); st.rerun()

cmd = st.chat_input("Befehl...")
if cmd:
    run_action(cmd)
    st.rerun()

if st.sidebar.button("FORCE SYSTEM RESET"):
    st.session_state.clear()
    st.rerun()
    
