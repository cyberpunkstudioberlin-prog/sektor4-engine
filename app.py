import streamlit as st
from google import genai
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

# --- 2. CLIENT INITIALISIERUNG (NEU) ---
# Nutzt das google-genai SDK von 2026
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 3. CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0a0c10; color: #00ff41; font-family: 'Courier New', Courier, monospace; }
    .terminal-container { border: 1px solid #10b981; padding: 20px; background: rgba(0, 255, 65, 0.03); border-radius: 4px; margin-bottom: 20px; box-shadow: inset 0 0 15px rgba(0, 255, 65, 0.1); }
    .kater-log { margin-top: 15px; padding-top: 10px; border-top: 1px dashed #10b981; color: #ffeb3b; font-size: 0.9em; }
    .hud-box { background: #161b22; border-left: 3px solid #00ff41; padding: 10px; text-align: center; }
    .hud-label { font-size: 0.7em; color: #8b949e; text-transform: uppercase; }
    .hud-value { font-weight: bold; font-size: 1.1em; }
</style>
""", unsafe_allow_html=True)

# --- 4. SESSION STATE ---
if 'round' not in st.session_state: st.session_state.round = 0
if 'habitus' not in st.session_state: st.session_state.habitus = "Unbekannt"
if 'kapital' not in st.session_state: st.session_state.kapital = "Null"
if 'loot' not in st.session_state: st.session_state.loot = 0
if 't_load' not in st.session_state: st.session_state.t_load = 10
if 'current_data' not in st.session_state: st.session_state.current_data = None
if 'current_image' not in st.session_state: st.session_state.current_image = None

# --- 5. ENGINE LOGIK ---
def run_engine(prompt_input, image_input=None):
    with st.spinner("⏳ SEKTOR 4 ENGINE ANALYSIERT..."):
        try:
            # TEXT GENERIERUNG
            sys_prompt = """
            Du bist die SEKTOR 4 ENGINE. Antworte NUR im JSON-Format:
            {
              "narrativ": "...", "kameraFeed": "...", "katerLog": "...",
              "optionen": [{"id": "A", "titel": "...", "desc": "...", "stress": 5, "loot": 0}, ...]
            }
            Thema: Cyberpunk, Kantische Logik, Sinus-Milieus.
            """
            
            content_list = [sys_prompt, prompt_input]
            if image_input:
                content_list.append(image_input)

            response = client.models.generate_content(
                model="gemini-2.0-flash", # Schnelle Engine für V28.0
                contents=content_list
            )
            
            # JSON bereinigen und laden
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            st.session_state.current_data = json.loads(clean_json)
            
            # BILD GENERIERUNG (Optionaler Teil deiner Logik)
            try:
                visual_prompt = st.session_state.current_data['kameraFeed']
                # Hier nutzt du Imagen über das neue SDK
                # Falls du kein Imagen-Modell nutzt, diesen Teil überspringen
                st.session_state.current_image = None # Platzhalter für Bild-Injektion
            except:
                pass
                
        except Exception as e:
            st.error(f"❌ ENGINE-KOLLAPS: {str(e)}")

def handle_choice(idx):
    choice = st.session_state.current_data['optionen'][idx]
    st.session_state.t_load = min(100, st.session_state.t_load + choice.get('stress', 5))
    st.session_state.round += 1
    run_engine(f"Runde {st.session_state.round}. Wahl: {choice['titel']}. Status: {st.session_state.habitus}")

# --- 6. UI ---
st.title("SEKTOR 4 ENGINE // V28.0")

# Scanner Sidebar
with st.sidebar:
    st.header("⚙️ Scanner-Modul")
    uploaded = st.file_uploader("Artefakt scannen...", type=["jpg", "png", "jpeg"])
    if uploaded:
        # FIX: 'width="stretch"' statt 'use_container_width'
        st.image(Image.open(uploaded), width=300)

# Start-Screen
if st.session_state.round == 0 and st.session_state.current_data is None:
    if st.button("INITIALISIERE SYSTEM (START)", use_container_width=True):
        img_input = Image.open(uploaded) if uploaded else None
        run_engine("START: Initialisierung. Bestimme Habitus basierend auf Artefakt.", img_input)
        st.rerun()

# Spiel-Inhalt
if st.session_state.current_data:
    data = st.session_state.current_data
    
    st.caption(f"📷 {data.get('kameraFeed', 'Kein Feed')}")
    st.markdown(f"""
    <div class="terminal-container">
        {data.get('narrativ', 'Lade Daten...')}
        <div class="kater-log">
            <strong>🐈 Feline Anomalie:</strong><br>
            „{data.get('katerLog', 'Miau... (Keine Daten)')}“
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Optionen
    for i, opt in enumerate(data.get('optionen', [])):
        if st.button(f"**{opt['id']}) {opt['titel']}**\n\n{opt['desc']}", key=f"opt_{i}", use_container_width=True):
            handle_choice(i)
            st.rerun()

# --- 7. HUD ---
st.markdown("---")
cols = st.columns(4)
stats = [
    ("Habitus", st.session_state.habitus), 
    ("Kapital", st.session_state.kapital), 
    ("Loot", f"{st.session_state.loot}/3"), 
    ("Runde", f"{st.session_state.round}")
]
for col, (label, val) in zip(cols, stats):
    col.markdown(f"<div class='hud-box'><div class='hud-label'>{label}</div><div class='hud-value'>{val}</div></div>", unsafe_allow_html=True)

st.write(f"🧠 T-LOAD (STRESS): {st.session_state.t_load}%")
st.progress(st.session_state.t_load / 100)

if st.button("System Reset"):
    st.session_state.clear()
    st.rerun()
    
