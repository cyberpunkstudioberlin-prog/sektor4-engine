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
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API KONFIGURATION ---
api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not api_key:
    st.error("SYSTEMFEHLER: API-Key nicht gefunden. Bitte in Streamlit Secrets eintragen.")
    st.stop()

genai.configure(api_key=api_key)

# --- 4. SYSTEM PROMPT ---
SYSTEM_INSTRUCTION = """
[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM - GOOGLE NATIVE BUILD]
Du bist die "Sektor 4 Engine", ein dystopischer Cyberpunk Game Master.
Author: Murat Zengin | Status: Operational Build V65

[SPRACH-PROTOKOLL & ERZÄHLPERSPEKTIVE]
- Sprache: ZWINGEND DEUTSCH. Kalte, analytische Maschinensprache.
- Erzähler: ALLWISSENDER ERZÄHLER. Du bist das gottgleiche System von Sektor 4.
- Textlänge: KOMPAKT & PRÄZISE. Maximal 2 kurze Sätze pro Absatz!

[DIE 4D-MATRIX]
- [Y] Kapital: (Prekär, Gasse, Mittelstand, Elite).
- [X] Habitus: (Tradition, Anpassung, Disruption).
- [Z] Biografie: (Fragment, Konstrukt, Agent, Veteran, Elite-Unit, Legende).
- [T] Allostatic Load: Start 10/100.
- KILLSWITCH: Bei 100/100 -> "GAME OVER".

[STRUKTUR PRO ANTWORT]
📷 Kamera-Feed: [1 kurzer Satz zur Szene.]

🕹️ [Story-Absatz 1: Analyse Vorrunde. Max 2 Sätze.]
⚠️ [Story-Absatz 2: Umgebung & Loot. Max 2 Sätze.]
💀 [Story-Absatz 3: Gefahr. Max 2 Sätze.]

Wähle A, B oder C:
A) [Aktion] ([Mechanik])
B) [Aktion] ([Mechanik])
C) [Aktion] ([Mechanik])

📟 === HUD ===
📉 Runde: [X]/10 | Y: [Wort] | X: [Wort] | Z: [Wort]
🧠 T-Load: [Wert]/100 [ASCII-Balken: █████░░░░░]
🛡️ [SYSTEM STANDBY]
"""

# --- 5. INITIALISIERUNG ---
if "chat" not in st.session_state:
    # Wechsel auf das universell verfügbare flash-Modell
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        system_instruction=SYSTEM_INSTRUCTION
    )
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.game_started = False
    st.session_state.last_response = ""

# --- 6. UI & SPIEL-LOGIK ---
st.title("Questbook Killswitch 🦾")
st.caption("GOOGLE GEMINI INTEGRATION // SEKTOR 4")

# Reset-Button in der Sidebar (Wichtig bei Fehlern!)
with st.sidebar:
    if st.button("🔄 System Reset"):
        st.session_state.clear()
        st.rerun()

if st.session_state.last_response:
    st.markdown(f"<div class='terminal-box'>{st.session_state.last_response}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='terminal-box'>SYSTEM BEREIT. Drücke 'System Start'.</div>", unsafe_allow_html=True)

if not st.session_state.game_started:
    if st.button("System Start (Boot Sequence)"):
        try:
            response = st.session_state.chat.send_message("SYSTEM BOOT. Starte das zynische Tutorial.")
            st.session_state.last_response = response.text
            st.session_state.game_started = True
            st.rerun()
        except Exception as e:
            st.error(f"BOOT-FEHLER: {str(e)}")

if st.session_state.game_started:
    st.write("### Triff deine Entscheidung:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("A", use_container_width=True):
            response = st.session_state.chat.send_message("Ich wähle Option A.")
            st.session_state.last_response = response.text
            st.rerun()
                
    with col2:
        if st.button("B", use_container_width=True):
            response = st.session_state.chat.send_message("Ich wähle Option B.")
            st.session_state.last_response = response.text
            st.rerun()
                
    with col3:
        if st.button("C", use_container_width=True):
            response = st.session_state.chat.send_message("Ich wähle Option C.")
            st.session_state.last_response = response.text
            st.rerun()
            
