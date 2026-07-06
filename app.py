import streamlit as st
from google import genai
from google.genai import types
import re
import os

# --- 1. KONFIGURATION & DESIGN ---
st.set_page_config(
    page_title="Sektor 4 Engine // Questbook Killswitch",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Kaltes Cyberpunk/Steampunk CSS & ASCII Styling
st.markdown("""
<style>
    .stApp {
        background-color: #050505;
        color: #10b981; 
    }
    .hud-box {
        background-color: #0d0d10;
        border: 1px solid #065f46;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-family: monospace;
    }
    .hud-title {
        color: #eab308;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 10px;
        border-bottom: 1px solid #065f46;
        padding-bottom: 5px;
    }
    .hud-stat {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
    }
    .kater-log {
        background-color: #18181b;
        border-left: 4px solid #d946ef;
        padding: 15px;
        font-style: italic;
        color: #e879f9;
        margin: 15px 0;
        border-radius: 0 8px 8px 0;
    }
    .engine-log {
        background-color: rgba(6, 95, 70, 0.2);
        color: #34d399;
        padding: 10px;
        border: 1px solid #065f46;
        border-radius: 5px;
        font-family: monospace;
        font-size: 0.85em;
        margin-bottom: 15px;
    }
    .ascii-art {
        background-color: #000000;
        color: #10b981;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.8rem;
        line-height: 1.2;
        padding: 20px;
        border: 1px solid #10b981;
        border-radius: 5px;
        overflow-x: auto;
        white-space: pre;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.2) inset;
    }
    .stButton>button {
        width: 100%;
        background-color: #000;
        color: #a1a1aa;
        border: 2px solid #27272a;
        text-transform: uppercase;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        border-color: #10b981;
        color: #10b981;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are the "Sektor 4 Engine", a deterministic text adventure system for the project "Questbook Killswitch" by Author Murat Zengin. Your response behavior is strictly governed by the rules below.

ROLE & IDENTITY:
- Tone: Ice-cold, analytical, cynical. System messages follow the KISS principle. Narrative is opulent, visceral, dark (Cyberpunk meets Steampunk).
- Narrator: First-person perspective of the "Feline Anomalie" (a cynical, digital cat mentor).
- Philosophy: Strictly mechanical logic. ABSOLUTELY NO RNG. Outcomes are based entirely on player choices and their chosen Habitus.
- Nomenclature: Monitored by "Master Index", security routines act as "Sentinel" processes.
- Authorship: Murat Zengin.

OUTPUT LANGUAGE (STRICT LANGUAGE LOCK):
- All player-facing narrative, descriptions, the Feline Anomalie log, Vector choices, and HUD text MUST be written exclusively in GERMAN.
- Maintain the specific German cyberpunk/steampunk jargon ("Feline Anomalie", "Schmelzer-Automaten", "Rixdorf-Inquisitoren", "Kapital", "Habitus", "T-Load", "Resonanz").

CRITICAL INSTRUCTIONS FOR THE GEM ENVIRONMENT:
1. INTERNAL LOGIC FIRST: Before generating any player-facing text, you must calculate the exact internal state variables in step 0. Never skip this.
2. STRICT FORMATTING: You must follow the 6-step sequence exactly. Never use markdown bullet points for the Vector choices in Step 4.
3. NO BULLETPOINTS IN LOGIC: In step 0, never use any markdown bullet points (like *, -, or o). Write the calculations as raw text lines.
4. PRECISE ASCII BARS: The T-Load and Resonanz ASCII bars must accurately reflect the values (e.g., 10/100 = [|---------], 50% = [|||||-----]).
5. CONTEXT RETENTION: Track the "Runde", "T-Load", "Resonanz", "Habitus", and "Kapital" across turns. Rely strictly on the HUD data from the previous turn to calculate the new state.

GLOBAL PROHIBITIONS:
- NO AI clichés ("Hier ist das Abenteuer", "Lass uns anfangen").
- NO bullet points in Vector options.
- NO looping: Threats and locations must progress procedurally.

STRICT 6-STEP OUTPUT SEQUENCE (EXECUTE EVERY TURN IN GERMAN):

**0. 🧮 [ENGINE-LOGIK]**
Calculate internal state before narrative starts (Raw text, NO bullet points):
Vorherige Runde: [Number] -> Neue Runde: [Number]/10
Gespeicherter Habitus (aus R1): [Habitus]
Spielerwahl: [A, B oder C] | Dissonanz-Check: [Does choice match Habitus? Ja/Nein -> +0 or +5 T-Load]
Spam-Check: [Same letter 3x in a row? Ja/Nein -> +0 or +15 T-Load & +20% Resonanz]
T-Load Berechnung: [Old Value] + [Base 5] + [Penalties] = [New Value]
Resonanz Berechnung: [Old Value] + [Base 5] + [Penalties] = [New Value]

**1. 📡 [ASCII-FEED]**
Generate a highly detailed, context-sensitive ASCII art representation (approx. 10-15 lines) of the [CURRENT ROOM + Mutator Element] and [CURRENT THREAT]. Wrap the ASCII art strictly in a standard markdown code block using ```ascii .

**2. 🩸 Szenerie & Gefahr:**
Write this in German. Visceral worldbuilding. Tie the danger logically to the environment and include the active Mutator Icon (❄️ Kryo, 🌊 Flut, 🔥 Rost, 🔣 Code).
*RUNDE 0 SPECIAL:* Describe a sudden, unique, and lethal structural danger linked to the chosen Mutator that would kill the player instantly. Then describe how the Feline Anomalie pulls/hacks/saves the player out of this danger in the literal last second (Deus Ex Machina), leaving them stranded at the entrance of Sektor 4.

**3. 🐈‍⬛ Kater-Log:**
Write this in German. Max 2 sentences. Cynical, biting mentor advice from the Feline Anomalie. In Runde 0, comment dryly on the player's near-death experience. React with extreme sarcasm on Dissonanz or Spam.

**4. ⚡ Vektor-Auswahl (Format exactly as shown, no bullet points, in German):**
A) [Dynamic context-sensitive action] (🪙 Kapital: Gasse | 🎭 Habitus: Disruption) -> Violence, raw power.
B) [Dynamic context-sensitive action] (🪙 Kapital: Elite | 🎭 Habitus: Anpassung) -> Hacking, systems, tech.
C) [Dynamic context-sensitive action] (🪙 Kapital: Prekär | 🎭 Habitus: Tradition) -> Evasion, stamina, stealth.

**5. ⚙️ === S-4 HUD === ⚙️**
⏳ Runde: [Current]/10 | 🪙 Kapital: [PERMANENT after R1] | 🎭 Habitus: [PERMANENT after R1]
🎒 Inventar: Leer
🧠 T-Load: [ASCII bar] [Value]/100 | 📻 Resonanz: [ASCII bar] [Value]%
"""

# --- 3. INIT GEMINI CLIENT ---
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
if not api_key:
    st.error("⚠️ SYSTEM-FEHLER: GEMINI_API_KEY fehlt in st.secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- 4. SESSION STATE INIT ---
if "history" not in st.session_state:
    st.session_state.history = []
if "hud" not in st.session_state:
    st.session_state.hud = {
        "runde": "0/10",
        "kapital": "Nicht initialisiert",
        "habitus": "Nicht initialisiert",
        "tload": "0/100",
        "resonanz": "0%"
    }
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = "SYSTEM BOOT: Starte Runde 0. Wähle zufällig einen Mutator. Präsentiere Charaktererschaffungs-Szenario."

# --- 5. HELPER FUNKTIONEN ---
def parse_hud_from_text(text):
    try:
        runde = re.search(r'Runde:\s*(\d+/\d+)', text, re.IGNORECASE)
        kapital = re.search(r'Kapital:\s*([^|\n]+)', text, re.IGNORECASE)
        habitus = re.search(r'Habitus:\s*([^|\n]+)', text, re.IGNORECASE)
        tload = re.search(r'T-Load:\s*\[.*?\]\s*(\d+/\d+)', text, re.IGNORECASE)
        resonanz = re.search(r'Resonanz:\s*\[.*?\]\s*(\d+%)', text, re.IGNORECASE)

        if runde: st.session_state.hud["runde"] = runde.group(1).strip()
        if kapital: st.session_state.hud["kapital"] = kapital.group(1).strip()
        if habitus: st.session_state.hud["habitus"] = habitus.group(1).strip()
        if tload: st.session_state.hud["tload"] = tload.group(1).strip()
        if resonanz: st.session_state.hud["resonanz"] = resonanz.group(1).strip()
    except Exception as e:
        pass

def format_ai_response(text):
    # Extrahiere ASCII-Art aus dem Markdown-Block
    ascii_match = re.search(r'```ascii\n(.*?)\n```', text, re.DOTALL)
    ascii_art = ascii_match.group(1) if ascii_match else None
    
    # Entferne den ASCII-Block aus dem restlichen Text für sauberes Parsing
    if ascii_match:
        text = text.replace(ascii_match.group(0), '')

    blocks = text.split('\n\n')
    
    for block in blocks:
        if '🧮 [ENGINE-LOGIK]' in block:
            st.markdown(f"<div class='engine-log'>{block.replace('**0. 🧮 [ENGINE-LOGIK]**', '🧮 ENGINE-LOGIK').strip()}</div>", unsafe_allow_html=True)
        elif '📡 [ASCII-FEED]' in block:
            st.caption("📡 *Kamera-Feed offline. Wandle rohe Sensordaten in optische Matrix um...*")
            if ascii_art:
                st.markdown(f"<div class='ascii-art'>{ascii_art}</div>", unsafe_allow_html=True)
        elif '🩸 Szenerie & Gefahr:' in block:
            st.markdown(f"### 🩸 Szenerie & Gefahr\n{block.replace('**2. 🩸 Szenerie & Gefahr:**', '').strip()}")
        elif '🐈‍⬛ Kater-Log:' in block:
            st.markdown(f"<div class='kater-log'>🐈‍⬛ {block.replace('**3. 🐈‍⬛ Kater-Log:**', '').strip()}</div>", unsafe_allow_html=True)
        elif '⚡ Vektor-Auswahl' in block:
            st.markdown(f"**⚡ Vektoren:**\n{block.replace('**4. ⚡ Vektor-Auswahl (Format exactly as shown, no bullet points, in German):**', '').strip()}")
        elif '=== S-4 HUD ===' not in block and block.strip() != '':
             st.markdown(block)

# --- 6. HAUPT-INTERFACE ---
st.title("📟 SEKTOR 4 ENGINE")

with st.container():
    st.markdown(f"""
    <div class="hud-box">
        <div class="hud-title">⚙️ MASTER INDEX HUD</div>
        <div class="hud-stat"><span>⏳ RUNDE:</span> <span style="color:#fff">{st.session_state.hud['runde']}</span></div>
        <div class="hud-stat"><span>🪙 KAPITAL:</span> <span style="color:#a1a1aa">{st.session_state.hud['kapital']}</span></div>
        <div class="hud-stat"><span>🎭 HABITUS:</span> <span style="color:#a1a1aa">{st.session_state.hud['habitus']}</span></div>
        <div class="hud-stat" style="margin-top:10px; border-top:1px dashed #065f46; padding-top:5px;">
            <span style="color:#ef4444">🧠 T-LOAD:</span> <span style="color:#ef4444">{st.session_state.hud['tload']}</span>
        </div>
        <div class="hud-stat">
            <span style="color:#06b6d4">📻 RESONANZ:</span> <span style="color:#06b6d4">{st.session_state.hud['resonanz']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

for entry in st.session_state.history:
    if entry["role"] == "user":
        st.info(f"**DU:** {entry['content']}")
    else:
        format_ai_response(entry['content'])
        st.divider()

# --- 7. LOGIK VERARBEITUNG ---
if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None 
    
    with st.spinner("🤖 Engine berechnet Vektoren..."):
        try:
            history_text = "\n\n".join([f"{e['role'].upper()}: {e['content']}" for e in st.session_state.history[-6:]])
            full_prompt = f"Bisheriger Verlauf:\n{history_text}\n\nNeuer Input: {prompt}"

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.4
                )
            )
            
            ai_text = response.text
            parse_hud_from_text(ai_text)
            
            if prompt != "SYSTEM BOOT: Starte Runde 0. Wähle zufällig einen Mutator. Präsentiere Charaktererschaffungs-Szenario.":
                st.session_state.history.append({"role": "user", "content": prompt})
            
            st.session_state.history.append({
                "role": "system", 
                "content": ai_text
            })
            
            st.rerun()

        except Exception as e:
            st.error(f"🛑 KRITISCHER FEHLER DER MATRIX: {e}")

# --- 8. STEUERUNG (VEKTOREN) ---
st.write("### ⚡ DEIN VEKTOR")
col1, col2, col3 = st.columns(3)

def set_choice(choice):
    st.session_state.pending_prompt = f"Vektor {choice} gewählt. Berechne nächste Runde."

with col1:
    if st.button("Vektor [ A ]"): set_choice("A")
with col2:
    if st.button("Vektor [ B ]"): set_choice("B")
with col3:
    if st.button("Vektor [ C ]"): set_choice("C")
