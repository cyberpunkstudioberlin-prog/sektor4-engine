import streamlit as st
import google.generativeai as genai

# Author: Murat Zengin | Version: V53 (Pure Text - Deep Link)

# --- STYLING ---
st.set_page_config(page_title="Sektor 4 V53", page_icon="📟")
st.markdown("<style>.stApp {background-color: #050505; color: #00ff41;} .stButton>button {background-color: #111; color: #00ff41; border: 1px solid #00ff41; font-family: 'monospace';}</style>", unsafe_allow_html=True)

st.title("Sektor 4: Text-Core V53 📟")

# --- API SETUP ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

if "log" not in st.session_state:
    st.session_state.log = "SYSTEM BEREIT. Warte auf 'System Boot'..."
    st.session_state.history = []

# --- CORE ENGINE ---
def run_logic(user_input):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Klare System-Vorgabe für jede Anfrage
        directive = (
            "Du bist die Sektor 4 Engine. Ein düsteres Cyberpunk-RPG in Berlin. "
            "Antworte kurz und knackig. Starte die Story bei 'System Boot'. "
            "Biete immer Optionen A, B, C an. Keine KI-Floskeln!"
        )
        
        # Kontext-Konstruktion
        full_prompt = f"{directive}\n\n"
        for msg in st.session_state.history[-4:]: # Fokus auf die letzten 4
            full_prompt += f"{msg['role']}: {msg['content']}\n"
        full_prompt += f"user: {user_input}"
        
        with st.spinner("📟 SYNCHRONISIERE..."):
            response = model.generate_content(full_prompt)
            
            # Sicherheitscheck für die Antwort
            if response and response.text:
                output = response.text
            else:
                output = "⚠️ DATENSTROM UNTERBROCHEN. Bitte Befehl erneut senden."
            
            st.session_state.log = output
            st.session_state.history.append({"role": "user", "content": user_input})
            st.session_state.history.append({"role": "assistant", "content": output})
            
    except Exception as e:
        st.error(f"MATRIX-CRASH: {str(e)}")

# --- UI ---
st.info(st.session_state.log)
st.write("---")

c1, c2, c3 = st.columns(3)
if c1.button("Option A"): run_logic("Option A"); st.rerun()
if c2.button("Option B"): run_logic("Option B"); st.rerun()
if c3.button("Option C"): run_logic("Option C"); st.rerun()

prompt = st.chat_input("Befehl...")
if prompt:
    run_logic(prompt)
    st.rerun()

with st.sidebar:
    if st.button("HARD RESET"):
        st.session_state.clear()
        st.rerun()
        
