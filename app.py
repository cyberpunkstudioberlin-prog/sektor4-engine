import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import re

# Author: Murat Zengin
# Project: Questbook Killswitch
# Module: V71.1 Core (Multimodal, Inferenz-stabilisiert)

# --- UI INITIALISIERUNG ---
st.set_page_config(
    page_title="Questbook Killswitch", 
    page_icon="🦾", 
    layout="centered"
)

# Custom CSS für das Sektor 4 Terminal-Feeling
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; }
    .stButton>button { 
        background-color: #111; color: #00ff41; border: 1px solid #00ff41; 
        width: 100%; border-radius: 4px; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #00ff41; color: #000; }
    .stChatInput { border-top: 1px solid #333; }
    div[data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #00ff41; }
    </style>
    """, unsafe_allow_html=True)

st.title("Questbook Killswitch 🦾")

# --- ENGINE CONFIG & INFERENZ-STABILISIERUNG ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("SYSTEM ERROR: API-Key nicht gefunden. Bitte in den Secrets hinterlegen.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Dynamische Modell-Auswahl zur Vermeidung von 404-Fehlern
if "active_text_model" not in st.session_state:
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Priorität: Gemini 2.5 -> 1.5 Pro Latest -> 1.5 Pro
        st.session_state.active_text_model = next((m for m in available if "gemini-2.5" in m), 
                                            next((m for m in available if "gemini-1.5-pro-latest" in m), 
                                            next((m for m in available if "gemini-1.5-pro" in m), "models/gemini-1.5-pro")))
    except:
        st.session_state.active_text_model = "models/gemini-1.5-pro-latest"

text_model = genai.GenerativeModel(st.session_state.active_text_model)
image_model = genai.GenerativeModel('imagen-3.0-generate-001')

# --- SESSION STATE ---
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
    st.session_state.display_text = "SYSTEM BEREIT. Bitte 'System Boot' eingeben."
    st.session_state.current_image = None
    st.session_state.matrix = {"Y": "Unbekannt", "X": "Unbekannt", "T": 10}
    st.session_state.round = 0

# --- BILDGENERATOR (IMAGEN 3) ---
def generate_sektor_visual(scene_description):
    """Erzeugt ein 9:16 Bild ohne Menschen (Safety-Bypass)."""
    safety_prompt = (
        f"9:16 vertical mobile aspect ratio. Sektor 4 Cyberpunk/Steampunk aesthetic. "
        f"Cinematic lighting, rainy atmosphere, ultra-detailed. "
        f"STRICTLY NO HUMANS, no blood. Focus on machines, robots, "
        f"anthropomorphic steampunk cat or biomechanical crocodile: {scene_description}"
    )
    try:
        with st.spinner("Generiere Visual-Asset..."):
            response = image_model.generate_content(safety_prompt)
            img_data = response.candidates[0].content.parts[0].inline_data.data
            st.session_state.current_image = img_data
            return img_data
    except Exception as e:
        st.sidebar.warning(f"Bild-Inferenz unterbrochen: {str(e)}")
        return None

# --- CORE LOGIK ---
def run_engine(user_input):
    directive = """[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM]
Du bist die "Sektor 4 Engine", ein unerbittlicher Cyberpunk/Steampunk Game Master.

[DIE 4D-MATRIX]
- [Y] Kapital, [X] Habitus, [Z] Biografie, [T] Allostatic Load (Stress).
- T-Load startet bei 10/100. Killswitch bei 100 = Game Over.

[OPERATIVE REGELN]
1. Jede Antwort MUSS mit einem "📷 Kamera-Feed: [1 Satz Szenerie]" beginnen.
2. Keine Menschen, keine Gewalt gegen Menschen. Nur Maschinen/Tiere.
3. Struktur: Bild-Prompt-Satz, Story-Text (KISS), Optionen A/B/C, HUD.

[KAPITEL 1] Necromancer Krokodil Jagd. Runden 1-9 Flucht, Runde 10 Showdown.
"""
    
    if user_input.upper() == "SYSTEM BOOT":
        boot_image_prompt = "A steampunk cat standing on a neon-lit rooftop in the rain, holding a rapier."
        generate_sektor_visual(boot_image_prompt)
        prompt = f"{directive}\nNutzer hat das System gestartet. Führe das Tutorial aus."
    else:
        prompt = f"{directive}\nHistorie: {st.session_state.chat_log[-3:]}\nStatus: {st.session_state.matrix}\nNutzer wählt: {user_input}"

    try:
        with st.spinner("Matrix-Inferenz läuft..."):
            response = text_model.generate_content(prompt)
            output_text = response.text
            
            # Bild für die nächste Runde vorbereiten
            feed_match = re.search(r"📷 Kamera-Feed: (.*)", output_text)
            if feed_match and user_input.upper() != "SYSTEM BOOT":
                generate_sektor_visual(feed_match.group(1))
            
            st.session_state.display_text = output_text
            st.session_state.chat_log.append({"role": "user", "content": user_input})
            st.session_state.chat_log.append({"role": "assistant", "content": output_text})
            st.session_state.round += 1
            
    except Exception as e:
        st.session_state.display_text = f"CRITICAL MATRIX CRASH: {str(e)}"

# --- UI LAYOUT ---

# 1. BILD (Mandatory Image-First)
if st.session_state.current_image:
    st.image(st.session_state.current_image, use_container_width=True)
else:
    st.markdown("""
        <div style="width:100%; height:300px; background:#111; border:1px solid #333; 
        display:flex; align-items:center; justify-content:center; color:#333;">
        [KAMERA-FEED OFFLINE]
        </div>
        """, unsafe_allow_html=True)

# 2. TEXT-OUTPUT
st.markdown("---")
st.markdown(st.session_state.display_text)

# 3. INTERAKTION
st.write("")
c1, c2, c3 = st.columns(3)
if c1.button("A"): run_engine("A"); st.rerun()
if c2.button("B"): run_engine("B"); st.rerun()
if c3.button("C"): run_engine("C"); st.rerun()

# 4. INPUT
cmd = st.chat_input("Konsoleneingabe...")
if cmd:
    if cmd.upper() == "SYSTEM BOOT":
        run_engine("SYSTEM BOOT")
    else:
        run_engine(cmd)
    st.rerun()

# 5. SIDEBAR (HUD)
with st.sidebar:
    st.header("⚙️ System-HUD")
    st.write(f"Modell: {st.session_state.active_text_model}")
    st.write(f"Runde: {st.session_state.round}")
    st.write(f"Kapital (Y): {st.session_state.matrix['Y']}")
    st.write(f"Habitus (X): {st.session_state.matrix['X']}")
    st.progress(st.session_state.matrix['T'] / 100, text=f"T-Load: {st.session_state.matrix['T']}%")
    
    if st.button("Matrix Reset"):
        st.session_state.clear()
        st.rerun()
