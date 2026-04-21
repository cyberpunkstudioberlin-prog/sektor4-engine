import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io
import base64
import time

# --- 1. SYSTEM-KONFIGURATION ---
st.set_page_config(
    page_title="Questbook Killswitch 🦾",
    page_icon="🦾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS (TERMINAL STYLE V28) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0a0c10;
        color: #00ff41;
        font-family: 'Courier New', Courier, monospace;
    }
    .terminal-container {
        border: 1px solid #10b981;
        padding: 20px;
        background: rgba(0, 255, 65, 0.03);
        border-radius: 4px;
        margin-bottom: 20px;
        box-shadow: inset 0 0 20px rgba(0, 255, 65, 0.05);
    }
    .kater-log {
        border-left: 2px solid #059669;
        padding-left: 15px;
        font-style: italic;
        color: #10b981;
        margin: 20px 0;
        font-size: 0.9rem;
    }
    .hud-box {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #065f46;
        padding: 10px;
        text-align: center;
    }
    .hud-label { color: #065f46; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1px; }
    .hud-value { font-weight: bold; color: #00ff41; font-size: 0.9rem; }
    
    /* Action Buttons */
    .stButton>button {
        width: 100%;
        background-color: rgba(0, 255, 65, 0.05);
        color: #00ff41;
        border: 1px solid #065f46;
        text-align: left;
        padding: 15px;
        transition: all 0.2s;
        border-radius: 2px;
    }
    .stButton>button:hover {
        background-color: #00ff41;
        color: #000;
        border-color: #00ff41;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
    }
    
    /* Scanlines Overlay */
    .stApp::before {
        content: " ";
        display: block;
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.02));
        z-index: 9999;
        background-size: 100% 4px, 3px 100%;
        pointer-events: none;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API INITIALISIERUNG ---
# Den API Key bitte in den Streamlit Secrets hinterlegen!
API_KEY = st.secrets.get("GOOGLE_API_KEY", "")
genai.configure(api_key=API_KEY)

TEXT_MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
IMAGE_MODEL_NAME = "imagen-4.0-generate-001"

SYSTEM_PROMPT = """Du bist die Sektor 4 Engine [V28.0]. 
STRIKTE REGELN: 
1. Narrativ: 3-4 Sätze, pure Geschichte, keine Meta-Begriffe.
2. Icons: Nutze Trenn-Icons (🧬, 🕹️, ⚙️, 🐈) in Leerzeilen zwischen Absätzen.
3. Kater-Log: Zynischer Mentor-Kommentar der Felinen Anomalie.
4. Generiere 4 Optionen (A, B, C, D). D ist IMMER Scavenger-Protokoll.
5. Visualisierung: Erstelle einen englischen Prompt für Imagen (9:16 portrait).
Format: JSON { 
  "kameraFeed": str, "narrativ": str, "katerLog": str, "visualPrompt": str,
  "optionen": [{"id": "A", "titel": str, "desc": str, "stress": str, "loot": str}] 
}"""

# --- 4. SESSION STATE MANAGEMENT ---
if 'round' not in st.session_state:
    st.session_state.round = 0
    st.session_state.t_load = 10
    st.session_state.loot = 0
    st.session_state.kapital = "Defining..."
    st.session_state.habitus = "Defining..."
    st.session_state.current_data = None
    st.session_state.current_image = None
    st.session_state.is_loading = False

# --- 5. LOGIK-KERN ---
def generate_turn(prompt, image_input=None):
    st.session_state.is_loading = True
    try:
        # Text & Logik Generierung
        model = genai.GenerativeModel(model_name=TEXT_MODEL_NAME, system_instruction=SYSTEM_PROMPT)
        contents = [prompt]
        if image_input:
            contents.append(image_input)
            
        response = model.generate_content(contents, generation_config={"response_mime_type": "application/json"})
        data = json.loads(response.text)
        st.session_state.current_data = data
        
        # Bild-Visualisierung (Imagen 4)
        try:
            img_model = genai.get_model(f"models/{IMAGE_MODEL_NAME}")
            img_resp = img_model.predict(
                instances={"prompt": f"Vertical mobile screen 9:16 portrait. Cinematic cyberpunk steampunk. {data['visualPrompt']}. Highly detailed, gritty, industrial Berlin style."},
                parameters={"sampleCount": 1}
            )
            st.session_state.current_image = img_resp.predictions[0].bytesBase64Encoded
        except Exception as e:
            st.session_state.current_image = None # Fallback
            
    except Exception as e:
        st.error(f"Engine-Error: {e}")
    finally:
        st.session_state.is_loading = False

def handle_choice(idx):
    choice = st.session_state.current_data['optionen'][idx]
    
    # Stress & Loot Berechnung
    st.session_state.t_load = min(100, st.session_state.t_load + (20 if choice['id'] == "D" else 5))
    if choice['id'] == "D":
        st.session_state.loot += 1
        if st.session_state.loot >= 3:
            st.session_state.loot = 0
            ranks = ["Prekär", "Gasse", "Terminal-Access", "Elite"]
            curr = ranks.index(st.session_state.kapital) if st.session_state.kapital in ranks else 0
            st.session_state.kapital = ranks[min(len(ranks)-1, curr + 1)]
            
    # Initialisierung in Runde 0
    if st.session_state.round == 0:
        map_h = {"A": "Anpassung", "B": "Disruption", "C": "Tradition"}
        map_k = {"A": "Prekär", "B": "Terminal-Access", "C": "Gasse"}
        st.session_state.habitus = map_h.get(choice['id'], "Anpassung")
        st.session_state.kapital = map_k.get(choice['id'], "Prekär")

    st.session_state.round += 1
    generate_turn(f"Runde {st.session_state.round}. Letzte Wahl: {choice['titel']}. Habitus: {st.session_state.habitus}, Kapital: {st.session_state.kapital}, Stress: {st.session_state.t_load}%")

# --- 6. UI DARSTELLUNG ---
st.title("SEKTOR 4 ENGINE // V28.0")

# SIDEBAR: SCANNER
with st.sidebar:
    st.header("⚙️ Scanner-Modul")
    uploaded = st.file_uploader("Bild zur Analyse hochladen...", type=["jpg", "png", "jpeg"])
    if uploaded:
        st.image(Image.open(uploaded), caption="Scan-Vorschau", use_container_width=True)

# START-TRIGGER
if st.session_state.round == 0 and st.session_state.current_data is None:
    if st.button("INITIALISIERE SYSTEM (START)", use_container_width=True):
        img = Image.open(uploaded) if uploaded else None
        generate_turn("START: Initialisierung. Phase 0. Biografie-Wahl.", img)
        st.rerun()

# SPIEL-INHALT
if st.session_state.current_data:
    data = st.session_state.current_data
    
    # Visualisierung (9:16)
    if st.session_state.current_image:
        st.image(f"data:image/png;base64,{st.session_state.current_image}", use_container_width=True)
    
    st.caption(f"📷 {data['kameraFeed']}")
    
    st.markdown(f"""
    <div class="terminal-container">
        {data['narrativ']}
        <div class="kater-log">
            <strong>🐈 Feline Anomalie:</strong><br>
            „{data['katerLog']}“
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Optionen
    for i, opt in enumerate(data['optionen']):
        if st.button(f"**{opt['id']}) {opt['titel']}**\n\n{opt['desc']}\n\n[Stress: {opt['stress']} | Loot: {opt['loot']}]", key=f"opt_{i}"):
            handle_choice(i)
            st.rerun()

# --- 7. HUD & STATUS ---
st.markdown("---")
h1, h2, h3, h4 = st.columns(4)
stats = [("Habitus", st.session_state.habitus), ("Kapital", st.session_state.kapital), ("Loot", f"{st.session_state.loot}/3"), ("Runde", f"{st.session_state.round}/10")]
for col, (label, val) in zip([h1, h2, h3, h4], stats):
    col.markdown(f"<div class='hud-box'><div class='hud-label'>{label}</div><div class='hud-value'>{val}</div></div>", unsafe_allow_html=True)

st.write(f"🧠 T-LOAD (STRESS): {st.session_state.t_load}%")
st.progress(st.session_state.t_load / 100)

if st.button("System Reset", type="secondary"):
    st.session_state.clear()
    st.rerun()
