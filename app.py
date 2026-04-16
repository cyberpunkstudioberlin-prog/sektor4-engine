import streamlit as st
import google.generativeai as genai
import time
import re
import requests
import io
from openai import OpenAI

# Author: Murat Zengin
# Project: Questbook Killswitch
# Module: V75 OpenAI DALL-E 3 Hybrid Core

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
if "GOOGLE_API_KEY" not in st.secrets or "OPENAI_API_KEY" not in st.secrets:
    st.error("SYSTEM ERROR: API-Keys (Google/OpenAI) fehlen in den Secrets.")
    st.stop()

# Initialisiere Clients
openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
API_KEY_GOOGLE = st.secrets["GOOGLE_API_KEY"]
TEXT_MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

# --- BILDGENERATOR (DALL-E 3) ---
def generate_dalle_visual(prompt):
    """Generiert ein 9:16 Bild (1024x1792) via DALL-E 3."""
    safety_prompt = (
        f"Cyberpunk steampunk style, dark rainy atmosphere, cinematic lighting. "
        f"STRICTLY NO HUMANS. Focus on mechanical parts, drones, or a steampunk cat: {prompt}"
    )
    try:
        with st.spinner("DALL-E 3 berechnet Visual-Asset..."):
            response = openai_client.images.generate(
                model="dall-e-3",
                prompt=safety_prompt,
                size="1024x1792", # Natives Hochformat
                quality="hd",
                n=1
            )
            image_url = response.data[0].url
            st.session_state.current_image = image_url
            return image_url
    except Exception as e:
        st.sidebar.error(f"DALL-E Inferenz fehlgeschlagen: {str(e)}")
        return None

# --- TEXTGENERATOR (GEMINI MIT BACKOFF) ---
def call_gemini_text(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{TEXT_MODEL_NAME}:generateContent?key={API_KEY_GOOGLE}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    delays = [1, 2, 4, 8, 16]
    for i, delay in enumerate(delays):
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 429:
                time.sleep(delay)
                continue
            response.raise_for_status()
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            if i == len(delays) - 1: raise e
            time.sleep(delay)
    return "Fehler in der Matrix-Verbindung."

# --- SESSION STATE ---
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
    st.session_state.display_text = "SYSTEM BEREIT. Bitte 'System Boot' eingeben."
    st.session_state.current_image = None
    st.session_state.matrix = {"Y": "Unbekannt", "X": "Unbekannt", "T": 10}
    st.session_state.round = 0

# --- ENGINE LOGIK ---
def run_engine(user_input):
    directive = """[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM]
Du bist die "Sektor 4 Engine". Nutze die 4D-Matrix: [Y] Kapital, [X] Habitus, [T] Stress.
Stress (T) startet bei 10. Killswitch bei 100 = GAME OVER.
REGELN: 
1. Starte IMMER mit '📷 Kamera-Feed: [1 atmosphärischer Satz]'. 
2. KEINE Menschen. 
3. Kapitel 1: Flucht vor dem Necromancer Krokodil.
"""
    
    try:
        with st.spinner("Inferenz läuft..."):
            # Text generieren
            prompt = f"{directive}\nUser: {user_input}\nMatrix: {st.session_state.matrix}\nHistorie: {st.session_state.chat_log[-2:]}"
            output_text = call_gemini_text(prompt)
            
            # Bild-Prompt extrahieren & generieren
            feed_match = re.search(r"📷 Kamera-Feed: (.*)", output_text)
            if feed_match:
                generate_dalle_visual(feed_match.group(1))
            elif user_input.upper() == "SYSTEM BOOT":
                generate_dalle_visual("A steampunk cat on a neon-lit rooftop in the rain.")

            st.session_state.display_text = output_text
            st.session_state.chat_log.append({"role": "user", "content": user_input})
            st.session_state.chat_log.append({"role": "assistant", "content": output_text})
            st.session_state.round += 1
    except Exception as e:
        st.session_state.display_text = f"CRITICAL MATRIX CRASH: {str(e)}"

# --- UI LAYOUT ---

# 1. BILD (DALL-E URL)
if st.session_state.current_image:
    st.image(st.session_state.current_image, use_container_width=True)
    st.markdown('<div class="synthid-badge">OPENAI DALL-E 3 // SYNTHID VERIFIED</div>', unsafe_allow_html=True)
else:
    st.markdown("""<div style="width:100%; height:400px; background:#111; border:1px solid #333; 
        display:flex; align-items:center; justify-content:center; color:#333;">[KAMERA-FEED OFFLINE]</div>""", unsafe_allow_html=True)

# 2. TEXT
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
    run_engine(cmd)
    st.rerun()

# 5. SIDEBAR
with st.sidebar:
    st.header("⚙️ System-HUD")
    st.write(f"Inferenz: {TEXT_MODEL_NAME}")
    st.write(f"Visuals: DALL-E 3 (HD)")
    st.write(f"Runde: {st.session_state.round}/10")
    st.progress(st.session_state.matrix["T"] / 100, text=f"ALI (Stress): {st.session_state.matrix['T']}%")
    if st.button("Matrix Reset"):
        st.session_state.clear()
        st.rerun()
