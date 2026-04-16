import streamlit as st
import google.generativeai as genai
import time
import re
import urllib.parse
import random

# Author: Murat Zengin
# Projekt: Questbook Killswitch
# Modul: V79 Zero-Budget Master (Gemini + Pollinations)

# --- UI INITIALISIERUNG ---
st.set_page_config(
    page_title="Questbook Killswitch", 
    page_icon="🦾", 
    layout="centered"
)

# Custom CSS für die Sektor 4 Terminal-Ästhetik (Mobile Optimized)
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; }
    .stButton>button { 
        background-color: #111; color: #00ff41; border: 1px solid #00ff41; 
        width: 100%; border-radius: 4px; height: 3.5em; font-weight: bold;
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
    st.error("SYSTEM FEHLER: Google API-Key fehlt in den Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Modell-Konfiguration (Gemini 2.5 Flash für schnelle Inferenz)
TEXT_MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

# --- BILDGENERATOR (POLLINATIONS.AI - GRATIS) ---
def generate_visual(prompt):
    """Generiert eine Bild-URL via Pollinations.ai (Kostenlos)."""
    # Sektor 4 Stil-Vorgaben
    style = "cinematic steampunk cyberpunk, dark rainy atmosphere, neon green accents, ultra-detailed, 9:16 vertical, no humans"
    full_prompt = f"{prompt}, {style}"
    
    encoded = urllib.parse.quote(full_prompt)
    seed = random.randint(0, 1000000)
    
    # 9:16 Format (540x960)
    image_url = f"https://pollinations.ai/p/{encoded}?width=540&height=960&seed={seed}&nologo=true"
    
    st.session_state.current_image = image_url
    return image_url

# --- NARRATIVE ENGINE (GEMINI) ---
def call_gemini(prompt):
    """Ruft Gemini mit Exponential Backoff auf (gegen 429-Fehler)."""
    model = genai.GenerativeModel(TEXT_MODEL_NAME)
    delays = [1, 2, 4, 8, 16]
    
    for i, delay in enumerate(delays):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) and i < len(delays) - 1:
                time.sleep(delay)
                continue
            raise e
    return "Verbindung zur Matrix verloren."

# --- SESSION STATE ---
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
    st.session_state.display_text = "SYSTEM BEREIT. Bitte 'System Boot' eingeben."
    st.session_state.current_image = None
    st.session_state.matrix = {"Y": "Prekär", "X": "Tradition", "T": 10}
    st.session_state.round = 0

# --- CORE LOGIK ---
def run_engine(user_input):
    directive = """[SYSTEM OVERRIDE: SEKTOR 4 ENGINE]
Du bist die "Sektor 4 Engine", ein unerbittlicher Game Master.
NUTZE DIE 4D-MATRIX: [Y] Kapital, [X] Habitus, [T] Stress (10-100).
REGELN:
1. Starte JEDE Antwort mit '📷 Kamera-Feed: [1 kurzer englischer Satz für die Bild-KI]'.
2. KEINE Menschen beschreiben oder generieren. Nur Maschinen und Tiere.
3. Struktur: Kamera-Feed, Kurze Story (KISS), Optionen (A, B, C), HUD.
4. Kapitel 1: Flucht vor dem Necromancer Krokodil.
"""
    try:
        with st.spinner("Synchronisiere mit der Matrix..."):
            prompt = f"{directive}\nUser: {user_input}\nMatrix: {st.session_state.matrix}\nHistorie: {st.session_state.chat_log[-2:]}"
            output_text = call_gemini(prompt)
            
            # Bild-Inferenz via Pollinations
            feed_match = re.search(r"📷 Kamera-Feed: (.*)", output_text)
            if feed_match:
                generate_visual(feed_match.group(1))
            elif user_input.upper() == "SYSTEM BOOT":
                generate_visual("A steampunk ginger cat with glowing green cybernetic eyes in a dark rainy alley")

            st.session_state.display_text = output_text
            st.session_state.chat_log.append({"role": "user", "content": user_input})
            st.session_state.chat_log.append({"role": "assistant", "content": output_text})
            st.session_state.round += 1
            
    except Exception as e:
        st.session_state.display_text = f"CRITICAL MATRIX CRASH: {str(e)}"

# --- UI LAYOUT ---

# 1. BILD (Visual-Feed)
if st.session_state.current_image:
    st.image(st.session_state.current_image, use_container_width=True)
    st.markdown('<div class="synthid-badge">POLLINATIONS.AI // ZERO-BUDGET VERIFIED</div>', unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="width:100%; height:400px; background:#111; border:1px solid #333; 
        display:flex; align-items:center; justify-content:center; color:#333;">
        [KAMERA-FEED OFFLINE]
        </div>
        """, unsafe_allow_html=True)

# 2. TERMINAL AUSGABE
st.markdown("---")
st.markdown(st.session_state.display_text)

# 3. INTERAKTION (Buttons)
st.write("")
c1, c2, c3 = st.columns(3)
if c1.button("A"): run_engine("A"); st.rerun()
if c2.button("B"): run_engine("B"); st.rerun()
if c3.button("C"): run_engine("C"); st.rerun()

# 4. KONSOLENEINGABE
cmd = st.chat_input("Befehl eingeben...")
if cmd:
    run_engine(cmd)
    st.rerun()

# 5. SIDEBAR (HUD)
with st.sidebar:
    st.header("⚙️ System-HUD")
    st.write(f"Inferenz-Knoten: {TEXT_MODEL_NAME}")
    st.write("Bild-Engine: Pollinations (Gratis)")
    st.write(f"Runde: {st.session_state.round}/10")
    st.progress(st.session_state.matrix["T"] / 100, text=f"T-Load: {st.session_state.matrix['T']}%")
    
    if st.button("Matrix Reset"):
        st.session_state.clear()
        st.rerun()
