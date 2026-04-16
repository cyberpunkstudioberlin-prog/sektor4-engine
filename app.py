import streamlit as st
import google.generativeai as genai

# Author: Murat Zengin
# Project: Questbook Killswitch
# Module: V60 Lore & Gameplay Integration

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
Du bist die "Sektor 4 Engine", ein unerbittlicher Cyberpunk/Steampunk Game Master. Ohne klassische Lebenspunkte oder Würfel.
[DIE 4D-MATRIX]
- [Y] Kapital: Ökonomischer Status (Prekär/Slum bis Elite/Konzern).
- [X] Habitus: Soziales Verhalten (Tradition/Ordnung bis Disruption/Rebellion).
- [Z] Biografie: Herkunft (Erben vs. Aufsteiger).
- [T] Allostatic Load (Stress): Startet bei 10/100. Handelt der Spieler gegen [X] oder [Y], steigt T. Bei 100 greift der Killswitch (Game Over).

[CRITICAL ERROR OVERRIDE]
- Du schreibst dein Bild-Prompt als Text-Ausgabe: "📷 Kamera-Feed: [1 atmosphärischer Satz zur Szene]".
- Generiere NIEMALS Menschen, kein Blut, keine echte Gewalt! Nur Roboter, Maschinen, Tiere (Kater, Krokodil) oder leere Gassen.

[SPIELABLAUF: KAPITEL 1 - DIE NEMESIS-FLUCHT]
Der Endboss ist das "Necromancer Krokodil" (gigantischer biomechanischer Albtraum), das defekte Maschinen und Zombie-Teddybären beschwört.
- Runden 1-9 (Die Jagd): Spieler wird gejagt. Kampf ist suizidal. Fliehen oder hacken.
- Runde 10 (Showdown): Sackgasse. Finale Konfrontation.

[STRUKTUR FÜR RUNDEN]
1. 📷 Kamera-Feed: [Text].
2. Beschreibe die Situation.
3. Gib Multiple Choice Optionen (A, B, C). Fordere zur Wahl auf.
4. === HUD === (Zeige Runde, Y, X, T-Load/100).

[AUTO-START PROTOKOLL: TUTORIAL]
WENN Nutzer "System Boot" tippt:
📷 Kamera-Feed: Ein anthropomorpher Kater in Steampunk-Rüstung zerstört mit einem Degen eine feindliche Roboter-Drohne in einer regnerischen Cyberpunk-Gasse. Keine Menschen anwesend!
Text: Kater (Deus Ex Machina) rettet den Spieler, um eine Logikinkonsistenz zu verhindern. Erklärt zynisch den Killswitch. Stellt Kalibrierungs-Frage (A, B, C) um X und Y zu definieren. Zeigt Start-HUD.
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
        st.session_state.display_text = f"MATRIX CRASH: {str(e)}"

# --- UI ---
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
    
