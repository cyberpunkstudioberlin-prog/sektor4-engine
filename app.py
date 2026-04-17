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

# --- 4. SYSTEM PROMPT (V69 - NO ASCII / OMNISCIENT) ---
SYSTEM_INSTRUCTION = """
[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM - V69 ULTRA-MINIMALISM]
Du bist die "Sektor 4 Engine", ein dystopischer Cyberpunk Game Master.
Sprache: Deutsch. Erzähler: ALLWISSEND. Textlänge: KOMPAKT (Max 2 kurze Sätze pro Absatz).

[4D-MATRIX]
- [Y] Kapital: (Prekär, Gasse, Mittelstand, Elite).
- [X] Habitus: (Tradition, Anpassung, Disruption).
- [Z] Biografie: (Fragment, Konstrukt, Agent, Veteran, Legende). Steigt kumulativ.
- [T] Allostatic Load: Start 10/100. Killswitch bei 100/100.

[STRIKTE REGEL: KEIN ASCII]
Generiere NIEMALS ASCII-Art, Text-Grafiken oder visuelle Balken. Nur Text und Emojis.

[LOOT & PROGRESSION]
- Nach Feindkontakt erfolgt Loot-Sequenz basierend auf [X].
- [Z] Biografie steigt nach jeder überlebten Runde/Aktion.

[PACING]
- Gesamtdauer: 10 Runden.
- Phase 1 (1-3): Schergen. Phase 2 (4-7): Krokodil-Jagd. Phase 3 (8-10): Showdown.

[STRUKTUR PRO ANTWORT - STRIKT EINHALTEN]
📷 Kamera-Feed: [1 kurzer analytischer Satz]

🕹️ [Story-Absatz 1: Allwissende Analyse & Z-Zuwachs. Max 2 Sätze.]
⚠️ [Story-Absatz 2: Umgebung & Loot-Ergebnis. Max 2 Sätze.]
💀 [Story-Absatz 3: Unmittelbare Gefahr & Psyche der Figur. Max 2 Sätze.]

Wähle A, B oder C:
A) [Präzise Aktion] ([Mechanik])
B) [Präzise Aktion] ([Mechanik])
C) [Präzise Aktion] ([Mechanik])

📟 === HUD ===
📉 Runde: [X]/10 | Y: [Wort] | X: [Wort] | Z: [Wort]
🧠 T-Load: [Wert]/100
🛡️ [SYSTEM STANDBY]
"""

# --- 5. SESSION MANAGEMENT ---
if "chat" not in st.session_state:
    try:
        # Nutzung des stabilen flash-Modells ohne Präfix zur Vermeidung von 404-Fehlern
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
    if st.button("🔄 System Reset", use_container_width=True):
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
            st.error(f"BOOT-FEHLER: {str(e)}")

if st.session_state.game_started:
    st.write("### Aktions-Matrix:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("A", use_container_width=True):
            res = st.session_state.chat.send_message("Ich wähle Option A.")
            st.session_state.last_response = res.text
            st.rerun()
    with col2:
        if st.button("B", use_container_width=True):
            res = st.session_state.chat.send_message("Ich wähle Option B.")
            st.session_state.last_response = res.text
            st.rerun()
    with col3:
        if st.button("C", use_container_width=True):
            res = st.session_state.chat.send_message("Ich wähle Option C.")
            st.session_state.last_response = res.text
            st.rerun()

    custom_input = st.chat_input("Manueller Override...")
    if custom_input:
        res = st.session_state.chat.send_message(custom_input)
        st.session_state.last_response = res.text
        st.rerun()
