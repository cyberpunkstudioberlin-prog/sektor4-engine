import streamlit as st
import google.generativeai as genai

# --- 1. SETTINGS & DESIGN ---
st.set_page_config(page_title="Sektor 4 Phoenix", page_icon="🔥")
st.markdown("<style>.stApp {background-color: #0d0d0d; color: #00ff41;} .stButton>button {width:100%; background-color: #1a1a1a; color: #00ff41; border: 1px solid #00ff41;}</style>", unsafe_allow_html=True)

st.title("Sektor 4: Phoenix Terminal 🔥")

# --- 2. API INITIALISIERUNG ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 3. ROBUSTE MODELL-AUSWAHL ---
if "active_model" not in st.session_state:
    # Wir erzwingen hier 1.5-flash, da es am schnellsten reagiert
    st.session_state.active_model = "gemini-1.5-flash"

# --- 4. SESSION MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.last_response = "SYSTEM REBOOT ERFOLGREICH. Warte auf Eingabe..."

# --- 5. DIE LOGIK-ENGINE ---
def send_to_matrix(prompt):
    model = genai.GenerativeModel(st.session_state.active_model)
    
    # Wir bauen den Kontext jedes Mal frisch auf, um "Hänger" zu vermeiden
    full_context = "Du bist die Sektor 4 KI in einem Cyberpunk-Rollenspiel. Antworte kurz und atmosphärisch. "
    for m in st.session_state.messages[-5:]: # Nur die letzten 5 Nachrichten für Stabilität
        full_context += f"\n{m['role']}: {m['content']}"
    full_context += f"\nuser: {prompt}"

    try:
        with st.spinner("⚡ Datenstrom wird stabilisiert..."):
            response = model.generate_content(full_context)
            if response.text:
                st.session_state.last_response = response.text
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.warning("Die Matrix schweigt. Versuche es erneut.")
    except Exception as e:
        st.error(f"MATRIX-FEHLER: {str(e)}")
        if "404" in str(e) or "not found" in str(e).lower():
            st.info("Modell-Konflikt erkannt. Setze System zurück...")
            st.session_state.clear()
            st.rerun()

# --- 6. INTERFACE ---
st.markdown(f"**STATUS:**\n{st.session_state.last_response}")

st.write("---")
col1, col2, col3 = st.columns(3)
if col1.button("Option A"): send_to_matrix("A"); st.rerun()
if col2.button("Option B"): send_to_matrix("B"); st.rerun()
if col3.button("Option C"): send_to_matrix("C"); st.rerun()

input_text = st.chat_input("Befehl an die Engine...")
if input_text:
    send_to_matrix(input_text)
    st.rerun()

# Sidebar für den Notfall
with st.sidebar:
    st.header("Admin-Konsole")
    if st.button("KALTSTART (Clear Cache)"):
        st.session_state.clear()
        st.rerun()
        
