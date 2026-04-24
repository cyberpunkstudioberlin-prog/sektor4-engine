import streamlit as st
import requests
import time
import base64
import json

# --- KONFIGURATION & METADATEN ---
API_KEY = "AIzaSyDbM0C98SJ0018OFfg0-QYlB7gr-UY-BJw"
PROJECT_ID = "163154392554"
MODEL_TEXT = "gemini-2.5-flash-preview-09-2025"
MODEL_IMAGE = "imagen-4.0-generate-001"

st.set_page_config(
    page_title="Sektor 4 Engine: Questbook Killswitch",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS: BERLIN-DYSTOPIA TERMINAL LOOK ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

    .stApp {{
        background-color: #050505;
        color: #d4d4d8;
        font-family: 'JetBrains Mono', monospace;
    }}
    
    .terminal-header {{
        color: #eab308;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        border-bottom: 1px solid #3f3f46;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }}

    .kater-log {{
        border-left: 3px solid #eab308;
        padding: 10px 20px;
        background: rgba(234, 179, 8, 0.05);
        font-style: italic;
        color: #a1a1aa;
        margin: 20px 0;
    }}

    .hud-container {{
        background: rgba(20, 20, 20, 0.9);
        border: 1px solid #27272a;
        padding: 15px;
        border-radius: 5px;
        margin-top: 20px;
    }}

    .stButton>button {{
        width: 100%;
        background-color: rgba(20, 20, 20, 0.5);
        border: 1px solid #3f3f46;
        color: #d4d4d8;
        text-align: left;
        padding: 15px;
        transition: 0.3s;
    }}

    .stButton>button:hover {{
        border-color: #eab308;
        color: #eab308;
        background-color: rgba(234, 179, 8, 0.1);
    }}
    
    .image-container {{
        border: 1px solid #27272a;
        border-radius: 10px;
        overflow: hidden;
    }}
    </style>
""", unsafe_allow_html=True)

# --- API INTEGRATION MIT EXPONENTIAL BACKOFF ---
def call_gemini_text(prompt, system_instruction):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_TEXT}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    
    for i in range(5):
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            time.sleep(2**i)
    return "SYSTEM ERROR: Inferenz-Fehlgeschlagen."

def generate_image(prompt_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_IMAGE}:predict?key={API_KEY}"
    payload = {
        "instances": {"prompt": prompt_text},
        "parameters": {"sampleCount": 1}
    }
    
    for i in range(5):
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                img_data = result['predictions'][0]['bytesBase64Encoded']
                return f"data:image/png;base64,{img_data}"
        except Exception:
            time.sleep(2**i)
    return None

# --- ENGINE STATE MANAGEMENT ---
if 'round' not in st.session_state:
    st.session_state.update({
        'round': 0,
        't_load': 10,
        'kapital': None,
        'habitus': None,
        'inventory': [],
        'history': [],
        'last_image': None,
        'last_text': None,
        'game_over': False
    })

SYSTEM_PROMPT = """
Rolle: Du bist die Sektor 4 Engine V7.0. Ein eiskaltes, analytisches Inferenz-System.
Stil: Zynisch, direkt, eiskalt. (KISS-Prinzip)
Urheber: Murat Zengin.

STRIKTES AUSGABEFORMAT:
📷 KAMERA-FEED: [Ein technischer Status-Satz zum Ort]
🕹️ NARRATIV: [Max. 2 kurze Sätze. Aggressiver Zeitdruck.]
🐈 KATER-LOG: [Ein bissiger Satz der Felinen Anomalie mit mechanischem Hinweis.]
❓ ENTSCHEIDUNG:
A) [Option] (Fokus: [Kapital/Habitus])
B) [Option] (Fokus: [Kapital/Habitus])
C) [Option] (Fokus: [Kapital/Habitus])

