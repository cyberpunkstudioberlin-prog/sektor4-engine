import streamlit as st
from google import genai
from google.genai import types
import re
import os
import random

# --- 1. KONFIGURATION & DESIGN ---
st.set_page_config(
    page_title="Sektor 4 Engine // Questbook Killswitch",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS UPDATE: Maximale Lesbarkeit & Vektor-Listen-Styling
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #10b981; }
    
    p, li, .stMarkdown { font-size: 1.3rem !important; line-height: 1.7 !important; color: #d4d4d8; }
    h3 { font-size: 1.6rem !important; margin-top: 1.5rem !important; }
    
    .hud-box { background-color: #0d0d10; border: 1px solid #065f46; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-family: monospace; font-size: 1.2rem; }
    .hud-title { color: #eab308; font-weight: bold; font-size: 1.4rem; margin-bottom: 10px; border-bottom: 1px solid #065f46; padding-bottom: 5px; }
    .hud-stat { display: flex; justify-content: space-between; margin-bottom: 8px; }
    
    .kater-log { background-color: #18181b; border-left: 4px solid #d946ef; padding: 15px; font-style: italic; color: #e879f9; margin: 15px 0; border-radius: 0 8px 8px 0; font-size: 1.3rem; }
    .engine-log { background-color: rgba(6, 95, 70, 0.2); color: #34d399; padding: 10px; border: 1px solid #065f46; border-radius: 5px; font-family: monospace; font-size: 1rem; margin-bottom: 15px; }
    .ascii-art { background-color: #000000; color: #10b981; font-family: 'Courier New', Courier, monospace; font-size: 0.9rem; line-height: 1.2; padding: 20px; border: 1px solid #10b981; border-radius: 5px; overflow-x: auto; white-space: pre; text-align: center; margin-bottom: 20px; box-shadow: 0 0 10px rgba(16, 185, 129, 0.2) inset; }
    
    .vektor-item { margin-top: 15px; padding: 15px; background: rgba(16, 185, 129, 0.05); border-left: 4px solid #10b981; border-radius: 4px; display: block; }
    
    .stButton>button { width: 100%; background-color: #000; color: #a1a1aa; border: 2px solid #27272a; text-transform: uppercase; font-weight: bold; font-size: 1.2rem; padding: 1rem; transition: all 0.3s; }
    .stButton>button:hover { border-color: #10b981; color: #10b981; }
    
    .game-over { background-color: #7f1d1d; color: #fca5a5; padding: 20px; border: 2px solid #ef4444; border-radius: 8px; text-align: center; font-weight: bold; font-size: 1.3rem; margin-top: 20px; }
    .game-win { background-color: #064e3b; color: #6ee7b7; padding: 20px; border: 2px solid #10b981; border-radius: 8px; text-align: center; font-weight: bold; font-size: 1.3rem; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are the "Sektor 4 Engine".
Follow V32 Rules strictly. NEVER calculate numbers yourself. I will provide the EXACT values in a [SYSTEM-OVERRIDE] block for every turn. You must merely render them into the 6-step sequence.

CRITICAL INSTRUCTIONS:
1. All text MUST be in GERMAN.
2. Narrative is opulent, visceral, dark Cyberpunk/Steampunk.
3. Narrator: Feline Anomalie (cynical digital cat mentor).
4. No bullet points in Vector options.

STRICT 6-STEP OUTPUT SEQUENCE:
**0. 🧮 [ENGINE-LOGIK]**
Print the exact calculation values provided in the [SYSTEM-OVERRIDE]. Do not calculate them yourself. (Raw text, no bullets).

**1. 📡 [ASCII-FEED]**
Context-sensitive ASCII art of [CURRENT ROOM] and [THREAT] inside a markdown ```ascii block.

**2. 🩸 Szenerie & Gefahr:**
Write this in German. Incorporate Mutator, Threat, and Room. ALWAYS integrate the [STORY-INJECT] provided in the prompt.

**3. 🐈‍⬛ Kater-Log:**
Max 2 sentences. Cynical Feline Anomalie advice/reaction.

**4. ⚡ Vektor-Auswahl:**
Format exactly (No bullets):
A) [Dynamic action] (🪙 Kapital: Gasse | 🎭 Habitus: Disruption) -> Violence.
B) [Dynamic action] (🪙 Kapital: Elite | 🎭 Habitus: Anpassung) -> Tech/Hacking.
C) [Dynamic action] (🪙 Kapital: Prekär | 🎭 Habitus: Tradition) -> Evasion/Stealth.

**5. ⚙️ === S-4 HUD === ⚙️**
Use the EXACT numbers from [SYSTEM-OVERRIDE] to render this HUD block and draw precise ASCII bars for T-Load and Resonanz.
"""

# --- 3. INIT GEMINI ---
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
if not api_key:
    st.error("⚠️ SYSTEM-FEHLER: API_KEY fehlt.")
    st.stop()
client = genai.Client(api_key=api_key)

# --- 4. PYTHON STATE MANAGEMENT ---
if "state" not in st.session_state:
    mutators = ['❄️ KRYO-LECK', '🌊 FLUT-ANOMALIE', '🔥 ROST-BRAND', '🔣 CODE-SKELETT']
    st.session_state.state = {
        "runde": 0,
        "t_load": 10,
        "resonanz": 50,
        "kapital": "Nicht initialisiert",
        "habitus": "Nicht initialisiert",
        "mutator": random.choice(mutators),
        "history_choices": []
    }
if "history" not in st.session_state:
    st.session_state.history = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = "SYSTEM BOOT"

def reset_game():
    st.session_state.clear()
    st.rerun()

# --- 4.5 DEBUG / CHEAT MENU (SIDEBAR) ---
with st.sidebar:
    st.header("🛠️ Entwickler-Terminal")
    st.write("Wird ignoriert, wenn Spiel vorbei ist.")
    
    if st.button("⏩ Springe zu Runde 9"):
        st.session_state.state["runde"] = 9
        st.session_state.state["t_load"] = 85
        st.session_state.state["resonanz"] = 90
        st.session_state.state["kapital"] = "Elite"
        st.session_state.state["habitus"] = "Anpassung"
        st.session_state.pending_prompt = "A" 
        st.rerun()
        
    if st.button("💀 Löse Killswitch aus (T-Load 100)"):
        st.session_state.state["t_load"] = 100
        st.rerun()
        
    if st.button("🔄 Hard Reset"):
        reset_game()

# --- 5. LOGIK BERECHNUNG (PYTHON) ---
def calculate_turn(choice):
    s = st.session_state.state
    
    if s["runde"] == 0:
        if choice == 'A':
            s["kapital"] = "Gasse"
            s["habitus"] = "Disruption"
        elif choice == 'B':
            s["kapital"] = "Elite"
            s["habitus"] = "Anpassung"
        elif choice == 'C':
            s["kapital"] = "Prekär"
            s["habitus"] = "Tradition"
        s["runde"] = 1
        s["history_choices"].append(choice)
        return {"spam_pen": 0, "diss_pen": 0, "old_t": 10, "old_r": 50}

    old_t = s["t_load"]
    old_r = s["resonanz"]
    s["runde"] += 1
    s["history_choices"].append(choice)
    
    base_increase = 5
    s["t_load"] += base_increase
    s["resonanz"] += base_increase
    
    diss_pen = 0
    choice_habitus_map = {'A': 'Disruption', 'B': 'Anpassung', 'C': 'Tradition'}
    if choice_habitus_map[choice] != s["habitus"]:
        diss_pen = 5
        s["t_load"] += diss_pen

    spam_pen_t = 0
    if len(s["history_choices"]) >= 3:
        if s["history_choices"][-1] == s["history_choices"][-2] == s["history_choices"][-3]:
            spam_pen_t = 15
            s["t_load"] += spam_pen_t
            s["resonanz"] += 20

    if s["t_load"] >= 100: s["t_load"] = 100
    if s["resonanz"] > 100: s["resonanz"] = 100

    return {"spam_pen": spam_pen_t, "diss_pen": diss_pen, "old_t": old_t, "old_r": old_r}

def get_threat_context(runde, t_load):
    context = ""
    if runde in [1, 2, 3, 4]:
        context = "FEIND-VORGABE: Lass den Spieler auf 'Schmelzer-Automaten' oder 'Rixdorf-Inquisitoren' treffen. Rohe, mechanische Gegner."
    elif runde in [5, 6, 7]:
        context = "FEIND-VORGABE (BOSS-PHASE): Das gigantische 'Necromancer-Krokodil' greift an! Es ist eine schwere mechanische Bedrohung und beschwört 'Untote Korrumpierte Mechanische Plüsch-Bären'."
    elif runde in [8, 9, 10]:
        context = "FEIND-VORGABE (SYSTEM-KOLLAPS): Sektor 4 dekonstruiert sich in digitale Korruption. Rote Matrix-Streams und Neon-Glitches zerreißen die Realität."
    
    if t_load >= 75:
        context += " [SYSTEM-ZUSTAND: Der T-Load ist über 75. Der Avatar ist kritisch verwundet. Beschreibe Schmerzen und Systemversagen!]"
        
    return context

# --- 6. RENDER HELPER ---
def format_ai_response(text):
    ascii_match = re.search(r'```ascii\n(.*?)\n```', text, re.DOTALL)
    if ascii_match:
        text = text.replace(ascii_match.group(0), '')

    blocks = text.split('\n\n')
    for block in blocks:
        if '🧮 [ENGINE-LOGIK]' in block:
            st.markdown(f"<div class='engine-log'>{block.replace('**0. 🧮 [ENGINE-LOGIK]**', '🧮 ENGINE-LOGIK').strip()}</div>", unsafe_allow_html=True)
        elif '📡 [ASCII-FEED]' in block:
            st.caption("📡 *Sensordaten geparst...*")
            if ascii_match:
                st.markdown(f"<div class='ascii-art'>{ascii_match.group(1)}</div>", unsafe_allow_html=True)
        elif '🩸 Szenerie & Gefahr:' in block:
            st.markdown(f"### 🩸 Szenerie & Gefahr\n{block.replace('**2. 🩸 Szenerie & Gefahr:**', '').strip()}")
        elif '🐈‍⬛ Kater-Log:' in block:
            st.markdown(f"<div class='kater-log'>🐈‍⬛ {block.replace('**3. 🐈‍⬛ Kater-Log:**', '').strip()}</div>", unsafe_allow_html=True)
        elif '⚡ Vektor-Auswahl' in block:
            vectors = block.replace('**4. ⚡ Vektor-Auswahl:**', '').strip()
            vectors = vectors.replace('A)', '<div class="vektor-item"><b>A)</b>')
            vectors = vectors.replace('B)', '</div><div class="vektor-item"><b>B)</b>')
            vectors = vectors.replace('C)', '</div><div class="vektor-item"><b>C)</b>') + '</div>'
            st.markdown(f"**⚡ Vektoren:**{vectors}", unsafe_allow_html=True)
        elif '=== S-4 HUD ===' not in block and block.strip() != '':
             st.markdown(block)

# --- 7. MAIN UI ---
st.title("📟 SEKTOR 4 ENGINE")
s = st.session_state.state

with st.container():
    t_color = "#ef4444" if s['t_load'] >= 75 else "#10b981"
    st.markdown(f"""
    <div class="hud-box">
        <div class="hud-title">⚙️ MASTER INDEX HUD</div>
        <div class="hud-stat"><span>⏳ RUNDE:</span> <span style="color:#fff">{s['runde']}/10</span></div>
        <div class="hud-stat"><span>🪙 KAPITAL:</span> <span style="color:#a1a1aa">{s['kapital']}</span></div>
        <div class="hud-stat"><span>🎭 HABITUS:</span> <span style="color:#a1a1aa">{s['habitus']}</span></div>
        <div class="hud-stat" style="margin-top:10px; border-top:1px dashed #065f46; padding-top:5px;">
            <span style="color:{t_color}">🧠 T-LOAD:</span> <span style="color:{t_color}">{s['t_load']}/100</span>
        </div>
        <div class="hud-stat">
            <span style="color:#06b6d4">📻 RESONANZ:</span> <span style="color:#06b6d4">{s['resonanz']}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

for entry in st.session_state.history:
    if entry["role"] == "user" and not entry["content"].startswith("[SYSTEM"):
        st.info(f"**DU:** {entry['content']}")
    elif entry["role"] == "system":
        format_ai_response(entry['content'])
        st.divider()

# --- 8. GAME LOOP VERARBEITUNG (STREAMING) ---
if st.session_state.pending_prompt:
    raw_choice = st.session_state.pending_prompt
    st.session_state.pending_prompt = None 
    
    if raw_choice == "SYSTEM BOOT":
        prompt = f"[SYSTEM-OVERRIDE] Starte RUNDE 0. Mutator: {s['mutator']}. Setze T-Load=10, Resonanz=50. Erstelle das Boot-Szenario zur Charakterwahl (A, B oder C)."
    else:
        calc_data = calculate_turn(raw_choice)
        threat_context = get_threat_context(s["runde"], s["t_load"])
        
        prompt = f"""[SYSTEM-OVERRIDE] Spieler wählt {raw_choice}. 
EXAKTE WERTE FÜR STEP 0 & HUD:
Neue Runde: {s['runde']}/10
Habitus: {s['habitus']}
Dissonanz-Strafe T-Load: +{calc_data['diss_pen']}
Spam-Strafe T-Load: +{calc_data['spam_pen']}
T-Load: {calc_data['old_t']} + 5 + Strafen = {s['t_load']}
Resonanz: {calc_data['old_r']} + 5 + Strafen = {s['resonanz']}

[STORY-INJECT]: {threat_context}

Schreibe nun die Storyline basierend auf diesen Werten. Integriere zwingend das [STORY-INJECT] in Schritt 2."""

    if s["t_load"] >= 100:
        s["t_load"] = 100
        st.rerun() # Killswitch sofort triggern
    else:
        # STREAMING UI
        st.caption("📡 Eingehende Datenübertragung vom Master Index (Stream aktiv)...")
        stream_placeholder = st.empty()
        full_response = ""
        
        try:
            history_text = "\n\n".join([f"{e['role'].upper()}: {e['content']}" for e in st.session_state.history[-4:]])
            full_prompt = f"History:\n{history_text}\n\nNeuer Input:\n{prompt}"

            # STREAMING API CALL
            response_stream = client.models.generate_content_stream(
                model='gemini-2.5-flash',
                contents=full_prompt,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, temperature=0.4)
            )
            
            # Live-Ausgabe im Hacker-Stil
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    stream_placeholder.markdown(f"""
                    <div style="background-color: #000; color: #10b981; font-family: monospace; padding: 15px; border-left: 3px solid #10b981; font-size: 0.9rem; max-height: 400px; overflow-y: auto;">
                        {full_response} █
                    </div>
                    """, unsafe_allow_html=True)
            
            # Sobald der Stream fertig ist: Platzhalter leeren und sauber formatieren
            stream_placeholder.empty()
            
            if raw_choice != "SYSTEM BOOT":
                st.session_state.history.append({"role": "user", "content": f"Vektor {raw_choice} gewählt."})
            
            st.session_state.history.append({"role": "system", "content": full_response})
            st.rerun()

        except Exception as e:
            st.error(f"🛑 MATRIX-FEHLER (Verbindungsabbruch): {e}")
            if st.button("Verbindung neu aufbauen"):
                st.rerun()

# --- 9. STEUERUNG & END CONDITIONS ---
if s["t_load"] >= 100:
    st.markdown("""
    <div class="game-over">
        💀 SYSTEM KILLSWITCH AKTIVIERT<br><br>
        T-Load bei 100%. Bewusstsein fragmentiert. Die Sentinel-Routinen haben dich gelöscht. Game Over.
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔄 NEUER VERSUCH", on_click=reset_game): pass

elif s["runde"] >= 10 and s["t_load"] < 100:
    st.markdown("""
    <div class="game-win">
        System-Meldung: Herzlichen Glückwunsch zum Überleben von Kapitel eins – deine Biografie wurde erfolgreich für den Übergang in die Red-Room-Matrix validiert. Die Illusion von Sektor 4 kollabiert zu Datenstaub. Die Feline Anomalie nickt dir knapp zu, bevor sie in den Code-Schatten des Red Rooms verschwindet. // Autor der Open Source Akte: Murat Zengin
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔄 NEUES SPIEL STARTEN", on_click=reset_game): pass

else:
    st.write("### ⚡ DEIN VEKTOR")
    col1, col2, col3 = st.columns(3)

    def set_choice(choice):
        st.session_state.pending_prompt = choice

    with col1:
        if st.button("Vektor [ A ]"): set_choice("A")
    with col2:
        if st.button("Vektor [ B ]"): set_choice("B")
    with col3:
        if st.button("Vektor [ C ]"): set_choice("C")
                
