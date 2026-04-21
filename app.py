import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import time

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="Questbook Killswitch // Sektor 4",
    page_icon="🦾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. ERWEITERTES CUSTOM CSS (TERMINAL-LOOK V30) ---
st.markdown("""
<style>
    /* Grundlegendes Design */
    .stApp {
        background-color: #0a0c10;
        color: #00ff41;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Terminal-Box für Story-Inhalte */
    .terminal-box {
        border: 1px solid #10b981;
        padding: 25px;
        background: rgba(0, 255, 65, 0.02);
        border-radius: 4px;
        margin-bottom: 20px;
        box-shadow: inset 0 0 20px rgba(0, 255, 65, 0.05);
        line-height: 1.6;
    }
    
    /* Kater-Log (Zitat-Stil) */
    .kater-log {
        border-left: 3px solid #059669;
        padding-left: 15px;
        font-style: italic;
        color: #10b981;
        margin-top: 20px;
        font-size: 0.95rem;
    }

    /* HUD (Stats-Leiste) */
    .hud-box {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #065f46;
        padding: 12px;
        text-align: center;
        border-radius: 4px;
    }
    .hud-label { 
        color: #065f46; 
        font-size: 0.7rem; 
        text-transform: uppercase; 
        letter-spacing: 2px;
        display: block;
        margin-bottom: 4px;
    }
    .hud-value { 
        font-weight: bold; 
        color: #00ff41; 
        font-size: 1rem;
        display: block;
    }
    
    /* Interaktive Buttons */
    .stButton>button {
        width: 100%;
        background-color: rgba(0, 255, 65, 0.05) !important;
        color: #00ff41 !important;
        border: 1px solid #065f46 !important;
        text-align: left !important;
        padding: 18px !important;
        transition: 0.3s !important;
        border-radius: 4px !important;
    }
    .stButton>button:hover {
        background-color: #00ff41 !important;
        color: #000 !important;
        border-color: #00ff41 !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3) !important;
    }

    /* Scanline-Effekt (Overlay) */
    .stApp::after {
        content: " ";
        display: block;
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.02));
        z-index: 9999;
        background-size: 100% 4px, 3px 100%;
        pointer-events: none;
        opacity: 0.15;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API INITIALISIERUNG ---
# WICHTIG: Key in Streamlit Secrets unter "GOOGLE_API_KEY" speichern
API_KEY = st.secrets.get("GOOGLE_API_KEY", "")

if not API_KEY:
    st.error("⚠️ API-KEY NICHT GEFUNDEN! Bitte 'GOOGLE_API_KEY' in den Streamlit Cloud Secrets (Settings) hinterlegen.")
    st.stop()

genai.configure(api_key=API_KEY)

# Konfiguration der Engine
SYSTEM_PROMPT = """Du bist die Sektor 4 Engine [V30.0]. 
DIREKTIVE: Die immersive Geschichte hat höchste Priorität.
STRIKTE REGELN:
1. Narrativ: 3-4 Sätze, pure Geschichte, keine Meta-Begriffe wie "Level" oder "Option".
2. Icons: Nutze Trenn-Icons (🧬, 🕹️, ⚙️, 🐈) in Leerzeilen zwischen Absätzen.
3. Kater-Log: Ein zynischer Kommentar der "Felinen Anomalie".
4. Entscheidungen: Generiere exakt 4 Optionen (A, B, C, D). D ist IMMER "Scavenger-Protokoll".
5. Visualisierung: Erstelle einen englischen Bild-Prompt (9:16 portrait).
Formatierung: Gib NUR valides JSON zurück. 
Schema: { "kameraFeed": string, "narrativ": string, "katerLog": string, "visualPrompt": string, "optionen": [{ "id": "A"|"B"|"C"|"D", "titel": string, "beschreibung": string, "stress": string, "loot": string }] }"""

# --- 4. SESSION STATE MANAGEMENT ---
if 'round' not in st.session_state:
    st.session_state.update({
        'round': 0,
        't_load': 10,
        'loot': 0,
        'kapital': "Defining...",
        'habitus': "Defining...",
        'current_turn': None,
        'current_image': None
    })

# --- 5. CORE LOGIC ---
def run_engine(prompt, uploaded_image=None):
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-preview-09-2025", # Das von dir gewählte Modell
        system_instruction=SYSTEM_PROMPT
    )
    
    contents = [prompt]
    if uploaded_image:
        contents.append(uploaded_image)
    
    try:
        # 1. Narrativ & Spiel-Logik generieren
        response = model.generate_content(contents, generation_config={"response_mime_type": "application/json"})
        data = json.loads(response.text)
        st.session_state.current_turn = data
        
        # 2. Visualisierung generieren (Imagen)
        try:
            img_model = genai.get_model("models/imagen-4.0-generate-001")
            img_resp = img_model.predict(
                instances={"prompt": f"9:16 portrait. Cinematic cyberpunk. {data['visualPrompt']}. Neon cyan and copper, industrial grit."},
                parameters={"sampleCount": 1}
            )
            st.session_state.current_image = img_resp.predictions[0].bytesBase64Encoded
        except:
            st.session_state.current_image = None
    except Exception as e:
        st.error(f"Engine-Error: {e}")

def handle_choice(idx):
    choice = st.session_state.current_turn['optionen'][idx]
    
    # Stress (T-Load)
    stress_gain = 20 if choice['id'] == 'D' else 5
    st.session_state.t_load = min(100, st.session_state.t_load + stress_gain)
    
    # Loot-Logik (Y-Kapital Upgrade bei 3/3)
    if choice['id'] == 'D':
        st.session_state.loot += 1
        if st.session_state.loot >= 3:
            st.session_state.loot = 0
            ranks = ["Prekär", "Gasse", "Terminal-Access", "Elite"]
            current_idx = ranks.index(st.session_state.kapital) if st.session_state.kapital in ranks else 0
            st.session_state.kapital = ranks[min(len(ranks)-1, current_idx + 1)]
            
    # Initial-Habitus in Runde 0
    if st.session_state.round == 0:
        h_map = {"A": "Anpassung", "B": "Disruption", "C": "Tradition"}
        k_map = {"A": "Prekär", "B": "Terminal-Access", "C": "Gasse"}
        st.session_state.habitus = h_map.get(choice['id'], "Anpassung")
        st.session_state.kapital = k_map.get(choice['id'], "Prekär")

    st.session_state.round += 1
    
    # Nächsten Turn laden
    next_prompt = f"Runde: {st.session_state.round}. Letzte Aktion: {choice['titel']}. Status: Stress {st.session_state.t_load}%, Kapital {st.session_state.kapital}. Phase: {'Jagd' if st.session_state.round < 5 else 'Eskalation'}."
    run_engine(next_prompt)

# --- 6. UI AUFBAU ---
st.title("SEKTOR 4 ENGINE // V30.0")

# SIDEBAR: SCANNER
with st.sidebar:
    st.header("⚙️ Scanner-Modul")
    uploaded_file = st.file_uploader("Bild zur Analyse hochladen...", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(Image.open(uploaded_file), caption="Analysiere Scan...", width=None)

# START-LOGIK
if st.session_state.round == 0 and st.session_state.current_turn is None:
    if st.button("INITIALISIERE SYSTEM (START)", use_container_width=True):
        img_in = Image.open(uploaded_file) if uploaded_file else None
        run_engine("START: Initialisierung. Phase 0. Biografie-Wahl.", img_in)
        st.rerun()

# SPIEL-INTERFACE
if st.session_state.current_turn:
    turn = st.session_state.current_turn
    
    # 1. Visualisierung (9:16)
    if st.session_state.current_image:
        st.image(f"data:image/png;base64,{st.session_state.current_image}", width="stretch")
    
    # 2. Kamera-Feed
    st.caption(f"📷 {turn['kameraFeed']}")
    
    # 3. Narrativ & Kater-Log
    st.markdown(f"""
    <div class="terminal-box">
        {turn['narrativ']}
        <div class="kater-log">
            <strong>🐈 Feline Anomalie:</strong><br>
            „{turn['katerLog']}“
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 4. Entscheidungs-Buttons
    for i, opt in enumerate(turn['optionen']):
        btn_text = f"**{opt['id']}) {opt['titel']}**\n\n{opt['beschreibung']}\n\n[Stress: {opt['stress']} | Loot: {opt['loot']}]"
        if st.button(btn_text, key=f"choice_{i}", use_container_width=True):
            handle_choice(i)
            st.rerun()

# --- 7. HUD (FOOTER) ---
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"<div class='hud-box'><span class='hud-label'>Habitus</span><span class='hud-value'>{st.session_state.habitus}</span></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='hud-box'><span class='hud-label'>Kapital</span><span class='hud-value'>{st.session_state.kapital}</span></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='hud-box'><span class='hud-label'>Loot</span><span class='hud-value'>{st.session_state.loot}/3</span></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='hud-box'><span class='hud-label'>Runde</span><span class='hud-value'>{st.session_state.round}/10</span></div>", unsafe_allow_html=True)

# T-Load Bar
st.write(f"🧠 T-LOAD (STRESS): {st.session_state.t_load}%")
st.progress(st.session_state.t_load / 100)

if st.button("System Reset", type="secondary", use_container_width=True):
    st.session_state.clear()
    st.rerun()