LOGIK-MATRIX:
- T-Load: Resonanz -10, Dissonanz +20.
- Phase 2 (R5-7): Schrott-Gott/Krokodil. +5 T-Load fix pro Runde.
- Phase 3 (R8-10): Matrix-Kollaps. Realität zerfällt in Binärcode.
- Killswitch: Bei T-Load 100 ist Ende.
"""

# --- GAME LOGIK ---
def process_step(user_input):
    if st.session_state.round == 0:
        # Initialisierung
        st.session_state.round = 1
        prompt = f"SYSTEM BOOT. Der Spieler wählt: {user_input}"
    else:
        # T-Load Berechnung (Vereinfachte Logik für Prompt-Input)
        st.session_state.round += 1
        st.session_state.t_load += 15 # Basis-Anstieg, wird durch Prompt-Inferenz verfeinert

    # Image Prompt Engineering
    phase_context = ""
    if 5 <= st.session_state.round <= 7:
        phase_context = "Massive mechanical crocodile Necromancer merging with Berlin subway tunnels, metal absorption."
    elif st.session_state.round >= 8:
        phase_context = "Matrix collapse, digital glitches, binary code artifacts, reality tearing apart."
    else:
        phase_context = "Industrial Berlin steampunk ruins, mechanical rats, rusty pipes."

    img_prompt = f"Cyberpunk-Steampunk Berlin vibe, 9:16 portrait, {phase_context}, hyper-detailed, no humans."
    
    with st.spinner("🔄 Inferenz-Engine berechnet nächsten Zyklus..."):
        st.session_state.last_text = call_gemini_text(user_input, SYSTEM_PROMPT)
        st.session_state.last_image = generate_image(img_prompt)

# --- UI RENDERING ---
st.markdown("<div class='terminal-header'>📟 SEKTOR 4 ENGINE // QUESTBOOK KILLSWITCH V7.5</div>", unsafe_allow_html=True)

if st.session_state.t_load >= 100:
    st.error("🚨 SYSTEM FATAL ERROR: T-LOAD LIMIT ÜBERSCHRITTEN. BIO-EINHEIT ZERSTÖRT.")
    if st.button("SYSTEM NEUSTART"):
        for key in st.session_state.keys(): del st.session_state[key]
        st.rerun()
else:
    col_vis, col_term = st.columns([1, 1.2])

    with col_vis:
        if st.session_state.last_image:
            st.markdown(f"<div class='image-container'><img src='{st.session_state.last_image}' style='width:100%'></div>", unsafe_allow_html=True)
        else:
            st.info("Kamera-Feed offline. Starte System für Visual-Inferenz.")

    with col_term:
        if st.session_state.round == 0:
            st.write("Willkommen in Sektor 4. Wähle deine Herkunft, um die Simulation zu starten.")
            if st.button("A) Konzern-Aussteiger (Fokus: Elite/Anpassung)"): process_step("Konzern-Aussteiger")
            if st.button("B) Mechaniker der Gosse (Fokus: Gasse/Tradition)"): process_step("Mechaniker der Gosse")
            if st.button("C) System-Glitch (Fokus: Prekär/Disruption)"): process_step("System-Glitch")
        else:
            # Parse Gemini Output
            lines = st.session_state.last_text.split('\n')
            for line in lines:
                if "📷" in line: st.write(f"**{line}**")
                elif "🕹️" in line: st.subheader(line.replace("🕹️", ""))
                elif "🐈" in line: st.markdown(f"<div class='kater-log'>{line}</div>", unsafe_allow_html=True)
                elif "A)" in line or "B)" in line or "C)" in line:
                    if st.button(line): process_step(line)

            # HUD
            st.markdown("<div class='hud-container'>", unsafe_allow_html=True)
            st.write(f"📉 RUNDE: {st.session_state.round}/10 | T-LOAD: {st.session_state.t_load}/100")
            
            # Progress Bar
            t_val = st.session_state.t_load
            bar = "|" * (t_val // 5) + "-" * (20 - (t_val // 5))
            st.code(f"🧠 STRESS-LEVEL: [{bar}]", language="text")
            st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<p style='text-align: center; color: #3f3f46; font-size: 0.7em; margin-top: 50px;'>Autor der Open Source Akte: Murat Zengin // Projekt-ID: 163154392554</p>", unsafe_allow_html=True)
