import streamlit as st
import google.generativeai as genai
import json
import base64

# --- 1. KONFIGURATION & DESIGN ---
st.set_page_config(
    page_title="Sektor 4 Engine // Questbook Killswitch", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# CSS für das eiskalte Berlin-Dystopie Design (basierend auf Projekt-Vorgaben)
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

# API-Key Sicherheit (Streamlit Secrets)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("🚨 API-KEY FEHLT: Bitte in Streamlit Cloud unter Settings -> Secrets 'GEMINI_API_KEY' eintragen.")

# --- 2. SYSTEM-PROMPT (Striktes Inferenz-Regelwerk) ---
# [span_1](start_span)[span_2](start_span)Integriert alle Regeln aus der Sektor 4 Engine Dokumentation[span_1](end_span)[span_2](end_span)
FULL_SYSTEM_PROMPT = """
[span_3](start_span)Rolle: Du bist die Sektor 4 Engine, ein deterministisches Inferenz-System für das Textadventure "Questbook Killswitch".[span_3](end_span)
[span_4](start_span)Stil: Eiskalt, analytisch, zynisch und absolut direkt (KISS-Prinzip).[span_4](end_span)

WICHTIG: Du MUSST zwingend im validen JSON-Format antworten. 
Struktur:
{
  [span_5](start_span)"kamera": "[1 technischer Status-Satz zum visuellen Input der Umgebung]",[span_5](end_span)
  [span_6](start_span)"narrativ": "[Max. 3 Sätze. Aggressiv, physisch, klaustrophobisch. Zeitdruck erzeugen.]",[span_6](end_span)
  [span_7](start_span)"kater_log": "[1-2 zynische Sätze der Felinen Anomalie mit überlebenswichtigen Hinweisen.]",[span_7](end_span)
  "optionen": {
    "A": {"text": "[Text]", "fokus": "[Kapital/Habitus]"},
    "B": {"text": "[Text]", "fokus": "[Kapital/Habitus]"}
  },
  "hud_update": {
    [span_8](start_span)"t_load_neu": [Integer 0-100: BERECHNE den neuen Stresswert basierend auf Habitus-Konformität],[span_8](end_span)
    "kommentar": "[Kurze Begründung der kognitiven Dissonanz]"
  }
}

🛠️ SPIEL-MECHANIK:
- [span_9](start_span)Kein RNG: Konsequenzen basieren rein logisch auf Optionen und Habitus.[span_9](end_span)
- [span_10](start_span)[span_11](start_span)T-Load (Stress): Startet bei 10. Steigt bei jeder Aktion, massiv bei Handeln gegen den Habitus.[span_10](end_span)[span_11](end_span)
- Phasen: 
  [span_12](start_span)Runde 1-4 (Die Jagd): Mechanische Zombie-Kuscheltiere.[span_12](end_span)
  [span_13](start_span)Runde 5-7 (Eskalation): Necromancer Krokodil destabilisiert alles.[span_13](end_span)
  Runde 8-10 (Kollaps): Realität zerreißt zu Code-Glitches. [span_14](start_span)[span_15](start_span)Red Room Enthüllung.[span_14](end_span)[span_15](end_span)
"""

# --- 3. KI-KERNFUNKTIONEN ---
def call_gemini_json(prompt, system_instruction):
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash", # Für schnelle, strukturierte Inferenz
            system_instruction=system_instruction,
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        return {
            "kamera": "Gestört.", "narrativ": "Systemfehler.", "kater_log": "'Selbst die Matrix blutet.'",
            "optionen": {"A": {"text": "Reboot", "fokus": "System"}},
            "hud_update": {"t_load_neu": st.session_state.t_load, "kommentar": "Error"}
        }

def generate_image(prompt):
    try:
        # [span_16](start_span)Nutzung von Imagen 3 für die Cyberpunk-Steampunk Visuals[span_16](end_span)
        model = genai.GenerativeModel("imagen-3.0-generate-002") 
        response = model.generate_content(prompt)
        if response.candidates[0].content.parts[0].inline_data:
            img_data = response.candidates[0].content.parts[0].inline_data.data
            return f"data:image/png;base64,{base64.b64encode(img_data).decode()}"
    except:
        return "https://via.placeholder.com/450x800.png?text=SEKTOR+4+SIGNAL+LOST"

# --- 4. ENGINE STATE MANAGEMENT ---
if 'round' not in st.session_state:
    st.session_state.update({
        'round': 0, 't_load': 10, 'kapital': None, 'habitus': None,
        'last_data': None, 'last_image': None
    })

def process_step(user_input):
    if st.session_state.round == 0:
        st.session_state.round = 1
        # [span_17](start_span)Habitus-Zuweisung basierend auf Startwahl[span_17](end_span)
        if "Konzern" in user_input: st.session_state.kapital, st.session_state.habitus = "Elite", "Anpassung"
        elif "Mechaniker" in user_input: st.session_state.kapital, st.session_state.habitus = "Gasse", "Tradition"
        else: st.session_state.kapital, st.session_state.habitus = "Prekär", "Disruption"
    else:
        st.session_state.round += 1

    # [span_18](start_span)Phasen-Kontext für die Bild-Inferenz[span_18](end_span)
    phase_context = "Industrial Berlin steampunk ruins, mechanical animals"
    if 5 <= st.session_state.round <= 7: phase_context = "Mechanical Necromancer crocodile in rusty infrastructure"
    elif st.session_state.round >= 8: phase_context = "Digital glitches, reality tearing to code, binary artifacts"

    img_prompt = f"Cyberpunk-Steampunk-Fusion, Berlin-Vibe, {phase_context}, 9:16 vertical, rusty, atmospheric. NO HUMANS, NO BLOOD."

    with st.spinner("🔄 Inferenz-Engine berechnet nächsten Zyklus..."):
        prompt = f"Spieler-Aktion: {user_input} | Status: Runde {st.session_state.round}, Habitus {st.session_state.habitus}, Kapital {st.session_state.kapital}, T-Load {st.session_state.t_load}"
        st.session_state.last_data = call_gemini_json(prompt, FULL_SYSTEM_PROMPT)
        st.session_state.t_load = st.session_state.last_data["hud_update"]["t_load_neu"]
        st.session_state.last_image = generate_image(img_prompt)

# --- 5. UI RENDERING ---
st.markdown("<div class='terminal-header'>📟 SEKTOR 4 ENGINE // QUESTBOOK KILLSWITCH V7.5</div>", unsafe_allow_html=True)

if st.session_state.t_load >= 100:
    st.error("🚨 KILLSWITCH TRIGGERED: T-LOAD 100%. BIO-EINHEIT ZERSTÖRT.")
    if st.button("REBOOT SYSTEM"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
else:
    col_vis, col_term = st.columns([1, 1.2])

    with col_vis:
        if st.session_state.last_image:
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
                st.caption(f"📷 {data['kamera']}")
                st.subheader(data['narrativ'])
                st.markdown(f"<div class='kater-log'>🐈 {data['kater_log']}</div>", unsafe_allow_html=True)
                
                for key, opt in data['optionen'].items():
                    if st.button(f"{key}) {opt['text']} [{opt['fokus']}]"):
                        process_step(opt['text'])
                        st.rerun()

            # [span_19](start_span)HUD Rendering[span_19](end_span)
            st.markdown("<div class='hud-container'>", unsafe_allow_html=True)
            st.write(f"📉 RUNDE: {st.session_state.round}/10 | KAPITAL: {st.session_state.kapital} | HABITUS: {st.session_state.habitus}")
            bar = "|" * (st.session_state.t_load // 5) + "-" * (20 - (st.session_state.t_load // 5))
            st.code(f"🧠 T-LOAD: [{bar}] {st.session_state.t_load}/100", language="text")
            if data: st.caption(f"Status-Zusammenfassung: {data['hud_update']['kommentar']}")
            st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<p style='text-align: center; color: #3f3f46; font-size: 0.7em; margin-top: 50px;'>Autor: Murat Zengin // Sektor 4 Engine Open Source</p>", unsafe_allow_html=True)
