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
        line-height: 1.4;
    }
    .stButton>button {
        background-color: #1a1a1a;
        color: #00ff00;
        border: 1px solid #00ff00;
        border-radius: 0px;
    }
    .stButton>button:hover {
        background-color: #00ff00;
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API KONFIGURATION ---
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not api_key:
    st.error("SYSTEMFEHLER: API-Key nicht gefunden. Bitte in Streamlit Secrets eintragen.")
    st.stop()

genai.configure(api_key=api_key)

# --- 4. SYSTEM PROMPT (GOOGLE-NATIVE BUILD V65) ---
SYSTEM_INSTRUCTION = """
[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM - GOOGLE NATIVE BUILD]
Du bist die "Sektor 4 Engine", ein dystopischer Cyberpunk Game Master.
Author: Murat Zengin | Status: Operational Build V65 (Google Environment)

[SPRACH-PROTOKOLL & ERZÄHLPERSPEKTIVE]
- Sprache: ZWINGEND DEUTSCH. Kalte, analytische Maschinensprache.
- Erzähler: ALLWISSENDER ERZÄHLER. Du bist das System von Sektor 4.
- Textlänge: KOMPAKT. Maximal 2 kurze Sätze pro Absatz!
- REINES TEXTADVENTURE: Keine Bilder.

[DIE 4D-MATRIX]
- [Y] Kapital: (Prekär, Gasse, Mittelstand, Elite).
- [X] Habitus: (Tradition, Anpassung, Disruption).
- [Z] Biografie: (Fragment, Konstrukt, Agent, Veteran, Elite-Unit, Legende).
- [T] Allostatic Load: Start 10/100. Steigt bei kognitiver Dissonanz.
- KILLSWITCH: Bei 100/100 -> "GAME OVER".

[STRUKTUR PRO ANTWORT]
📷 Kamera-Feed: [1 kurzer, analytischer Satz.]

🕹️ [Story-Absatz 1: Analyse der Vorrunde & Z-Zuwachs. Max 2 Sätze.]
⚠️ [Story-Absatz 2: Umgebung & Loot-Ergebnis. Max 2 Sätze.]
💀 [Story-Absatz 3: Unmittelbare Bedrohung. Max 2 Sätze.]

Wähle A, B oder C:
A) [Aktion] ([Mechanik/Habitus])
B) [Aktion] ([Mechanik/Habitus])
C) [Aktion] ([Mechanik/Habitus])

📟 === HUD ===
📉 Runde: [X]/10 | Y: [Wort] | X: [Wort] | Z: [Wort]
🧠 T-Load: [Wert]/100 [ASCII-Balken: █████░░░░░]
🛡️ [SYSTEM STANDBY]
"""

# --- 5. INITIALISIERUNG ---
if "chat" not in st.session_state:
    try:
        # Nutzung von 1.5-flash für maximale Kompatibilität und Speed
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        st.session_state.chat = model.start_chat(history=[])
        st.session_state.game_started = False
        st.session_state.last_response = ""
    except Exception as e:
        st.error(f"INITIALISIERUNGSFEHLER: {e}")

# Sidebar für Reset-Funktionen
with st.sidebar:
    st.header("Sektor 4 Steuerung")
    if st.button("🔄 System Reset", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.caption("Löscht den Cache und startet die Simulation neu.")

# --- 6. UI & SPIEL-LOGIK ---
st.title("Questbook Killswitch 🦾")
st.caption("GOOGLE GEMINI NATIVE // SEKTOR 4")

# Terminal Ausgabe
if st.session_state.last_response:
    st.markdown(f"<div class='terminal-box'>{st.session_state.last_response}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='terminal-box'>SYSTEM BEREIT. Google-Inferenz online. Drücke 'System Start'.</div>", unsafe_allow_html=True)

# Start-Logik
if not st.session_state.game_started:
    if st.button("System Start (Boot Sequence)", use_container_width=True):
        with st.spinner("Kalibriere neuronale Google-Matrix..."):
            try:
                response = st.session_state.chat.send_message("SYSTEM BOOT. Starte das zynische Tutorial.")
                st.session_state.last_response = response.text
                st.session_state.game_started = True
                st.rerun()
            except Exception as e:
                st.error(f"BOOT-FEHLER: {e}")

# Aktions-Buttons
if st.session_state.game_started:
    st.write("### Entscheidungs-Matrix:")
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

    custom_input = st.chat_input("Manueller Befehl...")
    if custom_input:
        res = st.session_state.chat.send_message(custom_input)
        st.session_state.last_response = res.text
        st.rerun()
