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

# --- 2. CUSTOM CSS (TERMINAL STYLE V29.0) ---
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
        background: rgba(0, 255, 65, 0.02);
        border-radius: 4px;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.05);
    }
    .kater-log {
        border-left: 2px solid #059669;
        padding-left: 15px;
        font-style: italic;
        color: #10b981;
        margin-top: 15px;
    }
    .hud-box {
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid #065f46;
        padding: 10px;
        text-align: center;
    }
    .hud-label { color: #065f46; font-size: 0.65rem; text-transform: uppercase; }
    .hud-value { font-weight: bold; color: #00ff41; }
    
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

# --- 3. API INITIALISIERUNG ---
# Stelle sicher, dass in den Streamlit Secrets "GOOGLE_API_KEY" gesetzt ist.
API_KEY = st.secrets.get("GOOGLE_API_KEY", "")
if not API_KEY:
    st.error("⚠️ API-Key fehlt! Bitte 'GOOGLE_API_KEY' in den Streamlit Cloud Secrets hinterlegen.")
    st.stop()

genai.configure(api_key=API_KEY)

# Engine System Instruction
SYSTEM_PROMPT = """Du bist die Sektor 4 Engine [V29.0]. 
STRIKTE REGELN:
1. Narrativ: 3-4 Sätze, pure Geschichte, keine Meta-Begriffe.
2. Icons: Nutze Trenn-Icons (🧬, 🕹️, ⚙️, 🐈) in Leerzeilen zwischen Absätzen.
3. Kater-Log: Zynischer Mentor-Kommentar.
4. Optionen: Generiere 4 Optionen (A, B, C, D). D ist IMMER Scavenger-Protokoll.
5. Ausgabe: NUR valides JSON zurückgeben.
Schema: { "kameraFeed": str, "narrativ": str, "katerLog": str, "visualPrompt": str, "optionen": [{"id": "A"|"B"|"C"|"D", "titel": str, "desc": str, "stress": str, "loot": str}] }"""

# --- 4. SESSION STATE MANAGEMENT ---
if 'round' not in st.session_state:
    st.session_state.round = 0
    st.session_state.t_load = 10
    st.session_state.loot = 0
    st.session_state.kapital = "Defining..."
    st.session_state.habitus = "Defining..."
    st.session_state.current_turn = None
    st.session_state.current_image = None

# --- 5. LOGIK-FUNKTIONEN ---
def generate_turn(prompt, image_input=None):
    with st.spinner("⏳ Rekonstruiere Sektor-Daten..."):
        try:
            # 1. Text & Narrativ
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash-preview-09-2025",
                system_instruction=SYSTEM_PROMPT
            )
            inputs = [prompt]
            if image_input:
                inputs.append(image_input)
            
            response = model.generate_content(inputs, generation_config={"response_mime_type": "application/json"})
            st.session_state.current_turn = json.loads(response.text)
            
            # 2. Visualisierung (Imagen 4)
            try:
                img_model = genai.get_model("models/imagen-4.0-generate-001")
                vis_prompt = st.session_state.current_turn.get("visualPrompt", "Cyberpunk industrial alleyway")
                img_resp = img_model.predict(
                    instances={"prompt": f"9:16 portrait mobile aspect ratio. Cinematic cyberpunk. {vis_prompt}. Neon cyan and copper, industrial grit."},
                    parameters={"sampleCount": 1}
                )
                st.session_state.current_image = img_resp.predictions[0].bytesBase64Encoded
            except:
                st.session_state.current_image = None
                
        except Exception as e:
            st.error(f"❌ Engine-Kollaps: {e}")

def handle_choice(idx):
    choice = st.session_state.current_turn['optionen'][idx]
    
    # Stress-Update
    stress_gain = 20 if choice['id'] == "D" else 5
    st.session_state.t_load = min(100, st.session_state.t_load + stress_gain)
    
    # Loot-Logik
    if choice['id'] == "D":
        st.session_state.loot += 1
        if st.session_state.loot >= 3:
            st.session_state.loot = 0
            ranks = ["Prekär", "Gasse", "Terminal-Access", "Elite"]
            curr_idx = ranks.index(st.session_state.kapital) if st.session_state.kapital in ranks else 0
            st.session_state.kapital = ranks[min(len(ranks)-1, curr_idx + 1)]
            
    # Initialisierung (Runde 0)
    if st.session_state.round == 0:
        if choice['id'] == "A": st.session_state.habitus, st.session_state.kapital = "Anpassung", "Prekär"
        elif choice['id'] == "B": st.session_state.habitus, st.session_state.kapital = "Disruption", "Terminal-Access"
        elif choice['id'] == "C": st.session_state.habitus, st.session_state.kapital = "Tradition", "Gasse"

    st.session_state.round += 1
    next_prompt = f"Runde {st.session_state.round}. Letzte Wahl: {choice['titel']}. Status: Stress {st.session_state.t_load}%, Loot {st.session_state.loot}/3, Kapital {st.session_state.kapital}."
    generate_turn(next_prompt)

# --- 6. UI ---
st.title("SEKTOR 4 ENGINE // V29.0")

with st.sidebar:
    st.header("⚙️ Scanner-Modul")
    uploaded = st.file_uploader("Bild scannen...", type=["jpg", "png", "jpeg"])
    if uploaded:
        st.image(Image.open(uploaded), width=250)

if st.session_state.round == 0 and st.session_state.current_turn is None:
    if st.button("INITIALISIERE SYSTEM (START)", width="stretch"):
        img_in = Image.open(uploaded) if uploaded else None
        generate_turn("START: Initialisierung. Phase 0. Biografie-Wahl.", img_in)
        st.rerun()

if st.session_state.current_turn:
    turn = st.session_state.current_turn
    
    if st.session_state.current_image:
        st.image(f"data:image/png;base64,{st.session_state.current_image}", width="stretch")
    
    st.caption(f"📷 {turn['kameraFeed']}")
    st.markdown(f"""
    <div class="terminal-container">
        {turn['narrativ']}
        <div class="kater-log">
            <strong>🐈 Feline Anomalie:</strong><br>
            „{turn['katerLog']}“
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    for i, opt in enumerate(turn['optionen']):
        btn_label = f"**{opt['id']}) {opt['titel']}**\n\n{opt['desc']}\n\n[Stress: {opt['stress']} | Loot: {opt['loot']}]"
        if st.button(btn_label, key=f"btn_{i}", width="stretch"):
            handle_choice(i)
            st.rerun()

# --- 7. HUD ---
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
