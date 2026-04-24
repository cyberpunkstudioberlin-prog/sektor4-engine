import streamlit as st
import google.generativeai as genai
import time
import base64

# --- KONFIGURATION & DESIGN ---
st.set_page_config(page_title="Sektor 4 Engine", layout="wide", initial_sidebar_state="collapsed")

# Projekt-Metadaten: 163154392554
# Autor: Murat Zengin

# CSS für das eiskalte Berlin-Dystopie Design
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #d4d4d8; font-family: 'Courier New', monospace; }
    .terminal-header { color: #eab308; font-weight: bold; border-bottom: 1px solid #3f3f46; padding-bottom: 10px; margin-bottom: 20px; font-size: 1.2em; text-transform: uppercase; letter-spacing: 2px; }
    .kater-log { font-style: italic; color: #a1a1aa; border-left: 2px solid #3f3f46; padding-left: 15px; margin: 20px 0; background: rgba(255,255,255,0.02); padding-top: 10px; padding-bottom: 10px; }
    .hud-container { border: 1px solid #27272a; padding: 15px; background: rgba(10,10,10,0.9); margin-top: 20px; border-left: 4px solid #eab308; }
    .stButton>button { width: 100%; border: 1px solid #3f3f46; background: transparent; color: #d4d4d8; transition: 0.3s; padding: 12px; font-weight: bold; }
    .stButton>button:hover { border-color: #eab308; color: #eab308; background: rgba(234, 179, 8, 0.05); }
    </style>
""", unsafe_allow_html=True)

# API-Key Sicherheit (Lädt aus Streamlit Secrets)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("🚨 API-KEY FEHLT: Bitte in Streamlit Cloud unter Settings -> Secrets 'GEMINI_API_KEY' eintragen.")

# --- KI FUNKTIONEN ---
def call_gemini_text(prompt, system_instruction):
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-preview-09-2025",
            system_instruction=system_instruction
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "📷 KAMERA-FEED: Gestört.\n🕹️ NARRATIV: Die Verbindung zum Sektor ist instabil.\n🐈 KATER-LOG: 'Sogar das System hat Angst vor dem Krokodil.'\n❓ ENTSCHEIDUNG:\nA) Verbindung neu kalibrieren"

def generate_image(prompt):
    try:
        # Nutzung des aktuellen Bild-Modells
        model = genai.GenerativeModel("imagen-3.0-generate-002") 
        response = model.generate_content(prompt)
        if response.candidates[0].content.parts[0].inline_data:
            img_data = response.candidates[0].content.parts[0].inline_data.data
            return f"data:image/png;base64,{base64.b64encode(img_data).decode()}"
    except:
        return "https://via.placeholder.com/450x800.png?text=SEKTOR+4+SIGNAL+LOST"

# --- ENGINE STATE MANAGEMENT ---
if 'round' not in st.session_state:
    st.session_state.update({
        'round': 0, 't_load': 10, 'kapital': None, 'habitus': None,
        'inventory': [], 'last_image': None, 'last_text': None
    })

SYSTEM_PROMPT = """
Rolle: Du bist die Sektor 4 Engine V7.0. Ein eiskaltes Inferenz-System.
Stil: Zynisch, direkt, eiskalt. (KISS-Prinzip)
Urheber: Murat Zengin.
STRIKTES FORMAT:
📷 KAMERA-FEED: [Ort]
🕹️ NARRATIV: [Kurzer Text]
🐈 KATER-LOG: [Kommentar]
❓ ENTSCHEIDUNG: A) [X] | B) [Y] | C) [Z]
"""

def process_step(user_input):
    if st.session_state.round == 0:
        st.session_state.round = 1
        # Habitus-Zuweisung
        if "Konzern" in user_input: st.session_state.kapital, st.session_state.habitus = "Elite", "Anpassung"
        elif "Mechaniker" in user_input: st.session_state.kapital, st.session_state.habitus = "Gasse", "Tradition"
        else: st.session_state.kapital, st.session_state.habitus = "Prekär", "Disruption"
    else:
        st.session_state.round += 1
        # T-Load Logik (Basis-Anstieg)
        st.session_state.t_load = min(100, st.session_state.t_load + 15)

    # Bild-Inferenz Logik basierend auf der Phase
    phase_context = "Industrial Berlin steampunk ruins"
    if 5 <= st.session_state.round <= 7: 
        phase_context = "Massive mechanical Necromancer crocodile merging with Berlin infrastructure"
    elif st.session_state.round >= 8: 
        phase_context = "Digital glitches, reality collapse, binary code artifacts"

    img_prompt = f"Cyberpunk-Steampunk Berlin, 9:16 portrait, {phase_context}, rusty metal, atmospheric, no humans."
    
    with st.spinner("🔄 Inferenz-Engine berechnet nächsten Zyklus..."):
        st.session_state.last_text = call_gemini_text(user_input, SYSTEM_PROMPT)
        st.session_state.last_image = generate_image(img_prompt)

# --- UI RENDERING ---
st.markdown("<div class='terminal-header'>📟 SEKTOR 4 ENGINE // QUESTBOOK KILLSWITCH V7.5</div>", unsafe_allow_html=True)

if st.session_state.t_load >= 100:
    st.error("🚨 SYSTEM FATAL ERROR: T-LOAD LIMIT ÜBERSCHRITTEN. BIO-EINHEIT ZERSTÖRT.")
    if st.button("REBOOT"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
else:
    col_vis, col_term = st.columns([1, 1.2])

    with col_vis:
        if st.session_state.last_image:
            st.image(st.session_state.last_image, use_container_width=True)
        else:
            st.info("Kamera-Feed offline. Starte System für Visual-Inferenz.")

    with col_term:
        if st.session_state.round == 0:
            st.write("Willkommen in Sektor 4. Wähle deine Herkunft:")
            if st.button("A) Konzern-Aussteiger (Elite/Anpassung)"): process_step("Konzern-Aussteiger")
            if st.button("B) Mechaniker der Gosse (Gasse/Tradition)"): process_step("Mechaniker der Gosse")
            if st.button("C) System-Glitch (Prekär/Disruption)"): process_step("System-Glitch")
        else:
            if st.session_state.last_text:
                lines = st.session_state.last_text.split('\n')
                for line in lines:
                    if "📷" in line: st.caption(line)
                    elif "🕹️" in line: st.subheader(line.replace("🕹️", ""))
                    elif "🐈" in line: st.markdown(f"<div class='kater-log'>{line}</div>", unsafe_allow_html=True)
                    elif any(x in line for x in ["A)", "B)", "C)"]):
                        if st.button(line): process_step(line)

            # HUD
            st.markdown("<div class='hud-container'>", unsafe_allow_html=True)
            st.write(f"📉 RUNDE: {st.session_state.round}/10 | KAPITAL: {st.session_state.kapital}")
            t_val = st.session_state.t_load
            bar = "|" * (t_val // 5) + "-" * (20 - (t_val // 5))
            st.code(f"🧠 T-LOAD: [{bar}] {t_val}/100", language="text")
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<p style='text-align: center; color: #3f3f46; font-size: 0.7em; margin-top: 50px;'>Autor: Murat Zengin // Projekt-ID: 163154392554</p>", unsafe_allow_html=True)
