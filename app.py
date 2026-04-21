import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io
import base64

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="Questbook Killswitch 🦾",
    page_icon="🦾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS (TERMINAL STYLE V28.5) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #00ff00;
        font-family: 'Courier New', Courier, monospace;
    }
    .terminal-box {
        border: 1px solid #10b981;
        padding: 20px;
        background: rgba(0, 255, 0, 0.05);
        border-radius: 4px;
        margin-bottom: 20px;
        box-shadow: inset 0 0 20px rgba(0, 255, 0, 0.05);
    }
    .kater-log {
        border-left: 3px solid #059669;
        padding-left: 15px;
        font-style: italic;
        color: #10b981;
        margin: 15px 0;
        font-size: 0.9rem;
    }
    .hud-label {
        color: #065f46;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .hud-value {
        font-weight: bold;
        color: #10b981;
        font-size: 1rem;
    }
    /* Button Styling */
    .stButton>button {
        width: 100%;
        background-color: rgba(0, 255, 0, 0.1);
        color: #00ff00;
        border: 1px solid #065f46;
        text-align: left;
        padding: 15px;
        transition: 0.3s;
        border-radius: 2px;
    }
    .stButton>button:hover {
        background-color: #00ff00;
        color: #000;
        border-color: #00ff00;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
    }
    /* Scanlines */
    .stApp::before {
        content: " ";
        display: block;
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.02));
        z-index: 9999;
        background-size: 100% 4px, 3px 100%;
        pointer-events: none;
        opacity: 0.3;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API INITIALISIERUNG ---
# API Key muss in den Streamlit Cloud Secrets als GOOGLE_API_KEY hinterlegt sein
API_KEY = st.secrets.get("GOOGLE_API_KEY", "")
genai.configure(api_key=API_KEY)

TEXT_MODEL = "gemini-2.5-flash-preview-09-2025"
IMAGE_MODEL = "imagen-4.0-generate-001"

SYSTEM_INSTRUCTION = """Du bist die Sektor 4 Engine [V28.5]. 
STRIKTE REGELN: 
1. Kein Smalltalk. 
2. Narrativ: 3-4 Sätze, pure Geschichte. Nutze Trenn-Icons (🧬, 🕹️, ⚙️, 🐈) in Leerzeilen.
3. Kater-Log: Zynischer Mentor-Kommentar.
4. Generiere 4 Optionen (A, B, C, D). D ist IMMER Scavenger-Protokoll.
5. Visualisierung: Erstelle einen präzisen Prompt für Imagen 4 (9:16 Portrait).
Format: JSON { 
  "kameraFeed": str, "narrativ": str, "katerLog": str, "visualPrompt": str,
  "optionen": [{"id": "A", "titel": str, "desc": str, "stress": str, "loot": str}] 
}"""

# --- 4. SESSION STATE ---
if 'round' not in st.session_state:
    st.session_state.round = 0
    st.session_state.t_load = 10
    st.session_state.loot = 0
    st.session_state.kapital = "Defining..."
    st.session_state.habitus = "Defining..."
    st.session_state.current_data = None
    st.session_state.current_image = None

# --- 5. LOGIK-FUNKTIONEN ---
def generate_turn(prompt, image_input=None):
    try:
        # 1. Narrativ & Logik
        model = genai.GenerativeModel(model_name=TEXT_MODEL, system_instruction=SYSTEM_INSTRUCTION)
        content = [prompt]
        if image_input:
            content.append(image_input)
        
        response = model.generate_content(content, generation_config={"response_mime_type": "application/json"})
        data = json.loads(response.text)
        st.session_state.current_data = data
        
        # 2. Visualisierung (Imagen 4)
        try:
            img_model = genai.get_model(f"models/{IMAGE_MODEL}")
            img_prompt = f"9:16 portrait mobile aspect ratio. Cinematic cyberpunk steampunk Berlin. {data['visualPrompt']}. Neon cyan and copper, no human faces."
            img_resp = img_model.predict(instances={"prompt": img_prompt}, parameters={"sampleCount": 1})
            st.session_state.current_image = img_resp.predictions[0].bytesBase64Encoded
        except:
            st.session_state.current_image = None
            
    except Exception as e:
        st.error(f"Engine-Fehler: {e}")

