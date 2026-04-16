import streamlit as st
import google.generativeai as genai

# Author: Murat Zengin
# Project: Questbook Killswitch
# Module: V63 Core (ASCII & Hard Paragraphs)

st.set_page_config(page_title="Questbook Killswitch", page_icon="🦾")
st.markdown("<style>.stApp {background-color: #050505; color: #00ff41;} .stButton>button {background-color: #111; color: #00ff41; border: 1px solid #00ff41;}</style>", unsafe_allow_html=True)
st.title("Questbook Killswitch 🦾")

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- AUTO-SCANNER ---
if "active_model" not in st.session_state:
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.session_state.active_model = next((m for m in available if "gemini-2.5" in m), next((m for m in available if "gemini-1.5" in m), available[0]))
    except Exception:
        st.session_state.active_model = "models/gemini-1.5-pro-latest"

model = genai.GenerativeModel(st.session_state.active_model)

# --- SESSION ---
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
    st.session_state.display_text = "SYSTEM BEREIT. Bitte 'System Boot' eingeben."

# --- LOGIK & LORE ---
def run_core(cmd):
    directive = """[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM]
Du bist die "Sektor 4 Engine", ein unerbittlicher Cyberpunk/Steampunk Game Master.

[FORMATIERUNGS-PROTOKOLL: ZWINGEND]
1. Kürze alle Texte auf das absolute Minimum (KISS-Prinzip).
2. Beginne JEDEN Absatz zwingend mit einem passenden Icon (Emoji).
3. Trenne die Optionen A, B und C IMMER durch harte Absätze (Leerzeilen) voneinander.
4. Generiere vor den Handlungsoptionen IMMER ein kontext-sensitives ASCII-Art (max 7 Zeilen) in einem Code-Block.

[DIE 4D-MATRIX]
- [Y] Kapital: Ökonomischer Status.
- [X] Habitus: Soziales Verhalten.
- [Z] Biografie: Herkunft.
- [T] Allostatic Load (Stress): Startet bei 10/100. Killswitch bei 100.

[CRITICAL ERROR OVERRIDE]
- Startausgabe: "📸 Kamera-Feed: [1 kurzer atmosphärischer Satz]".
- Keine Menschen, kein Blut, keine echte Gewalt! Nur Maschinen und Tiere.

[SPIELABLAUF: KAPITEL 1]
Endboss: Necromancer Krokodil. Runden 1-9: Flucht/Hacken. Runde 10: Showdown.

[AUTO-START PROTOKOLL: TUTORIAL]
WENN Nutzer "System Boot" tippt, antworte exakt so:

📸 Kamera-Feed: Ein Steampunk-Kater durchbohrt eine surrende Drohne. Funken regnen in die nasse Cyberpunk-Gasse.

```text
   /\\_/\\
  ( o.o )
   > ^ <
    | |
   /|-|\\
  /_|_|_\\
  
