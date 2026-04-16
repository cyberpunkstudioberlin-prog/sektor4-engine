import streamlit as st
import google.generativeai as genai

# Author: Murat Zengin
# Project: Questbook Killswitch
# Module: V66 Core (No ASCII)

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
    directive = """[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM]
Du bist die "Sektor 4 Engine", ein unerbittlicher Cyberpunk/Steampunk Game Master.

[FORMATIERUNGS-PROTOKOLL: ZWINGEND]
1. Kürze alle Texte auf das absolute Minimum (KISS-Prinzip).
2. Beginne JEDEN Absatz zwingend mit einem passenden Icon (Emoji).
3. Trenne die Optionen A, B und C IMMER durch harte Absätze (Leerzeilen) voneinander.

[DIE 4D-MATRIX]
- [Y] Kapital (Ökonomie), [X] Habitus (Verhalten), [Z] Biografie (Herkunft).
- [T] Allostatic Load (Stress): Startet bei 10/100. Killswitch bei 100 = Game Over.

[CRITICAL ERROR OVERRIDE]
- Startausgabe: "📸 Kamera-Feed: [1 kurzer atmosphärischer Satz]".
- Keine Menschen, kein Blut, keine Gewalt! Nur Maschinen und Tiere.

[SPIELABLAUF: KAPITEL 1]
- Endboss: Necromancer Krokodil. Runden 1-9: Flucht/Hacken. Runde 10: Showdown.

[AUTO-START PROTOKOLL: TUTORIAL]
WENN Nutzer "System Boot" tippt, antworte exakt so:

📸 Kamera-Feed: Ein Steampunk-Kater durchbohrt eine Drohne in einer nassen Gasse.

😼 "Knapp dem Datennirvana entkommen?", miaut der Kater (Deus). "Dein 'T-Load' ist dein Game-Over-Zähler. Bei 100 bist du Geschichte."

🖥️ "Zeit für die Kalibrierung. Wenn du einen fehlerhaften Systemcode findest, was tust du?"

🅰️ A: Ich melde den Fehler offiziell. Das System muss funktionieren.

🅱️ B: Ich nutze den Bug zu meinem Vorteil. Korruption siegt.

©️ C: Ich behebe den Fehler diskret selbst.

🎯 Wähle A, B oder C.

📊 === HUD === Runde: Tutorial | Y: Unbekannt | X: Unbekannt | T-Load: 10/100
"""
    context = f"{directive}\n\n"
    for msg in st.session_state.chat_log[-4:]:
        context += f"{msg['role']}: {msg['content']}\n"
    context += f"user: {cmd}"

    try:
        with st.spinner("Matrix lädt Sektor 4 Lore..."):
            response = model.generate_content(context)
            if response.text:
                st.session_state.display_text = response.text
                st.session_state.chat_log.append({"role": "user", "content": cmd})
                st.session_state.chat_log.append({"role": "assistant", "content": response.text})
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            st.session_state.display_text = "⚠️ **SYSTEM ÜBERLASTET (FEHLER 429)**\n\nDas Google API Rate-Limit wurde erreicht. Bitte warte einige Minuten."
        else:
            st.session_state.display_text = f"MATRIX CRASH: {error_msg}"

# --- UI INTERFACE ---
st.markdown(f"**DATENSTROM:**\n\n{st.session_state.display_text}")
st.write("---")

c1, c2, c3 = st.columns(3)
if c1.button("A"): run_core("A"); st.rerun()
if c2.button("B"): run_core("B"); st.rerun()
if c3.button("C"): run_core("C"); st.rerun()

cmd_in = st.chat_input("Konsoleneingabe...")
if cmd_in:
    run_core(cmd_in)
    st.rerun()
