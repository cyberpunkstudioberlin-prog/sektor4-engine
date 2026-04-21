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

# --- 2. CUSTOM CSS (TERMINAL STYLE) ---
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
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .kater-log {
        border-left: 3px solid #059669;
        padding-left: 15px;
        font-style: italic;
        color: #10b981;
        margin: 15px 0;
    }
    .hud-label { color: #065f46; font-size: 0.7rem; text-transform: uppercase; }
    .hud-value { font-weight: bold; color: #10b981; }
    .stButton>button {
        width: 100%;
        background-color: rgba(0, 255, 0, 0.1);
        color: #00ff00;
        border: 1px solid #065f46;
        text-align: left;
        padding: 15px;
        border-radius: 2px;
    }
    .stButton>button:hover {
        background-color: #00ff00;
        color: #000;
        border-color: #00ff00;
    }
    .img-container {
        border: 1px solid #065f46;
        padding: 5px;
        background: #000;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API INITIALISIERUNG ---
API_KEY = st.secrets.get("GOOGLE_API_KEY", "")
genai.configure(api_key=API_KEY)

# Modelle definieren
TEXT_MODEL = "gemini-2.5-flash-preview-09-2025"
IMAGE_MODEL = "imagen-4.0-generate-001"

SYSTEM_INSTRUCTION = """Du bist die Sektor 4 Engine [V28.5]. 
STRIKTE REGELN: 
1. Kein Smalltalk. 
2. Narrativ: 3-4 Sätze, pure Geschichte. Nutze Trenn-Icons (🧬, 🕹️, ⚙️, 🐈).
3. Image-Prompt: Erstelle einen detaillierten Prompt für einen Bildgenerator (9:16 Portrait, Cyberpunk Berlin).
Format: JSON { 
  "kameraFeed": str, 
  "narrativ": str, 
  "katerLog": str, 
  "imagePrompt": str,
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
def generate_image(prompt):
    """Generiert ein Bild basierend auf dem narrativen Prompt."""
    try:
        img_model = genai.get_model(f"models/{IMAGE_MODEL}")
        # Simulation der Bildgenerierung via predict (falls verfügbar im Environment)
        # Hier nutzen wir das Standard-Pattern für Imagen-Aufrufe
        response = img_model.predict(
            instances={"prompt": prompt},
            parameters={"sampleCount": 1}
        )
        return response.predictions[0].bytesBase64Encoded
    except:
        # Fallback falls Imagen-Dienst im speziellen Projekt nicht aktiv ist
        return None

def generate_turn(prompt, scan_image=None):
    """Generiert den nächsten Spielzug inkl. Text und Bild."""
    try:
        model = genai.GenerativeModel(model_name=TEXT_MODEL, system_instruction=SYSTEM_INSTRUCTION)
        content = [prompt]
        if scan_image:
            content.append(scan_image)
        
        # Text-Generierung
        response = model.generate_content(content, generation_config={"response_mime_type": "application/json"})
        data = json.loads(response.text)
        st.session_state.current_data = data
        
        # Bild-Visualisierung generieren
        with st.spinner("Visualisiere Sektor-Daten..."):
            b64_image = generate_image(data.get("imagePrompt", "Cyberpunk industrial Berlin alleyway, green lighting, cinematic"))
            st.session_state.current_image = b64_image
            
    except Exception as e:
        st.error(f"Engine-Kollaps: {e}")

def handle_choice(choice_idx):
    choice = st.session_state.current_data['optionen'][choice_idx]
    
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
    generate_turn(f"Runde {st.session_state.round}. Letzte Wahl: {choice['titel']}. Habitus: {st.session_state.habitus}. Kapital: {st.session_state.kapital}. Stress: {st.session_state.t_load}%")

# --- 6. UI ---
st.title("SEKTOR 4 ENGINE // V28.5")

# Scanner-Modul in der Sidebar
with st.sidebar:
    st.header("⚙️ Scanner-Modul")
    uploaded_file = st.file_uploader("Bild zur Analyse hochladen...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img_display = Image.open(uploaded_file)
        st.image(img_display, caption="Scan-Vorschau", use_container_width=True)

# Spiel-Start
if st.session_state.round == 0 and st.session_state.current_data is None:
    if st.button("INITIALISIERE SYSTEM (START)"):
        scan_img = Image.open(uploaded_file) if uploaded_file else None
        generate_turn("START: Initialisierung. Analysiere Herkunft.", scan_img)
        st.rerun()

# Spiel-Inhalt
if st.session_state.current_data:
    data = st.session_state.current_data
    
    # VISUALISIERUNG
    if st.session_state.current_image:
        st.markdown('<div class="img-container">', unsafe_allow_html=True)
        st.image(f"data:image/png;base64,{st.session_state.current_image}", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # NARRATIV
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
    
    # OPTIONEN
    for i, opt in enumerate(data['optionen']):
        btn_label = f"**{opt['id']}) {opt['titel']}**\n\n{opt['desc']}\n\n[Stress: {opt['stress']} | Loot: {opt['loot']}]"
        if st.button(btn_label, key=f"btn_{i}"):
            handle_choice(i)
            st.rerun()

# HUD
st.markdown("---")
h_col1, h_col2, h_col3, h_col4 = st.columns(4)
stats = [("Habitus", st.session_state.habitus), ("Kapital", st.session_state.kapital), ("Loot", f"{st.session_state.loot}/3"), ("Runde", f"{st.session_state.round}/10")]
for col, (label, val) in zip([h_col1, h_col2, h_col3, h_col4], stats):
    col.markdown(f"<span class='hud-label'>{label}</span><br><span class='hud-value'>{val}</span>", unsafe_allow_html=True)

st.write(f"🧠 T-LOAD (STRESS): {st.session_state.t_load}%")
st.progress(st.session_state.t_load / 100)

if st.button("System Reset", type="secondary"):
    st.session_state.clear()
    st.rerun()
