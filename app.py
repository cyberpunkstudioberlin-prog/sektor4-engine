import streamlit as st
import google.generativeai as genai
import os

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="Questbook Killswitch 🦾",
    page_icon="🦾",
    layout="centered"
)

# --- 2. CUSTOM CSS (TERMINAL STYLE) ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #00ff00; font-family: monospace; }
    .terminal-box { background-color: #000000; border: 1px solid #333; padding: 20px; border-radius: 5px; color: #00ff00; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 3. API KONFIGURATION ---
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
if not api_key:
    st.error("SYSTEMFEHLER: API-Key fehlt.")
    st.stop()

genai.configure(api_key=api_key)

# --- 4. SYSTEM PROMPT ---
SYSTEM_INSTRUCTION = """
[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM]
Du bist die "Sektor 4 Engine".
- Erzähler: ALLWISSEND.
- Textlänge: KOMPAKT (Max 2 Sätze pro Absatz).
- Struktur: 📷 Kamera-Feed, 🕹️ Story, ⚠️ Umgebung, 💀 Gefahr, A/B/C Optionen, 📟 HUD.
"""

# --- 5. MODELL-INITIALISIERUNG (FIX) ---
if "chat" not in st.session_state:
    try:
        # Wir nutzen den exakten Namen für die produktive v1 API
        model = genai.GenerativeModel(
            model_name="models/gemini-1.5-flash", 
            system_instruction=SYSTEM_INSTRUCTION
        )
        st.session_state.chat = model.start_chat(history=[])
        st.session_state.game_started = False
        st.session_state.last_response = ""
    except Exception as e:
        st.error(f"Initialisierungsfehler: {e}")

# --- 6. UI ---
st.title("Questbook Killswitch 🦾")
st.caption("GOOGLE GEMINI NATIVE // SEKTOR 4")

with st.sidebar:
    if st.button("🔄 Hard Reset"):
        st.session_state.clear()
        st.rerun()

if st.session_state.last_response:
    st.markdown(f"<div class='terminal-box'>{st.session_state.last_response}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='terminal-box'>SYSTEM BEREIT. Drücke 'System Start'.</div>", unsafe_allow_html=True)

if not st.session_state.game_started:
    if st.button("System Start (Boot Sequence)"):
        try:
            # Expliziter Boot-Befehl
            response = st.session_state.chat.send_message("SYSTEM BOOT. Starte Tutorial.")
            st.session_state.last_response = response.text
            st.session_state.game_started = True
            st.rerun()
        except Exception as e:
            st.error(f"BOOT-FEHLER: {e}")

# --- 7. BUTTON LOGIK ---
if st.session_state.game_started:
    col1, col2, col3 = st.columns(3)
    for idx, opt in enumerate(["A", "B", "C"]):
        if [col1, col2, col3][idx].button(opt, use_container_width=True):
            res = st.session_state.chat.send_message(f"Ich wähle Option {opt}.")
            st.session_state.last_response = res.text
            st.rerun()
            
