import streamlit as st
import google.generativeai as genai
import time
import re
import urllib.parse
import random
import requests

# Autor: Murat Zengin
# Projekt: Questbook Killswitch
# Modul: V82 Meta-Elite Core (Llama 3 + Hugging Face FLUX)
# Sprache: Deutsch (UI & Kommentare)

# --- UI INITIALISIERUNG ---
st.set_page_config(
    page_title="Questbook Killswitch x Meta AI", 
    page_icon="🦾", 
    layout="centered"
)

# Meta & Sektor 4 High-End Design (Mobile Optimiert)
st.markdown("""
    <style>
    .stApp { background-color: #060709; color: #e4e6eb; font-family: 'Segoe UI', Tahoma, sans-serif; }
    .stButton>button { 
        background-color: #0084ff; color: white; border: none; 
        width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold;
        transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton>button:hover { background-color: #0073e6; transform: scale(1.02); box-shadow: 0 4px 15px rgba(0, 132, 255, 0.3); }
    .matrix-display { 
        color: #00ff41; font-family: 'Courier New', monospace; 
        background: #18191a; padding: 20px; border-radius: 10px; border: 1px solid #333;
        box-shadow: inset 0 0 10px rgba(0, 255, 65, 0.05);
        white-space: pre-wrap;
    }
    .meta-label {
        font-size: 0.75rem; color: #0084ff; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Questbook Killswitch 🦾")
st.markdown('<div class="meta-label">Meta AI Ecosystem Integration // Sektor 4</div>', unsafe_allow_html=True)

# --- API KONFIGURATION ---
# Prüfung der notwendigen Secrets
if "GROQ_API_KEY" not in st.secrets or "HF_TOKEN" not in st.secrets or "GOOGLE_API_KEY" not in st.secrets:
    st.error("SYSTEM FEHLER: API-Keys fehlen in den Secrets.")
    st.stop()

# --- BILDKNOTEN (HUGGING FACE - FLUX.1) ---
def generate_meta_visual(prompt):
    """Generiert High-End Visuals über Hugging Face (Gratis via FLUX.1)."""
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
    
    # Sektor 4 Stil-Vorgaben für die Bild-KI
    style = "cinematic photorealistic cyberpunk steampunk, high detail, Meta AI Imagine style, dark rain, 9:16 aspect ratio, no humans"
    payload = {"inputs": f"{prompt}, {style}"}

    try:
        with st.spinner("Meta-Visual Inferenz wird berechnet..."):
            response = requests.post(API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                st.session_state.current_image = response.content
                return response.content
            else:
                # Fallback auf Pollinations.ai bei HF Überlastung
                encoded = urllib.parse.quote(f"{prompt}, {style}")
                url = f"https://pollinations.ai/p/{encoded}?width=540&height=960&nologo=true"
                st.session_state.current_image = url
                return url
    except Exception as e:
        st.sidebar.error(f"Bildfehler: {str(e)}")
        return None

# --- NARRATIVE ENGINE (LLAMA 3 ÜBER GROQ) ---
def call_llama(user_input):
    """Ruft Meta Llama 3 über die Groq API auf."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}", 
        "Content-Type": "application/json"
    }
    
    directive = """[SYSTEM OVERRIDE: SEKTOR 4 ENGINE]
    Du bist der GM von Questbook Killswitch.
    MATRIX: [Y] Kapital, [X] Habitus, [T] Stress (ALI).
    REGELN:
    1. Starte JEDE Antwort mit '📷 Kamera-Feed: [1 Satz auf Englisch für die Bild-KI]'.
    2. Absolut KEINE Menschen beschreiben oder generieren.
    3. Struktur: Kamera-Feed, Kurze Story (KISS), Optionen A/B/C, HUD.
    Sprache der Geschichte: Deutsch.
    """
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": directive},
            {"role": "user", "content": f"Aktion: {user_input} | Matrix: {st.session_state.matrix}"}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Fehler in der Meta-Matrix: {str(e)}"

# --- SESSION STATUS ---
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
    st.session_state.display_text = "SYSTEM BEREIT. Meta-Inferenz online. Drücke 'System Start'."
    st.session_state.current_image = None
    st.session_state.matrix = {"Y": "Basis", "X": "Neutral", "T": 10}
    st.session_state.round = 0

# --- ENGINE START ---
def run_engine(user_input):
    try:
        with st.spinner("Matrix-Vektoren werden analysiert..."):
            output = call_llama(user_input)
            
            # Bild-Prompt extrahieren
            feed_match = re.search(r"📷 Kamera-Feed: (.*)", output)
            if feed_match:
                generate_meta_visual(feed_match.group(1))
            elif user_input.upper() == "SYSTEM START":
                generate_meta_visual("A futuristic steampunk ginger cat with blue eyes in the rain")
            
            st.session_state.display_text = output
            st.session_state.chat_log.append(user_input)
            st.session_state.round += 1
    except:
        st.session_state.display_text = "VERBINDUNGS-FEHLER ZUR MATRIX."

# --- UI LAYOUT ---

# 1. VISUAL (Hochformat 9:16)
if st.session_state.current_image:
    if isinstance(st.session_state.current_image, bytes):
        st.image(st.session_state.current_image, use_container_width=True)
    else:
        st.image(st.session_state.current_image, use_container_width=True)
    st.markdown('<div class="meta-label" style="text-align:center;">IMAGINE BY META-ELITE // SEKTOR 4</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="height:350px; background:#111; border-radius:15px; display:flex; align-items:center; justify-content:center; color:#333; border: 1px solid #333;">[KAMERA-FEED OFFLINE]</div>', unsafe_allow_html=True)

# 2. TERMINAL AUSGABE
st.markdown("---")
st.markdown(f'<div class="matrix-display">{st.session_state.display_text}</div>', unsafe_allow_html=True)

# 3. INTERAKTION (A/B/C Buttons)
st.write("")
c1, c2, c3 = st.columns(3)
if c1.button("A"): run_engine("A"); st.rerun()
if c2.button("B"): run_engine("B"); st.rerun()
if c3.button("C"): run_engine("C"); st.rerun()

# 4. KONSOLENEINGABE
cmd = st.chat_input("Befehl eingeben...")
if cmd:
    if cmd.upper() == "SYSTEM START":
        run_engine("SYSTEM START")
    else:
        run_engine(cmd)
    st.rerun()

# 5. SIDEBAR (HUD)
with st.sidebar:
    st.header("⚙️ Meta-HUD")
    st.write(f"Runde: {st.session_state.round}/10")
    st.progress(st.session_state.matrix.get("T", 10) / 100, text=f"Stress (ALI): {st.session_state.matrix.get('T', 10)}%")
    
    st.markdown("---")
    st.markdown("**4D-Matrix Werte:**")
    st.write(f"Kapital (Y): {st.session_state.matrix.get('Y')}")
    st.write(f"Habitus (X): {st.session_state.matrix.get('X')}")
    
    if st.button("System Reset"):
        st.session_state.clear()
        st.rerun()
