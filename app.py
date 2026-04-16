import streamlit as st
import google.generativeai as genai

# Author: Murat Zengin
# Sektor 4 - Legacy Core (Text-Only)

# --- CONFIG ---
st.set_page_config(page_title="Sektor 4 Legacy", page_icon="📟")
st.markdown("<style>.stApp {background-color: #050505; color: #00ff41;} .stButton>button {background-color: #111; color: #00ff41; border: 1px solid #00ff41;}</style>", unsafe_allow_html=True)

st.title("Sektor 4: Legacy Core 📟")

# --- API ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- SESSION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.system_prompt = (
        "Du bist die Sektor 4 Engine. Cyberpunk-RPG Berlin. "
        "Kurze, düstere Antworten. Keine KI-Floskeln. Immer Optionen A, B, C anbieten. "
        "Reagiere auf 'System Boot' mit dem Spielstart."
    )

# --- DISPLAY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LOGIK ---
def chat(text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    # Wir schicken den gesamten Verlauf als flachen Text für maximale Stabilität
    prompt = st.session_state.system_prompt + "\n\n"
    for m in st.session_state.messages[-10:]: # Letzte 10 Nachrichten für Kontext
        prompt += f"{m['role']}: {m['content']}\n"
    prompt += f"user: {text}"
    
    try:
        response = model.generate_content(prompt)
        if response.text:
            st.session_state.messages.append({"role": "user", "content": text})
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun()
    except Exception as e:
        st.error(f"MATRIX CRASH: {e}")

# --- INPUT ---
st.write("---")
c1, c2, c3 = st.columns(3)
if c1.button("A"): chat("Option A")
if c2.button("B"): chat("Option B")
if c3.button("C"): chat("Option C")

user_in = st.chat_input("System Boot eingeben...")
if user_in:
    chat(user_in)

# --- ADMIN ---
if st.sidebar.button("HARD RESET"):
    st.session_state.messages = []
    st.rerun()
    
