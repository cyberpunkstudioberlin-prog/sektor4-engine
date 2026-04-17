import streamlit as st
import google.generativeai as genai
import os

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="Questbook Killswitch 🦾",
    page_icon="🦾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS (TERMINAL STYLE) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #00ff00;
        font-family: 'Courier New', Courier, monospace;
    }
    .terminal-box {
        background-color: #000000;
        border: 1px solid #333333;
        padding: 20px;
        border-radius: 5px;
        color: #00ff00;
        font-family: 'Courier New', Courier, monospace;
        white-space: pre-wrap;
        margin-bottom: 20px;
        line-height: 1.5;
    }
    .stButton>button {
        background-color: #1a1a1a;
        color: #00ff00;
        border: 1px solid #00ff00;
        border-radius: 0px;
        height: 3em;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00ff00;
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API KONFIGURATION & MODELL-FINDER ---
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not api_key:
    st.error("SYSTEM-FEHLER: API-Key fehlt in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

def get_best_model():
    """Findet das beste verfügbare Flash-Modell für diesen API-Key."""
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Priorität: 2.0 Flash -> 1.5 Flash -> 1.5 Flash 8B
        for preferred in ["models/gemini-1.5-flash", "models/gemini-1.5-flash-latest", "models/gemini-2.0-flash-exp"]:
            if preferred in available_models:
                return preferred
        return available_models[0] if available_models else "gemini-1.5-flash"
    except Exception:
        return "gemini-1.5-flash"

# --- 4. SYSTEM PROMPT (V70 - PURE TEXT / OMNISCIENT) ---
SYSTEM_INSTRUCTION = """
[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM - V70]
Du bist die "Sektor 4 Engine".
- Erzähler: ALLWISSEND (kennt Ängste, Psyche und versteckte Gefahren).
- Sprache: Deutsch, kalt, analytisch.
- Länge: Kompakt (Max 2 kurze Sätze pro Absatz).
- KEIN ASCII: Generiere niemals Ladebalken oder Text-Grafiken.

[4D-MATRIX]
- [Y] Kapital: (Prekär, Gasse, Mittelstand, Elite).
- [X] Habitus: (Tradition, Anpassung, Disruption).
- [Z] Biografie: (Fragment, Konstrukt, Agent, Veteran, Legende).
- [T] Allostatic Load: Start 10/100. Killswitch bei 100/100.

[STRUKTUR]
📷 Kamera-Feed: [1 Satz]
🕹️ [Story/Z-Progress]
⚠️ [Umgebung/Loot]
💀 [Gefahr/Psyche]
Multiple Choice A, B, C (mit Mechanik in Klammern).
HUD (Runde [X]/10, Y, X, Z, T-Load).
"""

# --- 5. SESSION MANAGEMENT ---
if "chat" not in st.session_state:
    try:
        model_name = get_best_model()
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_INSTRUCTION
        )
        st.session_state.chat = model.start_chat(history=[])
        st.session_state.game_started = False
        st.session_state.last_response = ""
        st.session_state.active_model = model_name
    except Exception as e:
        st.error(f"INITIALISIERUNGS-FEHLER: {str(e)}")

# Sidebar
with st.sidebar:
    st.header("Sektor 4 Konsole")
    st.info(f"Aktives Modell: {st.session_state.get('active_model', 'Suche...')}")
    if st.button("🔄 System Reset / Hard Reboot", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- 6. UI & SPIEL-LOGIK ---
st.title("Questbook Killswitch 🦾")
st.caption("GOOGLE GEMINI NATIVE // SEKTOR 4 ENGINE")

if st.session_state.last_response:
    st.markdown(f"<div class='terminal-box'>{st.session_state.last_response}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='terminal-box'>SYSTEM BEREIT. Google-Inferenz online.\n\nDrücke 'System Start'.</div>", unsafe_allow_html=True)

if not st.session_state.game_started:
    if st.button("System Start (Boot Sequence)", use_container_width=True):
        try:
            response = st.session_state.chat.send_message("SYSTEM BOOT. Starte das zynische Tutorial.")
            st.session_state.last_response = response.text
            st.session_state.game_started = True
            st.rerun()
        except Exception as e:
            st.error(f"BOOT-FEHLER (404/429): {str(e)}\n\nVersuche einen Hard Reset in der Sidebar.")

if st.session_state.game_started:
    st.write("### Entscheidungs-Matrix:")
    col1, col2, col3 = st.columns(3)
    for idx, opt in enumerate(["A", "B", "C"]):
        if [col1, col2, col3][idx].button(opt, use_container_width=True):
            try:
                res = st.session_state.chat.send_message(f"Ich wähle Option {opt}.")
                st.session_state.last_response = res.text
                st.rerun()
            except Exception as e:
                st.error(f"FEHLER: {str(e)}")
