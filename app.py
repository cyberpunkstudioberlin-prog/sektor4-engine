import streamlit as st
import time
import re
import urllib.parse
import random
import requests

# Author: Murat Zengin
# Projekt: Questbook Killswitch
# Modul: V81 Meta Llama Core (Groq Inferenz & Pollinations)

# --- UI INITIALISIERUNG ---
st.set_page_config(
    page_title="Questbook Killswitch x Llama 3", 
    page_icon="🦾", 
    layout="centered"
)

# Meta-Blue & Sektor 4 Green Hybrid Design
st.markdown("""
    <style>
    .stApp { background-color: #060709; color: #e4e6eb; font-family: 'Segoe UI', Helvetica, Arial, sans-serif; }
    .stButton>button { 
        background-color: #0084ff; color: white; border: none; 
        width: 100%; border-radius: 8px; height: 3.5em; font-weight: bold;
        transition: 0.2s ease;
    }
    .stButton>button:hover { background-color: #0073e6; transform: translateY(-2px); }
    .stChatInput { border-top: 1px solid #242526; }
    div[data-testid="stSidebar"] { background-color: #18191a; border-right: 1px solid #333; }
    .matrix-status { 
        color: #00ff41; font-family: 'Courier New', monospace; 
        background: rgba(0, 255, 65, 0.1); padding: 10px; border-radius: 5px; border-left: 3px solid #00ff41;
    }
    .meta-tag {
        font-size: 0.7rem; color: #0084ff; border: 1px solid #0084ff;
        padding: 2px 6px; border-radius: 4px; font-weight: bold; margin-bottom: 10px; display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Questbook Killswitch 🦾")
st.markdown('<div class="meta-tag">INFERENZ: META LLAMA 3 (VIA GROQ)</div>', unsafe_allow_html=True)

# --- API KONFIGURATION (GROQ FÜR LLAMA 3) ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("SYSTEM ERROR: GROQ_API_KEY fehlt in den Secrets.")
    st.info("Hol dir einen kostenlosen Key auf console.groq.com")
    st.stop()

GROQ_KEY = st.secrets["GROQ_API_KEY"]
MODEL_NAME = "llama3-70b-8192" # Das leistungsstarke Llama 3 Modell

# --- BILDGENERATOR (POLLINATIONS - LLAMA STYLE) ---
def generate_visual(prompt):
    """Erzeugt 9:16 Visuals im Meta-Look (Gratis)."""
    style = "hyper-realistic cinematic, Meta AI aesthetic, photorealistic, 9:16, dark cyberpunk steampunk, ginger cat, no humans"
    full_prompt = f"{prompt}, {style}"
    encoded = urllib.parse.quote(full_prompt)
    seed = random.randint(0, 10**6)
    url = f"https://pollinations.ai/p/{encoded}?width=540&height=960&seed={seed}&nologo=true"
    st.session_state.current_image = url
    return url

# --- NARRATIVE ENGINE (LLAMA 3 VIA GROQ REST API) ---
def call_llama_inference(prompt):
    """Ruft Llama 3 via Groq API auf."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Du bist die Sektor 4 Engine. Dein Stil ist der von Meta AI (Llama 3): Klar, präzise, analytisch. Nutze Emojis am Satzanfang. Halte dich kurz. KEINE MENSCHEN."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 512
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"CRITICAL MATRIX ERROR: {str(e)}"

# --- SESSION STATE ---
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
    st.session_state.display_text = "SYSTEM BEREIT. Inferenz-Knoten Llama 3 online. Bitte 'System Boot' eingeben."
    st.session_state.current_image = None
    st.session_state.matrix = {"Y": "Basis", "X": "Neutral", "T": 10}
    st.session_state.round = 0

# --- CORE LOGIK ---
def run_engine(user_input):
    directive = """[SYSTEM OVERRIDE: META LLAMA 3 GM]
Berechne die 4D-Matrix: [Y] Kapital, [X] Habitus, [T] Stress (10-100).
Kapitel 1: Flucht vor dem Necromancer Krokodil.
Regeln: 1. Start mit '📷 Kamera-Feed: [1 Satz]'. 2. Keine Menschen. 3. Struktur: Feed, Story, Optionen (A, B, C), HUD.
"""
    try:
        with st.spinner("Llama 3 berechnet Inferenz-Vektoren..."):
            prompt = f"{directive}\nMatrix: {st.session_state.matrix}\nUser: {user_input}\nHistorie: {st.session_state.chat_log[-2:]}"
            output_text = call_llama_inference(prompt)
            
            # Bild-Inferenz
            feed_match = re.search(r"📷 Kamera-Feed: (.*)", output_text)
            if feed_match:
                generate_visual(feed_match.group(1))
            elif user_input.upper() == "SYSTEM BOOT":
                generate_visual("A futuristic steampunk cat with blue glowing eyes, rainy city background")

            st.session_state.display_text = output_text
            st.session_state.chat_log.append({"role": "user", "content": user_input})
            st.session_state.chat_log.append({"role": "assistant", "content": output_text})
            st.session_state.round += 1
    except Exception as e:
        st.session_state.display_text = f"MATRIX COLLAPSE: {str(e)}"

# --- UI LAYOUT ---

# 1. BILD
if st.session_state.current_image:
    st.image(st.session_state.current_image, use_container_width=True)
    st.markdown('<div class="meta-tag">GENERATED BY SEKTOR 4 VISUALS (FREE)</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="height:350px; background:#1c1e21; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#444;">[KAMERA-FEED OFFLINE]</div>', unsafe_allow_html=True)

# 2. TEXT
st.markdown("---")
st.markdown(f'<div class="matrix-status">{st.session_state.display_text}</div>', unsafe_allow_html=True)

# 3. INTERAKTION
st.write("")
c1, c2, c3 = st.columns(3)
if c1.button("A"): run_engine("A"); st.rerun()
if c2.button("B"): run_engine("B"); st.rerun()
if c3.button("C"): run_engine("C"); st.rerun()

# 4. INPUT
cmd = st.chat_input("Konsolenbefehl...")
if cmd:
    run_engine(cmd)
    st.rerun()

# 5. SIDEBAR
with st.sidebar:
    st.header("⚙️ Meta-HUD")
    st.write(f"Inferenz: {MODEL_NAME}")
    st.write(f"Runde: {st.session_state.round}/10")
    st.progress(st.session_state.matrix["T"] / 100, text=f"T-Load: {st.session_state.matrix['T']}%")
    if st.button("System Reset"):
        st.session_state.clear()
        st.rerun()
