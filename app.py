import streamlit as st
import google.generativeai as genai
import time
import re
import io
from PIL import Image

# Author: Murat Zengin
# Project: Questbook Killswitch
# Module: V73 Master Core (Stabilisiert)

# --- UI INITIALISIERUNG ---
st.set_page_config(
    page_title="Questbook Killswitch", 
    page_icon="🦾", 
    layout="centered"
)

# Custom CSS für die Sektor 4 Terminal-Ästhetik
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
    .synthid-badge { 
        color: #00ff41; font-size: 0.7rem; border: 1px solid #00ff41; 
        padding: 2px 5px; border-radius: 3px; opacity: 0.7; margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Questbook Killswitch 🦾")

# --- API KONFIGURATION ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("SYSTEM ERROR: API-Key fehlt in den Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- HILFSFUNKTIONEN FÜR STABILITÄT ---

def call_with_exponential_backoff(func, *args, **kwargs):
    """Implementiert Backoff: 1s, 2s, 4s, 8s, 16s."""
    delays = [1, 2, 4, 8, 16]
    for i, delay in enumerate(delays):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            err = str(e).lower()
            if "429" in err or "quota" in err or "too many" in err:
                if i < len(delays) - 1:
                    time.sleep(delay)
                    continue
            raise e
    return func(*args, **kwargs)

def get_stable_model_names():
    """Findet verfügbare Modelle dynamisch."""
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        text = next((m for m in models if "gemini-2.5-flash-preview-09-2025" in m),
               next((m for m in models if "gemini-2.5-flash" in m),
               next((m for m in models if "gemini-1.5-flash" in m), "models/gemini-1.5-flash")))
        
        img_models = [m.name for m in genai.list_models() if 'predict' in m.supported_generation_methods or 'generateContent' in m.supported_generation_methods]
        image = next((m for m in img_models if "imagen-4.0" in m),
                next((m for m in img_models if "imagen-3.0" in m), "models/imagen-3.0-generate-001"))
        
        return text, image
    except:
        return "models/gemini-1.5-flash", "models/imagen-3.0-generate-001"

if "text_model_name" not in st.session_state:
    t_name, i_name = get_stable_model_names()
    st.session_state.text_model_name = t_name
    st.session_state.image_model_name = i_name

text_model = genai.GenerativeModel(st.session_state.text_model_name)
image_model = genai.GenerativeModel(st.session_state.image_model_name)

# --- SESSION STATE ---
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
    st.session_state.display_text = "SYSTEM BEREIT. Bitte 'System Boot' eingeben."
    st.session_state.current_image = None
    st.session_state.matrix = {"Y": "Unbekannt", "X": "Unbekannt", "T": 10}
    st.session_state.round = 0

# --- BILDGENERATOR ---
def generate_visual(prompt):
    safety_prompt = (
        f"vertical 9:16 mobile aspect ratio. Sektor 4 aesthetic, cinematic. "
        f"NO HUMANS, no blood. Cybernetic machines, steampunk creatures: {prompt}"
    )
    try:
        response = call_with_exponential_backoff(image_model.generate_content, safety_prompt)
        img_data = response.candidates[0].content.parts[0].inline_data.data
        st.session_state.current_image = img_data
        return img_data
    except Exception as e:
        st.sidebar.warning(f"Inferenz-Konflikt: {str(e)}")
        return None

# --- CORE LOGIK ---
def run_engine(user_input):
    directive = """[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM]
Du bist die "Sektor 4 Engine". Nutze die 4D-Matrix: [Y] Kapital, [X] Habitus, [T] Stress.
Stress (T) startet bei 10. Killswitch bei 100 = GAME OVER.
Regeln: 1. Starte mit '📷 Kamera-Feed: [1 Satz]'. 2. KEINE Menschen. 3. Struktur: Bild-Prompt, Story, Optionen (A, B, C), HUD.
"""
    
    if user_input.upper() == "SYSTEM BOOT":
        boot_prompt = "A steampunk cat with green glowing optics in a rainy cyberpunk alley."
        generate_visual(boot_prompt)
        prompt = f"{directive}\nInitialisiere Simulation. Starte Tutorial."
    else:
        prompt = f"{directive}\nStatus: {st.session_state.matrix}\nHistorie: {st.session_state.chat_log[-2:]}\nUser wählt: {user_input}"

    try:
        response = call_with_exponential_backoff(text_model.generate_content, prompt)
        output_text = response.text
        
        feed_match = re.search(r"📷 Kamera-Feed: (.*)", output_text)
        if feed_match and user_input.upper() != "SYSTEM BOOT":
            generate_visual(feed_match.group(1))
            
        st.session_state.display_text = output_text
        st.session_state.chat_log.append({"role": "user", "content": user_input})
        st.session_state.chat_log.append({"role": "assistant", "content": output_text})
        st.session_state.round += 1
            
    except Exception as e:
        st.session_state.display_text = f"CRITICAL MATRIX CRASH: {str(e)}"

# --- UI LAYOUT ---
if st.session_state.current_image:
    st.image(st.session_state.current_image, use_container_width=True)
    st.markdown('<div class="synthid-badge">SYNTHID VERIFIED // PIXEL-EMBEDDED</div>', unsafe_allow_html=True)
else:
    st.markdown("""<div style="width:100%; height:300px; background:#111; border:1px solid #333; 
        display:flex; align-items:center; justify-content:center; color:#333;">[KAMERA-FEED OFFLINE]</div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown(st.session_state.display_text)
st.markdown('<div class="synthid-badge" style="border:none; border-left:1px solid #00ff41;">TOURNAMENT SAMPLING SIGNATURE: ACTIVE</div>', unsafe_allow_html=True)

st.write("")
c1, c2, c3 = st.columns(3)
if c1.button("A"): run_engine("A"); st.rerun()
if c2.button("B"): run_engine("B"); st.rerun()
if c3.button("C"): run_engine("C"); st.rerun()

cmd = st.chat_input("Konsoleneingabe...")
if cmd:
    run_engine(cmd)
    st.rerun()

with st.sidebar:
    st.header("⚙️ System-HUD")
    st.write(f"Inferenz-Tier: {st.session_state.get('text_model_name', 'Verbinde...')}")
    st.write(f"Runde: {st.session_state.round}/10")
    st.progress(st.session_state.matrix["T"] / 100, text=f"ALI (Stress): {st.session_state.matrix['T']}%")
    if st.button("Matrix Reset"):
        st.session_state.clear()
        st.rerun()
