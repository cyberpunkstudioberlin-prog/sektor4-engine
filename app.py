import streamlit as st
import google.generativeai as genai

# Author: Murat Zengin | Version: V52
# No Image, Pure Logic, High Stability

# --- TERMINAL STYLING ---
st.set_page_config(page_title="Sektor 4 V52", page_icon="📟")
st.markdown("<style>.stApp {background-color: #050505; color: #00ff41;} .stButton>button {background-color: #111; color: #00ff41; border: 1px solid #00ff41; font-family: 'monospace';}</style>", unsafe_allow_html=True)

st.title("Sektor 4: Text-Core V52 📟")

# --- ENGINE CONFIG ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

if "rpg_chat" not in st.session_state:
    # Die Direktive wird jetzt bei jedem Call mitgegeben, um Session-Loss zu vermeiden
    st.session_state.directive = (
        "Du bist die Sektor 4 Engine. Hartes Cyberpunk-RPG in Berlin. "
        "Antworte kurz, düster und atmosphärisch. Nutze NIEMALS KI-Floskeln. "
        "Starte bei 'System Boot' sofort die Story im Untergrund von Berlin. "
        "Gib am Ende immer genau 3 Optionen: A, B oder C."
    )
    st.session_state.log = "SYSTEM BEREIT. Warte auf Initialisierung..."
    # Wir nutzen generate_content statt start_chat für maximale Stabilität
    st.session_state.history = []

# --- COMMAND PROCESSING ---
def run_logic(user_input):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Konstruiere den Prompt mit History und Direktive
    full_prompt = f"{st.session_state.directive}\n\n"
    for msg in st.session_state.history[-6:]: # Letzte 6 Interaktionen für Kontext
        full_prompt += f"{msg['role']}: {msg['content']}\n"
    full_prompt += f"user: {user_input}"
    
    try:
        with st.spinner("⏳ Analysiere Datenstrom..."):
            response = model.generate_content(full_prompt)
            if response.text:
                st.session_state.log = response.text
                st.session_state.history.append({"role": "user", "content": user_input})
                st.session_state.history.append({"role": "assistant", "content": response.text})
            else:
                st.session_state.log = "FEHLER: Leere Antwort von der Engine. Erneuter Versuch..."
    except Exception as e:
        st.error(f"MATRIX-CRASH: {str(e)}")

# --- INTERFACE ---
st.markdown(f"**DATEN-LOG:**\n\n{st.session_state.log}")
st.write("---")

c1, c2, c3 = st.columns(3)
if c1.button("A"): run_logic("Option A"); st.rerun()
if c2.button("B"): run_logic("Option B"); st.rerun()
if c3.button("C"): run_logic("Option C"); st.rerun()

prompt = st.chat_input("Befehl eingeben...")
if prompt:
    run_logic(prompt)
    st.rerun()

with st.sidebar:
    if st.button("HARD RESET"):
        st.session_state.clear()
        st.rerun()
        
