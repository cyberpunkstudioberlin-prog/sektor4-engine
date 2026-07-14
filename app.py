import streamlit as st
import google.generativeai as genai
import random

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Sektor 4 Engine", page_icon="🤖", layout="centered")

# --- 2. CSS ---
st.markdown("""<style>
    .stApp { background-color: #0d0e12; color: #e2e8f0; font-family: 'Courier New', monospace; }
    .hud-container { border: 2px solid #d46a13; background: rgba(20,22,28,0.85); padding: 15px; margin-bottom: 25px; display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
    .narrative-block { line-height: 1.6; padding: 15px; background: rgba(0,0,0,0.4); border-left: 2px solid #4a5568; }
</style>""", unsafe_allow_html=True)

# --- 3. API SETUP ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API Konfigurationsfehler: {e}")
    st.stop()

# --- 4. STATE ---
if "state" not in st.session_state:
    st.session_state.state = {
        "runde": 0, "t_load": 10, "resonanz": 50,
        "kapital": "N/A", "habitus": "N/A",
        "story_log": ["**[SYSTEM BOOT]** Sektor 4 Engine bereit."]
    }
s = st.session_state.state

# --- 5. LOGIK ---
def process_turn(choice):
    s["runde"] += 1
    prompt = f"Runde {s['runde']}. Spieler wählte {choice}. Berechne Story-Fortschritt für Cyberpunk-Setting. Erzähle aus Sicht der Felinen Anomalie. Status: T-Load {s['t_load']}, Resonanz {s['resonanz']}. Bisheriger Log: {s['story_log'][-1]}"
    
    try:
        response = model.generate_content(prompt)
        s["story_log"].append(response.text)
    except Exception as e:
        s["story_log"].append(f"Fehler: {e}")

# --- 6. UI ---
st.title("SEKTOR 4 ENGINE")
hud = f"<div class='hud-container'><div>Runde: {s['runde']}</div><div>T-Load: {s['t_load']}</div></div>"
st.markdown(hud, unsafe_allow_html=True)
st.markdown(f"<div class='narrative-block'>{s['story_log'][-1]}</div>", unsafe_allow_html=True)

if s["runde"] == 0:
    if st.button("A - Disruption"): process_turn("A"); st.rerun()
    if st.button("B - Anpassung"): process_turn("B"); st.rerun()
else:
    if st.button("A - Gewalt"): process_turn("A"); st.rerun()
    if st.button("B - Hacken"): process_turn("B"); st.rerun()
    if st.button("C - Schleichen"): process_turn("C"); st.rerun()
