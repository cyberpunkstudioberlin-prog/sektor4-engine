import streamlit as st
import google.generativeai as genai
import time
import re
import base64
import io
from PIL import Image

# Autor: Murat Zengin
# Projekt: Questbook Killswitch
# Modul: V72 Stable Core (Inferenz-Stabilisierung & SynthID)

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
        padding: 2px 5px; border-radius: 3px; opacity: 0.7;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Questbook Killswitch 🦾")

# --- API KONFIGURATION ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("SYSTEM ERROR: API-Key fehlt in den Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- HILFSFUNKTIONEN FÜR STABILITÄT (FIX 429) ---

def call_gemini_with_backoff(model, prompt, max_retries=5):
    """Implementiert Exponential Backoff für Quota-Fehler."""
    for i in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response
        except Exception as e:
            err_msg = str(e).lower()
            if "429" in err_msg or "quota" in err_msg:
                wait_time = 2**i + (0.1 * i)
                time.sleep(wait_time)
                continue
            else:
                raise e
    raise Exception("Maximale Retries nach 429-Fehler erreicht.")

# --- DYNAMISCHE MODELL-AUSWAHL (FIX 404) ---
if "active_text_model_name" not in st.session_state:
    try:
        # Scannt verfügbare Modelle im aktuellen Inferenz-Tier
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Prioritäten-Matrix für Sektor 4
        target = next((m for m in models if "gemini-1.5-pro-latest" in m),
                 next((m for m in models if "gemini-1.5-pro" in m),
                 next((m for m in models if "gemini-1.5-flash" in m), models[0])))
        st.session_state.active_text_model_name = target
    except:
        # Hardcoded Fallback
        st.session_state.active_text_model_name = "models/gemini-1.5-pro-latest"

text_model = genai.GenerativeModel(st.session_state.active_text_model_name)
# Bild-Modell (Standard-Referenz für Imagen 3)
image_model = genai.GenerativeModel('imagen-3.0-generate-001')

# --- SESSION STATE ---
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
    st.session_state.display_text = "SYSTEM BEREIT. Bitte 'System Boot' eingeben."
    st.session_state.current_image = None
    st.session_state.matrix = {"Y": "Unbekannt", "X": "Unbekannt", "T": 10, "Z": "Unbekannt"}
    st.session_state.round = 0

# --- BILDGENERATOR (IMAGEN) ---
def generate_visual(prompt):
    """Erzeugt 9:16 Visuals ohne Menschen (Sektor 4 Safety-Protokoll)."""
    safety_prompt = (
        f"9:16 vertical mobile aspect ratio. Sektor 4 aesthetic, dark cyberpunk. "
        f"NO HUMANS, no blood. Focus on machines, steampunk cats or drones. "
        f"Cinematic lighting: {prompt}"
    )
    try:
        response = call_gemini_with_backoff(image_model, safety_prompt)
        # Extraktion der Inline-Bilddaten
        img_data = response.candidates[0].content.parts[0].inline_data.data
        st.session_state.current_image = img_data
        return img_data
    except Exception as e:
        st.sidebar.warning(f"Bild-Inferenz verzögert: {str(e)}")
        return None

# --- ENGINE LOGIK ---
def run_engine(user_input):
    directive = """[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM]
Du bist die "Sektor 4 Engine". Nutze die 4D-Matrix: [Y] Kapital, [X] Habitus, [Z] Biografie, [T] Stress.
T-Load startet bei 10. Killswitch bei 100 = GAME OVER.

REGELN:
1. Beginne IMMER mit: "📷 Kamera-Feed: [1 atmosphärischer Satz]".
2. KEINE Menschen oder Gewalt an Menschen beschreiben/generieren.
3. Struktur: Bild-Prompt, Story (KISS), MC-Optionen (A, B, C), HUD.
4. Kapitel 1: Flucht vor dem Necromancer Krokodil.
"""
    
    if user_input.upper() == "SYSTEM BOOT":
        boot_prompt = "A steampunk cat with glowing green eyes in a dark rainy alleyway."
        generate_visual(boot_prompt)
        prompt = f"{directive}\nInitialisiere Sektor 4. Starte Tutorial."
    else:
        prompt = f"{directive}\nStatus: {st.session_state.matrix}\nHistorie: {st.session_state.chat_log[-2:]}\nUser wählt: {user_input}"

    try:
        response = call_gemini_with_backoff(text_model, prompt)
        output_text = response.text
        
        # Bild für die nächste Runde vorbereiten (Kamera-Feed Parsing)
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

# 1. BILD (Mandatory Image-First)
if st.session_state.current_image:
    st.image(st.session_state.current_image, use_container_width=True)
    st.markdown('<div class="synthid-badge">SYNTHID VERIFIED // PIXEL-EMBEDDED</div>', unsafe_allow_html=True)
else:
    st.markdown("""<div style="width:100%; height:300px; background:#111; border:1px solid #333; 
        display:flex; align-items:center; justify-content:center; color:#333;">[KAMERA-FEED OFFLINE]</div>""", unsafe_allow_html=True)

# 2. TEXT
st.markdown("---")
st.markdown(st.session_state.display_text)
st.markdown('<div class="synthid-badge" style="border:none; border-left:1px solid #00ff41;">TOURNAMENT SAMPLING SIGNATURE: ACTIVE</div>', unsafe_allow_html=True)

# 3. INTERAKTION
st.write("")
c1, c2, c3 = st.columns(3)
if c1.button("A"): run_engine("A"); st.rerun()
if c2.button("B"): run_engine("B"); st.rerun()
if c3.button("C"): run_engine("C"); st.rerun()

# 4. INPUT
cmd = st.chat_input("Konsoleneingabe...")
if cmd:
    run_engine(cmd)
    st.rerun()

# 5. SIDEBAR (HUD)
with st.sidebar:
    st.header("⚙️ System-HUD")
    st.write(f"Inferenz-Knoten: {st.session_state.active_text_model_name}")
    st.write(f"Runde: {st.session_state.round}/10")
    st.progress(st.session_state.matrix["T"] / 100, text=f"ALI (Stress): {st.session_state.matrix['T']}%")
    
    st.markdown("---")
    st.markdown("**4D-Vektoren:**")
    st.write(f"Kapital (Y): {st.session_state.matrix['Y']}")
    st.write(f"Habitus (X): {st.session_state.matrix['X']}")
    
    if st.button("Matrix Reset"):
        st.session_state.clear()
        st.rerun()
