import streamlit as st
import google.generativeai as genai
import time
import re
import requests
import base64
import io
from PIL import Image

# Author: Murat Zengin
# Project: Questbook Killswitch
# Module: V74 Master Core (Stable Inferenz)

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

# Wir nutzen die vom System vorgegebenen Modelle für 2026
TEXT_MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
IMAGE_MODEL_NAME = "imagen-4.0-generate-001"
API_KEY = st.secrets["GOOGLE_API_KEY"]

# --- HILFSFUNKTIONEN FÜR STABILITÄT (BACKOFF) ---

def call_text_api_with_backoff(prompt):
    """Ruft die Gemini Text API mit Exponential Backoff auf (1, 2, 4, 8, 16s)."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{TEXT_MODEL_NAME}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": "Du bist die Sektor 4 Engine. Antworte kurz, zynisch und nutze Emojis."}]}
    }
    
    delays = [1, 2, 4, 8, 16]
    for i, delay in enumerate(delays):
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 429:
                time.sleep(delay)
                continue
            response.raise_for_status()
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            if i == len(delays) - 1:
                raise e
            time.sleep(delay)
    return "Fehler bei der Inferenz."

def generate_image_with_backoff(prompt):
    """Ruft die Imagen API mit Exponential Backoff auf."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{IMAGE_MODEL_NAME}:predict?key={API_KEY}"
    payload = {
        "instances": {"prompt": f"vertical 9:16 aspect ratio, cyberpunk, steampunk, no humans, {prompt}"},
        "parameters": {"sampleCount": 1}
    }
    
    delays = [1, 2, 4, 8, 16]
    for i, delay in enumerate(delays):
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 429:
                time.sleep(delay)
                continue
            response.raise_for_status()
            result = response.json()
            img_b64 = result['predictions'][0]['bytesBase64Encoded']
            st.session_state.current_image = img_b64
            return img_b64
        except Exception as e:
            if i == len(delays) - 1:
                return None
            time.sleep(delay)
    return None

# --- SESSION STATE ---
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
    st.session_state.display_text = "SYSTEM BEREIT. Bitte 'System Boot' eingeben."
    st.session_state.current_image = None
    st.session_state.matrix = {"Y": "Unbekannt", "X": "Unbekannt", "T": 10}
    st.session_state.round = 0

# --- ENGINE LOGIK ---
def run_engine(user_input):
    directive = f"""[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM]
Du bist die "Sektor 4 Engine".
4D-MATRIX: [Y] Kapital, [X] Habitus, [T] Stress (10-100).
REGELN:
1. Starte mit '📷 Kamera-Feed: [1 Satz]'.
2. KEINE Menschen.
3. Kapitel 1: Flucht vor dem Necromancer Krokodil.
User wählt: {user_input} | Status: {st.session_state.matrix}
"""
    
    try:
        with st.spinner("Synchronisiere Matrix..."):
            output_text = call_text_api_with_backoff(directive)
            
            # Bild-Prompt Parsing
            feed_match = re.search(r"📷 Kamera-Feed: (.*)", output_text)
            if feed_match:
                generate_image_with_backoff(feed_match.group(1))
            elif user_input.upper() == "SYSTEM BOOT":
                generate_image_with_backoff("A steampunk cat with glowing eyes in a rainy alley")
            
            st.session_state.display_text = output_text
            st.session_state.round += 1
    except Exception as e:
        st.session_state.display_text = f"CRITICAL MATRIX CRASH: {str(e)}"

# --- UI LAYOUT ---

# 1. BILD (Mandatory Image-First)
if st.session_state.current_image:
    st.image(base64.b64decode(st.session_state.current_image), use_container_width=True)
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
    st.write(f"Inferenz: {TEXT_MODEL_NAME}")
    st.write(f"Runde: {st.session_state.round}/10")
    st.progress(st.session_state.matrix["T"] / 100, text=f"ALI (Stress): {st.session_state.matrix['T']}%")
    if st.button("Matrix Reset"):
        st.session_state.clear()
        st.rerun()
