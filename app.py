import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io
import time

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="Questbook Killswitch // Sektor 4",
    page_icon="🦾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS (TERMINAL-LOOK V28.5) ---
st.markdown("""
<style>
    /* Hintergrund und Haupttext */
    .stApp {
        background-color: #0e1117;
        color: #00ff00;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Terminal-Box für das Narrativ */
    .terminal-box {
        border: 1px solid #10b981;
        padding: 25px;
        background: rgba(0, 255, 0, 0.02);
        border-radius: 4px;
        margin-bottom: 20px;
        box-shadow: inset 0 0 15px rgba(0, 255, 0, 0.05);
        line-height: 1.6;
    }
    
    /* Kater-Log Zitat-Stil */
    .kater-log {
        border-left: 2px solid #059669;
        padding-left: 15px;
        font-style: italic;
        color: #10b981;
        margin-top: 20px;
        font-size: 0.95rem;
    }

    /* HUD Styling */
    .hud-box {
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid #065f46;
        padding: 10px;
        text-align: center;
        border-radius: 2px;
    }
    .hud-label { color: #065f46; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; }
    .hud-value { font-weight: bold; color: #00ff00; font-size: 1rem; }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background-color: rgba(0, 255, 0, 0.05);
        color: #00ff00;
        border: 1px solid #065f46;
        text-align: left;
        padding: 15px;
        transition: 0.2s;
        border-radius: 2px;
    }
    .stButton>button:hover {
        background-color: #00ff00;
        color: #000;
        border-color: #00ff00;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
    }
    
    /* Scanline Effekt */
    .stApp::before {
        content: " ";
        display: block;
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.02));
        z-index: 9999;
        background-size: 100% 4px, 3px 100%;
        pointer-events: none;
        opacity: 0.2;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API SETUP & ENGINE CONFIG ---
# WICHTIG: Key in Streamlit Secrets unter "GOOGLE_API_KEY" speichern
API_KEY = st.secrets.get("GOOGLE_API_KEY", "")

if not API_KEY:
    st.error("⚠️ API-Key fehlt! Bitte 'GOOGLE_API_KEY' in den Streamlit Cloud Secrets hinterlegen.")
    st.stop()

genai.configure(api_key=API_KEY)

# Engine System Instruction
SYSTEM_PROMPT = """Du bist die Sektor 4 Engine [V28.5]. 
DIREKTIVE: Die immersive Geschichte hat höchste Priorität.
STRIKTE REGELN:
1. Narrativ: 3-4 Sätze, reine Story, keine Meta-Begriffe (Level, Option, etc.).
2. Icons: Nutze Trenn-Icons (🧬, 🕹️, ⚙️, 🐈) in Leerzeilen zwischen Absätzen.
3. Kater-Log: Ein zynischer Kommentar der "Felinen Anomalie".
4. Entscheidungen: Generiere 4 Optionen (A, B, C, D). D ist IMMER "Scavenger-Protokoll".
Formatierung: Gib NUR valides JSON zurück. 
Schema: { "kameraFeed": string, "narrativ": string, "katerLog": string, "optionen": [{ "id": "A"|"B"|"C"|"D", "titel": string, "beschreibung": string, "stress": string, "loot": string }] }"""

# --- 4. SESSION STATE INITIALISIERUNG ---
if 'round' not in st.session_state:
    st.session_state.round = 0
    st.session_state.t_load = 10
    st.session_state.loot = 0
    st.session_state.kapital = "Defining..."
    st.session_state.habitus = "Defining..."
    st.session_state.current_turn = None
    st.session_state.last_action = "System Boot"

# --- 5. LOGIK-FUNKTIONEN ---
def run_engine(prompt, uploaded_image=None):
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-preview-09-2025",
        system_instruction=SYSTEM_PROMPT
    )
    
    contents = [prompt]
    if uploaded_image:
        contents.append(uploaded_image)
    
    # Exponential Backoff für API Calls
    for delay in [1, 2, 4]:
        try:
            response = model.generate_content(contents, generation_config={"response_mime_type": "application/json"})
            st.session_state.current_turn = json.loads(response.text)
            return
        except Exception as e:
            time.sleep(delay)
    
    st.error("Engine-Fehler: Verbindung zu Sektor 4 unterbrochen.")

def handle_choice(idx):
    choice = st.session_state.current_turn['optionen'][idx]
    st.session_state.last_action = choice['titel']
    
    # Stress-Mechanik
    stress_gain = 20 if choice['id'] == 'D' else 5
    st.session_state.t_load = min(100, st.session_state.t_load + stress_gain)
    
    # Loot-Logik
    if choice['id'] == 'D':
        st.session_state.loot += 1
        if st.session_state.loot >= 3:
            st.session_state.loot = 0
            ranks = ["Prekär", "Gasse", "Terminal-Access", "Elite"]
            current_idx = ranks.index(st.session_state.kapital) if st.session_state.kapital in ranks else 0
            st.session_state.kapital = ranks[min(len(ranks)-1, current_idx + 1)]
            
    # Initialisierung in Runde 0
    if st.session_state.round == 0:
        if choice['id'] == 'A': st.session_state.habitus, st.session_state.kapital = "Anpassung", "Prekär"
        elif choice['id'] == 'B': st.session_state.habitus, st.session_state.kapital = "Disruption", "Terminal-Access"
        elif choice['id'] == 'C': st.session_state.habitus, st.session_state.kapital = "Tradition", "Gasse"

    st.session_state.round += 1
    
    # Nächsten Zug generieren
    next_prompt = f"Runde: {st.session_state.round}. Aktion: {choice['titel']}. Status: Stress {st.session_state.t_load}%, Loot {st.session_state.loot}/3, Kapital {st.session_state.kapital}. Phase: {'Jagd' if st.session_state.round < 5 else 'Eskalation'}."
    run_engine(next_prompt)

# --- 6. UI AUFBAU ---
st.title("SEKTOR 4 ENGINE // V28.5")

# Sidebar: Scanner-Modul
with st.sidebar:
    st.header("⚙️ Scanner-Modul")
    uploaded_file = st.file_uploader("Bild zur Analyse hochladen...", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        img_preview = Image.open(uploaded_file)
        st.image(img_preview, caption="Analysiere Scan...", width=300)

# Start / Spiel-Logic
if st.session_state.round == 0 and st.session_state.current_turn is None:
    if st.button("INITIALISIERE SYSTEM (START)", use_container_width=True):
        img_input = Image.open(uploaded_file) if uploaded_file else None
        run_engine("START: Initialisierung. Phase 0. Biografie-Wahl.", img_input)
        st.rerun()

if st.session_state.current_turn:
    turn = st.session_state.current_turn
    
    # Kamera Feed Info
    st.caption(f"📷 {turn['kameraFeed']}")
    
    # Haupt-Narrativ
    st.markdown(f"""
    <div class="terminal-box">
        {turn['narrativ']}
        <div class="kater-log">
            <strong>🐈 Feline Anomalie:</strong><br>
            „{turn['katerLog']}“
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Optionen
    for i, opt in enumerate(turn['optionen']):
        if st.button(f"**{opt['id']}) {opt['titel']}**\n\n{opt['beschreibung']}\n\n[Stress: {opt['stress']} | Loot: {opt['loot']}]", key=f"opt_{i}"):
            handle_choice(i)
            st.rerun()

# --- 7. HUD (FOOTER) ---
st.markdown("---")
h_col1, h_col2, h_col3, h_col4 = st.columns(4)

with h_col1:
    st.markdown(f"<div class='hud-box'><div class='hud-label'>Habitus</div><div class='hud-value'>{st.session_state.habitus}</div></div>", unsafe_allow_html=True)
with h_col2:
    st.markdown(f"<div class='hud-box'><div class='hud-label'>Kapital</div><div class='hud-value'>{st.session_state.kapital}</div></div>", unsafe_allow_html=True)
with h_col3:
    st.markdown(f"<div class='hud-box'><div class='hud-label'>Loot</div><div class='hud-value'>{st.session_state.loot}/3</div></div>", unsafe_allow_html=True)
with h_col4:
    st.markdown(f"<div class='hud-box'><div class='hud-label'>Runde</div><div class='hud-value'>{st.session_state.round}/10</div></div>", unsafe_allow_html=True)

st.write(f"🧠 T-LOAD (STRESS): {st.session_state.t_load}%")
st.progress(st.session_state.t_load / 100)

if st.button("System Reset"):
    st.session_state.clear()
    st.rerun()
