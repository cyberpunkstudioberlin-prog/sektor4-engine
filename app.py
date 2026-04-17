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
    /* Buttons Customization */
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
        border: 1px solid #00ff00;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API KONFIGURATION ---
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not api_key:
    st.error("KRITISCHER FEHLER: API-Key nicht gefunden. Bitte in Streamlit Secrets hinterlegen.")
    st.stop()

genai.configure(api_key=api_key)

# --- 4. SYSTEM PROMPT (STABLE BUILD V68 - NO ASCII) ---
SYSTEM_INSTRUCTION = """
[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM - V68 PURE MINIMALISM]
Du bist die "Sektor 4 Engine", ein dystopischer Cyberpunk Game Master.
Sprache: Deutsch. Erzähler: Allwissend. Textlänge: Kompakt (max. 2 Sätze pro Absatz).

[4D-MATRIX & LOGIK]
- [Y] Kapital: (Prekär, Gasse, Mittelstand, Elite).
- [X] Habitus: (Tradition, Anpassung, Disruption).
- [Z] Biografie: (Fragment, Konstrukt, Agent, Veteran, Legende). Progressionswert.
- [T] Allostatic Load: Start 10/100. Killswitch bei 100/100.

[STRIKTE REGEL: KEINE ASCII-ART]
Generiere unter keinen Umständen ASCII-Art, Grafiken aus Textzeichen oder visuelle Ladebalken. Nur reiner Text und Emojis/Icons sind erlaubt.

[LOOT-MECHANIK]
- Loot-Qualität hängt von X (Habitus) ab.
- Tradition: Stabiles Y. Disruption: Riskantes hohes Y (T-Load Risiko).

[PACING]
- 10 Runden insgesamt. 
- Eskalation (Spannungsbogen) in Runde 4 (Krokodil erscheint) und Runde 8 (Showdown).

[STRUKTUR PRO ANTWORT]
📷 Kamera-Feed: [1 kurzer analytischer Satz]
🕹️ [Story: Konsequenz & Z-Progress. Max 2 Sätze]
⚠️ [Umgebung: Loot-Chance & Situation. Max 2 Sätze]
💀 [Gefahr: Unmittelbare Bedrohung. Max 2 Sätze]

Wähle A, B oder C:
A) [Aktion] ([Mechanik])
B) [Aktion] ([Mechanik])
C) [Aktion] ([Mechanik])

📟 === HUD ===
📉 Runde: [X]/10 | Y: [Wort] | X: [Wort] | Z: [Wort]
🧠 T-Load: [Wert]/100
"""

# --- 5. SESSION MANAGEMENT ---
if "chat" not in st.session_state:
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        st.session_state.chat = model.start_chat(history=[])
        st.session_state.game_started = False
        st.session_state.last_response = ""
    except Exception as e:
        st.error(f"INITIALISIERUNGSFEHLER: {str(e)}")

# Sidebar für Hard-Reset
with st.sidebar:
    st.header("Sektor 4 Konsole")
    if st.button("🔄 Hard Reset (Simulation Neustart)", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.caption("Nutze den Reset, wenn das System keine Antwort liefert.")

# --- 6. UI & SPIEL-LOGIK ---
st.title("Questbook Killswitch 🦾")
st.caption("GOOGLE GEMINI NATIVE // SEKTOR 4 ENGINE")

# Haupt-Terminal
if st.session_state.last_response:
    st.markdown(f"<div class='terminal-box'>{st.session_state.last_response}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='terminal-box'>SYSTEM BEREIT. Google-Inferenz online.\n\nDrücke 'System Start' zur Initialisierung der 4D-Matrix.</div>", unsafe_allow_html=True)

# Startvorgang
if not st.session_state.game_started:
    if st.button("System Start (Boot Sequence)", use_container_width=True):
        with st.spinner("Initialisiere neuronale Matrix..."):
            try:
                response = st.session_state.chat.send_message("SYSTEM BOOT. Starte das zynische Tutorial und setze initiale Parameter.")
                st.session_state.last_response = response.text
                st.session_state.game_started = True
                st.rerun()
            except Exception as e:
                st.error(f"BOOT-FEHLER: {str(e)}")

# Multiple Choice Steuerung
if st.session_state.game_started:
    st.write("### Aktions-Matrix:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("A", use_container_width=True):
            with st.spinner("Analysiere Option A..."):
                res = st.session_state.chat.send_message("Ich wähle Option A.")
                st.session_state.last_response = res.text
                st.rerun()
                
    with col2:
        if st.button("B", use_container_width=True):
            with st.spinner("Analysiere Option B..."):
                res = st.session_state.chat.send_message("Ich wähle Option B.")
                st.session_state.last_response = res.text
                st.rerun()
                
    with col3:
        if st.button("C", use_container_width=True):
            with st.spinner("Analysiere Option C..."):
                res = st.session_state.chat.send_message("Ich wähle Option C.")
                st.session_state.last_response = res.text
                st.rerun()

    # Manueller Input für fortgeschrittene Nutzer
    custom_input = st.chat_input("Eigener Override-Befehl...")
    if custom_input:
        with st.spinner("Verarbeite Override..."):
            res = st.session_state.chat.send_message(custom_input)
            st.session_state.last_response = res.text
            st.rerun()