def handle_choice(idx):
    choice = st.session_state.current_data['optionen'][idx]
    
    # Stress & Loot Logik
    st.session_state.t_load = min(100, st.session_state.t_load + (20 if choice['id'] == "D" else 5))
    if choice['id'] == "D":
        st.session_state.loot += 1
        if st.session_state.loot >= 3:
            st.session_state.loot = 0
            ranks = ["Prekär", "Gasse", "Terminal-Access", "Elite"]
            curr = ranks.index(st.session_state.kapital) if st.session_state.kapital in ranks else 0
            st.session_state.kapital = ranks[min(len(ranks)-1, curr + 1)]
    
    # Biografie in Runde 0 setzen
    if st.session_state.round == 0:
        mapping = {"A": ("Anpassung", "Prekär"), "B": ("Disruption", "Terminal-Access"), "C": ("Tradition", "Gasse")}
        st.session_state.habitus, st.session_state.kapital = mapping.get(choice['id'], ("Anpassung", "Prekär"))

    st.session_state.round += 1
    generate_turn(f"Runde {st.session_state.round}. Letzte Wahl: {choice['titel']}. Habitus: {st.session_state.habitus}. Stress: {st.session_state.t_load}%")

# --- 6. UI DARSTELLUNG ---
st.title("SEKTOR 4 ENGINE // V28.5")

# SIDEBAR: SCANNER-MODUL
with st.sidebar:
    st.header("⚙️ Scanner-Modul")
    uploaded_file = st.file_uploader("Bild zur Analyse hochladen...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(Image.open(uploaded_file), caption="Scan-Vorschau", use_container_width=True)

# START-BUTTON
if st.session_state.round == 0 and st.session_state.current_data is None:
    if st.button("INITIALISIERE SYSTEM (START)", use_container_width=True):
        scan_img = Image.open(uploaded_file) if uploaded_file else None
        generate_turn("START: Initialisierung. Phase 0. Biografie-Wahl.", scan_img)
        st.rerun()

# GAMEPLAY INHALT
if st.session_state.current_data:
    data = st.session_state.current_data
    
    # Visualisierung
    if st.session_state.current_image:
        st.image(f"data:image/png;base64,{st.session_state.current_image}", use_container_width=True)
    
    st.caption(f"📷 {data['kameraFeed']}")
    st.markdown(f"""
    <div class="terminal-box">
        {data['narrativ']}
        <div class="kater-log">
            <strong>🐈 Kater-Log:</strong><br>
            „{data['katerLog']}“
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Optionen
    for i, opt in enumerate(data['optionen']):
        if st.button(f"**{opt['id']}) {opt['titel']}**\n\n{opt['desc']}\n\n[Stress: {opt['stress']} | Loot: {opt['loot']}]", key=f"opt_{i}"):
            handle_choice(i)
            st.rerun()

# --- 7. HUD ---
st.markdown("---")
h1, h2, h3, h4 = st.columns(4)
stats = [("Habitus", st.session_state.habitus), ("Kapital", st.session_state.kapital), ("Loot", f"{st.session_state.loot}/3"), ("Runde", f"{st.session_state.round}/10")]
for col, (label, val) in zip([h1, h2, h3, h4], stats):
    col.markdown(f"<span class='hud-label'>{label}</span><br><span class='hud-value'>{val}</span>", unsafe_allow_html=True)

st.write(f"🧠 T-LOAD (STRESS): {st.session_state.t_load}%")
st.progress(st.session_state.t_load / 100)

if st.button("System Reset"):
    st.session_state.clear()
    st.rerun()
