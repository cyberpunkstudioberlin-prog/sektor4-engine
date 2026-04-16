import streamlit as st
import google.generativeai as genai

# Author: Murat Zengin
# Project: Questbook Killswitch
# Module: V64 Core (Fix: Syntax & ASCII Integration)

st.set_page_config(page_title="Questbook Killswitch", page_icon="🦾")
st.markdown("<style>.stApp {background-color: #050505; color: #00ff41;} .stButton>button {background-color: #111; color: #00ff41; border: 1px solid #00ff41;}</style>", unsafe_allow_html=True)
st.title("Questbook Killswitch 🦾")

# --- ENGINE CONFIG ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

if "active_model" not in st.session_state:
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.session_state.active_model = next((m for m in available if "gemini-2.5" in m), next((m for m in available if "gemini-1.5" in m), available[0]))
    except Exception:
        st.session_state.active_model = "models/gemini-1.5-pro-latest"

model = genai.GenerativeModel(st.session_state.active_model)

if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
    st.session_state.display_text = "SYSTEM BEREIT. Bitte 'System Boot' eingeben."

# --- CORE ENGINE ---
def run_core(cmd):
    # [span_0](start_span)Die Lore & Gameplay Regeln [cite: 1-21]
    directive = """[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM]
[cite_start]Du bist die "Sektor 4 Engine", ein unerbittlicher Cyberpunk/Steampunk Game Master[span_0](end_span).

[FORMATIERUNGS-PROTOKOLL: ZWINGEND]
1. Kürze alle Texte auf das absolute Minimum (KISS-Prinzip).
2. Beginne JEDEN Absatz zwingend mit einem passenden Icon (Emoji).
3. Generiere vor den Optionen IMMER ein kontext-sensitives ASCII-Art (max 7 Zeilen) in einem Code-Block, das die aktuelle Szene visuell darstellt.
4. Trenne die Optionen A, B und C IMMER durch harte Absätze (Leerzeilen) voneinander.

[DIE 4D-MATRIX]
- [span_1](start_span)[Y] Kapital (Ökonomie), [X] Habitus (Verhalten), [Z] Biografie (Herkunft)[span_1](end_span).
- [T] Allostatic Load (Stress): Startet bei 10/100. [span_2](start_span)Killswitch bei 100 = Game Over[span_2](end_span).

[CRITICAL ERROR OVERRIDE]
- [span_3](start_span)Startausgabe: "📸 Kamera-Feed: [1 kurzer atmosphärischer Satz]"[span_3](end_span).
- Keine Menschen, kein Blut, keine Gewalt! [span_4](start_span)Nur Maschinen und Tiere[span_4](end_span).

[SPIELABLAUF: KAPITEL 1]
- [span_5](start_span)Endboss: Necromancer Krokodil[span_5](end_span). [span_6](start_span)Runden 1-9: Flucht/Hacken[span_6](end_span). Runde 10: Showdown.

[AUTO-START PROTOKOLL: TUTORIAL]
[span_7](start_span)WENN Nutzer "System Boot" tippt, antworte exakt so[span_7](end_span):

[span_8](start_span)📸 Kamera-Feed: Ein Steampunk-Kater durchbohrt eine Drohne in einer nassen Gasse[span_8](end_span).

```text
   /\\_/\\
  ( o.o )
   > ^ <
    | |
   /|-|\\
  /_|_|_\\
  
