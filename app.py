import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io
import base64

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="Questbook Killswitch // Sektor 4",
    page_icon="🦾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS (STABILISIERTER TERMINAL-LOOK) ---
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
        box-shadow: inset 0 0 15px rgba(0, 255, 65, 0.05);
    }
    .kater-log {
        border-left: 3px solid #059669;
        padding-left: 15px;
        font-style: italic;
        color: #10b981;
        margin-top: 15px;
        font-size: 0.9rem;
    }
    .hud-box {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid #065f46;
        padding: 10px;
        text-align: center;
        border-radius: 4px;
    }
    .hud-label { color: #065f46; font-size: 0.65rem; text-transform: uppercase; }
    .hud-value { font-weight: bold; color: #00ff41; font-size: 0.9rem; }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background-color: rgba(0, 255, 65, 0.05);
        color: #00ff41;
        border: 1px solid #065f46;
        text-align: left;
        padding: 15px;
        border-radius: 2px;
    }
    .stButton>button:hover {
        background-color: #00ff41;
        color: #000;
        border-color: #00ff41;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API SETUP ---
# WICHTIG: Key muss in Streamlit Secrets "GOOGLE_API_KEY" heißen!
API_KEY = st.secrets.get("GOOGLE_API_KEY", "")

if not API_KEY:
    st.error("⚠️ KEIN API-KEY GEFUNDEN! Bitte füge 'GOOGLE_API_KEY' in deinen Streamlit Secrets hinzu.")
    st.stop()

genai.configure(api_key=API_KEY)

# Modellnamen (Stabile Versionen)
TEXT_MODEL = "gemini-2.5-flash-preview-09-2025"
IMAGE_MODEL = "imagen-4.0-generate-001"

SYSTEM_PROMPT = """Du bist die Sektor 4 Engine [V28.0]. 
STRIKTE REGELN: 
1. Narrativ: 3-4 Sätze, pure Geschichte, keine Meta-Begriffe.
2. Icons: Nutze Trenn-Icons (🧬, 🕹️, ⚙️, 🐈) in Leerzeilen zwischen Absätzen.
3. Kater-Log: Zynischer Mentor-Kommentar der Felinen Anomalie.
4. Generiere 4 Optionen (A, B, C, D). D ist IMMER Scavenger-Protokoll.
5. Visualisierung: Erstelle einen englischen Bild-Prompt (9:16 portrait).
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
def run_engine(prompt, uploaded_image=None):
    with st.spinner("⏳ SEKTOR 4 ENGINE ANALYSIERT DATEN..."):
        try:
            # TEXT-GENERIERUNG
            model = genai.GenerativeModel(model_name=TEXT_MODEL, system_instruction=SYSTEM_PROMPT)
            inputs = [prompt]
            if uploaded_image:
                inputs.append(uploaded_image)
            
            response = model.generate_content(inputs, generation_config={"response_mime_type": "application/json"})
            st.session_state.current_data = json.loads(response.text)
            
            # BILD-GENERIERUNG (Fallback, falls Modell nicht verfügbar)
            try:
                img_model = genai.get_model(f"models/{IMAGE_MODEL}")
                visual_prompt = st.session_state.current_data.get("visualPrompt", "Cyberpunk Berlin")
                img_resp = img_model.predict(
                    instances={"prompt": f"9:16 portrait. Cinematic cyberpunk. {visual_prompt}"},
                    parameters={"sampleCount": 1}
                )
                st.session_state.current_image = img_resp.predictions[0].bytesBase64Encoded
            except Exception as e:
                st.session_state.current_image = None
                
        except Exception as e:
            st.error(f"❌ ENGINE-KOLLAPS: {str(e)}")

def handle_choice(idx):
    choice = st.session_state.current_data['optionen'][idx]
    
    # Stress-Update
    st.session_state.t_load = min(100, st.session_state.t_load + (20 if choice['id'] == "D" else 5))
    
    # Loot-Logik
    if choice['id'] == "D":
        st.session_state.loot += 1
        if st.session_state.loot >= 3:
            st.session_state.loot = 0
            ranks = ["Prekär", "Gasse", "Terminal-Access", "Elite"]
            curr_idx = ranks.index(st.session_state.kapital) if st.session_state.kapital in ranks else 0
            st.session_state.kapital = ranks[min(len(ranks)-1, curr_idx + 1)]
            
    # Start-Initialisierung
    if st.session_state.round == 0:
        if choice['id'] == "A": st.session_state.habitus, st.session_state.kapital = "Anpassung", "Prekär"
        elif choice['id'] == "B": st.session_state.habitus, st.session_state.kapital = "Disruption", "Terminal-Access"
        elif choice['id'] == "C": st.session_state.habitus, st.session_state.kapital = "Tradition", "Gasse"

    st.session_state.round += 1
    run_engine(f"Runde {st.session_state.round}. Letzte Wahl: {choice['titel']}. T-Load: {st.session_state.t_load}%")

# --- 6. UI ---
st.title("SEKTOR 4 ENGINE // V28.0")

# Scanner Sidebar
with st.sidebar:
    st.header("⚙️ Scanner-Modul")
    uploaded = st.file_uploader("Artefakt scannen...", type=["jpg", "png", "jpeg"])
    if uploaded:
        st.image(Image.open(uploaded), use_container_width=True)

# Start-Screen
if st.session_state.round == 0 and st.session_state.current_data is None:
    if st.button("INITIALISIERE SYSTEM (START)", use_container_width=True):
        img_input = Image.open(uploaded) if uploaded else None
        run_engine("START: Initialisierung. Phase 0.", img_input)
        st.rerun()

# Spiel-Inhalt
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

# --- 7. HUD ---
st.markdown("---")
cols = st.columns(4)
stats = [("Habitus", st.session_state.habitus), ("Kapital", st.session_state.kapital), ("Loot", f"{st.session_state.loot}/3"), ("Runde", f"{st.session_state.round}/10")]
for col, (label, val) in zip(cols, stats):
    col.markdown(f"<div class='hud-box'><div class='hud-label'>{label}</div><div class='hud-value'>{val}</div></div>", unsafe_allow_html=True)

st.write(f"🧠 T-LOAD (STRESS): {st.session_state.t_load}%")
st.progress(st.session_state.t_load / 100)

if st.button("System Reset", type="secondary"):
    st.session_state.clear()
    st.rerun()
