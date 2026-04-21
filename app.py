import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io

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
    }
    .stButton>button:hover {
        background-color: #00ff00;
        color: #000;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. API INITIALISIERUNG ---
API_KEY = st.secrets.get("GOOGLE_API_KEY", "")
genai.configure(api_key=API_KEY)

SYSTEM_INSTRUCTION = """Du bist die Sektor 4 Engine [V28.5]. 
STRIKTE REGELN: 
1. Kein Smalltalk. 
2. Narrativ: 3-4 Sätze, pure Geschichte. Nutze Trenn-Icons (🧬, 🕹️, ⚙️, 🐈).
3. Wenn ein Bild hochgeladen wurde, integriere dessen Inhalt zynisch in die Story.
Format: JSON { "kameraFeed": str, "narrativ": str, "katerLog": str, "optionen": [{"id": "A", "titel": str, "desc": str, "stress": str, "loot": str}] }"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-preview-09-2025",
    system_instruction=SYSTEM_INSTRUCTION
)

# --- 4. SESSION STATE ---
if 'round' not in st.session_state:
    st.session_state.round = 0
    st.session_state.t_load = 10
    st.session_state.loot = 0
    st.session_state.kapital = "Defining..."
    st.session_state.habitus = "Defining..."
    st.session_state.current_data = None

# --- 5. LOGIK-FUNKTIONEN ---
def generate_turn(prompt, image=None):
    try:
        content = [prompt]
        if image:
            content.append(image)
        
        response = model.generate_content(content, generation_config={"response_mime_type": "application/json"})
        st.session_state.current_data = json.loads(response.text)
    except Exception as e:
        st.error(f"Engine-Fehler: {e}")

def handle_choice(choice_idx):
    choice = st.session_state.current_data['optionen'][choice_idx]
    st.session_state.t_load = min(100, st.session_state.t_load + (20 if choice['id'] == "D" else 5))
    if choice['id'] == "D":
        st.session_state.loot += 1
        if st.session_state.loot >= 3:
            st.session_state.loot = 0
            ranks = ["Prekär", "Gasse", "Terminal-Access", "Elite"]
            curr = ranks.index(st.session_state.kapital) if st.session_state.kapital in ranks else 0
            st.session_state.kapital = ranks[min(len(ranks)-1, curr + 1)]
    
    if st.session_state.round == 0:
        mapping = {"A": ("Anpassung", "Prekär"), "B": ("Disruption", "Terminal-Access"), "C": ("Tradition", "Gasse")}
        st.session_state.habitus, st.session_state.kapital = mapping.get(choice['id'], ("Anpassung", "Prekär"))

    st.session_state.round += 1
    generate_turn(f"Runde {st.session_state.round}. Letzte Wahl: {choice['titel']}. Stress: {st.session_state.t_load}")

# --- 6. UI ---
st.title("SEKTOR 4 ENGINE // V28.5")

# IMAGE UPLOADER SIDEBAR
with st.sidebar:
    st.header("⚙️ Scanner-Modul")
    uploaded_file = st.file_uploader("Bild zur Analyse hochladen...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Analysiere Scan...", use_container_width=True)

# START / GAMEPLAY
if st.session_state.round == 0 and st.session_state.current_data is None:
    if st.button("INITIALISIERE SYSTEM (START)"):
        img_input = Image.open(uploaded_file) if uploaded_file else None
        generate_turn("START: Initialisierung. Analysiere Herkunft.", img_input)
        st.rerun()

if st.session_state.current_data:
    data = st.session_state.current_data
    st.caption(f"📷 {data['kameraFeed']}")
    st.markdown(f"""<div class="terminal-box">{data['narrativ']}<div class="kater-log"><strong>🐈 Kater-Log:</strong><br>„{data['katerLog']}“</div></div>""", unsafe_allow_html=True)
    
    for i, opt in enumerate(data['optionen']):
        if st.button(f"**{opt['id']}) {opt['titel']}**\n\n{opt['desc']}\n\n[Stress: {opt['stress']} | Loot: {opt['loot']}]", key=f"btn_{i}"):
            handle_choice(i)
            st.rerun()

# HUD
st.markdown("---")
cols = st.columns(4)
stats = [("Habitus", st.session_state.habitus), ("Kapital", st.session_state.kapital), ("Loot", f"{st.session_state.loot}/3"), ("Runde", f"{st.session_state.round}/10")]
for col, (label, val) in zip(cols, stats):
    col.markdown(f"<span class='hud-label'>{label}</span><br><span class='hud-value'>{val}</span>", unsafe_allow_html=True)

st.write(f"🧠 T-LOAD: {st.session_state.t_load}%")
st.progress(st.session_state.t_load / 100)

if st.button("System Reset"):
    st.session_state.clear()
    st.rerun()
