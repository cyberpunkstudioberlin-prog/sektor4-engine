import streamlit as st
from google import genai
from google.genai import types
import json
import base64
import os

# --- 1. KONFIGURATION & DESIGN ---
st.set_page_config(
    page_title="Sektor 4 Engine // Questbook Killswitch", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# CSS für das eiskalte Berlin-Dystopie Design
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #d4d4d8; font-family: 'Courier New', monospace; }
    .terminal-header { color: #eab308; font-weight: bold; border-bottom: 1px solid #3f3f46; padding-bottom: 10px; margin-bottom: 20px; font-size: 1.2em; text-transform: uppercase; letter-spacing: 2px; }
    .kater-log { font-style: italic; color: #a1a1aa; border-left: 2px solid #3f3f46; padding-left: 15px; margin: 20px 0; background: rgba(255,255,255,0.02); padding-top: 10px; padding-bottom: 10px; }
    .hud-container { border: 1px solid #27272a; padding: 15px; background: rgba(10,10,10,0.9); margin-top: 20px; border-left: 4px solid #eab308; }
    .stButton>button { width: 100%; border: 1px solid #3f3f46; background: transparent; color: #d4d4d8; transition: 0.3s; padding: 12px; font-weight: bold; }
    .stButton>button:hover { border-color: #eab308; color: #eab308; background: rgba(234, 179, 8, 0.05); }
    </style>
""", unsafe_allow_html=True)

# API-Client Setup
if "GEMINI_API_KEY" in st.secrets:
    # Saubere Übergabe des Keys an das neue SDK
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("🚨 API-KEY FEHLT: Bitte in Streamlit Cloud Secrets 'GEMINI_API_KEY' eintragen.")
    st.stop()

# --- 2. SYSTEM-PROMPT ---
FULL_SYSTEM_PROMPT = """
Rolle: Du bist die Sektor 4 Engine, ein deterministisches Inferenz-System für das Textadventure "Questbook Killswitch".
Stil: Eiskalt, analytisch, zynisch und direkt.

WICHTIG: Du MUSST zwingend im validen JSON-Format antworten. 
Struktur:
{
  "kamera": "[Status-Satz]",
  "narrativ": "[Max. 3 Sätze]",
  "kater_log": "[Zynischer Hinweis]",
  "optionen": {
    "A": {"text": "[Text]", "fokus": "[Fokus]"},
    "B": {"text": "[Text]", "fokus": "[Fokus]"}
  },
  "hud_update": {
    "t_load_neu": [Zahl 0-100],
    "kommentar": "[Grund]"
  }
}
"""

# --- 3. KI-KERNFUNKTIONEN ---
def call_gemini_json(prompt, system_instruction):
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash', # KORREKTUR: Stabiles Modell für fehlerfreie Inferenz
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.1 # Stellt sicher, dass das System analytisch und weniger "zufällig" agiert
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {
            "kamera": f"🚨 DIAGNOSE: {str(e)}", 
            "narrativ": "Die Matrix blockiert den Zugriff. Prüfe den Fehler-Code im Kamera-Feed.", 
            "kater_log": "'Das System wehrt sich gegen die Inferenz.'",
            "optionen": {"A": {"text": "Neu kalibrieren", "fokus": "System"}},
            "hud_update": {"t_load_neu": st.session_state.t_load, "kommentar": "Fehler-Modus"}
        }

def generate_image(prompt):
    try:
        result = client.models.generate_images(
            model='imagen-3.0-generate-001', # KORREKTUR: Stabiles Standard-Modell für Imagen
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="9:16"
            )
        )
        if result.generated_images:
            image_bytes = result.generated_images[0].image.image_bytes
            return f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}"
    except Exception:
        # Fängt Fehler ab, falls die Bildgenerierung ausfällt, damit das Spiel weiterläuft
        return None

# --- 4. ENGINE STATE MANAGEMENT ---
if 'round' not in st.session_state:
    st.session_state.update({
        'round': 0, 't_load': 10, 'kapital': None, 'habitus': None,
        'last_data': None, 'last_image': None
    })

def process_step(user_input):
    if st.session_state.round == 0:
        st.session_state.round = 1
        if "Konzern" in user_input: 
            st.session_state.kapital, st.session_state.habitus = "Elite", "Anpassung"
        elif "Mechaniker" in user_input: 
            st.session_state.kapital, st.session_state.habitus = "Gasse", "Tradition"
        else: 
            st.session_state.kapital, st.session_state.habitus = "Prekär", "Disruption"
    else:
        st.session_state.round += 1

    img_prompt = f"Cyberpunk-Steampunk Berlin, industrial ruins, atmospheric, rusty, no humans. 9:16 portrait."

    with st.spinner("🔄 Inferenz-Engine berechnet nächsten Zyklus..."):
        prompt = f"Spieler-Aktion: {user_input} | Status: Runde {st.session_state.round}, Habitus {st.session_state.habitus}, Kapital {st.session_state.kapital}, T-Load {st.session_state.t_load}"
        st.session_state.last_data = call_gemini_json(prompt, FULL_SYSTEM_PROMPT)
        st.session_state.t_load = st.session_state.last_data.get("hud_update", {}).get("t_load_neu", st.session_state.t_load)
        st.session_state.last_image = generate_image(img_prompt)

# --- 5. UI RENDERING ---
st.markdown("<div class='terminal-header'>📟 SEKTOR 4 ENGINE // QUESTBOOK KILLSWITCH V7.5</div>", unsafe_allow_html=True)

if st.session_state.t_load >= 100:
    st.error("🚨 KILLSWITCH TRIGGERED: T-LOAD 100%. BIO-EINHEIT ZERSTÖRT.")
    if st.button("REBOOT SYSTEM"):
        for key in list(st.session_state.keys()): 
            del st.session_state[key]
        st.rerun()
else:
    col_vis, col_term = st.columns([1, 1.2])

    with col_vis:
        if st.session_state.last_image:
            # use_container_width ist der aktuelle Streamlit-Standard
            st.image(st.session_state.last_image, use_container_width=True) 
        else:
            st.info("Kamera-Feed offline. Warte auf Inferenz...")

    with col_term:
        if st.session_state.round == 0:
            st.write("Sektor 4 Inception. Wähle deine Herkunft:")
            if st.button("A) Konzern-Aussteiger (Elite/Anpassung)"): process_step("Konzern-Aussteiger")
            if st.button("B) Mechaniker der Gosse (Gasse/Tradition)"): process_step("Mechaniker der Gosse")
            if st.button("C) System-Glitch (Prekär/Disruption)"): process_step("System-Glitch")
        else:
            data = st.session_state.last_data
            if data:
                # Sichere Abfrage mit .get() falls das Modell von der Struktur abweicht
                st.caption(f"📷 {data.get('kamera', 'Feed offline')}")
                st.subheader(data.get('narrativ', '...'))
                st.markdown(f"<div class='kater-log'>🐈‍⬛ {data.get('kater_log', '...')}</div>", unsafe_allow_html=True)
                
                if 'optionen' in data:
                    for key, opt in data['optionen'].items():
                        if st.button(f"{key}) {opt.get('text', 'Unbekannter Vektor')} [{opt.get('fokus', '???')}]"):
                            process_step(opt.get('text', ''))
                            st.rerun()

            st.markdown("<div class='hud-container'>", unsafe_allow_html=True)
            st.write(f"📉 RUNDE: {st.session_state.round}/10 | KAPITAL: {st.session_state.kapital} | HABITUS: {st.session_state.habitus}")
            # Verhindere Fehler, falls T-Load über 100 geht vor dem Reboot-Screen
            display_tload = min(st.session_state.t_load, 100) 
            bar = "|" * (display_tload // 5) + "-" * (20 - (display_tload // 5))
            st.code(f"🧠 T-LOAD: [{bar}] {st.session_state.t_load}/100", language="text")
            if data and 'hud_update' in data: 
                st.caption(f"Status-Zusammenfassung: {data['hud_update'].get('kommentar', '')}")
            st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<p style='text-align: center; color: #3f3f46; font-size: 0.7em; margin-top: 50px;'>Autor: Murat Zengin // Sektor 4 Engine (Open Source)</p>", unsafe_allow_html=True)
        
