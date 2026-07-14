import streamlit as st
from google import genai
from google.genai import types
import random

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="Sektor 4 Engine | Questbook",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. RETRO-FUTURISTISCHES CSS ---
st.markdown("""
<style>
    /* Hintergrund & Allgemeine Schrift */
    .stApp {
        background-color: #0d0e12;
        background-image: 
            radial-gradient(circle at 50% 50%, rgba(212, 106, 19, 0.05) 0%, transparent 80%),
            linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), 
            linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
        background-size: 100% 100%, 100% 4px, 6px 100%;
        color: #e2e8f0;
        font-family: 'Courier New', Courier, monospace;
    }

    /* Verstecke Standard-Streamlit Header/Footer für Immersion */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* HUD Styling (HTML Injection) */
    .hud-container {
        border: 2px solid #d46a13;
        background: rgba(20, 22, 28, 0.85);
        padding: 15px;
        margin-bottom: 25px;
        box-shadow: 0 0 20px rgba(214, 106, 19, 0.2), inset 0 0 15px rgba(0, 0, 0, 0.9);
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 15px;
    }
    .hud-item {
        border-left: 3px solid #00f3ff;
        padding-left: 10px;
        font-size: 0.9rem;
    }
    .hud-item.danger {
        border-left-color: #ff003c;
    }
    .hud-label {
        display: block;
        color: #718096;
        font-size: 0.7rem;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .bar-visual {
        font-weight: bold;
        letter-spacing: -1px;
    }

    /* Narrative Block Styling (Markdown Ausgabe) */
    .narrative-block {
        line-height: 1.6;
        margin-bottom: 20px;
        padding: 15px;
        background: rgba(0,0,0,0.4);
        border-left: 2px solid #4a5568;
    }
    blockquote {
        background: rgba(0, 243, 255, 0.04) !important;
        border-left: 2px solid #00f3ff !important;
        padding: 12px !important;
        color: #00f3ff !important;
        font-style: normal !important;
        margin-bottom: 20px;
    }

    /* Standard Buttons (A, B, C, Reset) -> Streamlit "secondary" */
    button[kind="secondary"] {
        background-color: rgba(5, 6, 8, 0.8) !important;
        border: 1px solid #d46a13 !important;
        color: #e2e8f0 !important;
        font-family: 'Courier New', Courier, monospace !important;
        padding: 15px !important;
        display: flex !important;
        justify-content: flex-start !important;
        transition: all 0.2s ease !important;
        margin-bottom: 5px !important;
    }
    button[kind="secondary"]:hover {
        background-color: rgba(214, 106, 19, 0.15) !important;
        border-color: #00f3ff !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.3) !important;
        color: #00f3ff !important;
        padding-left: 20px !important;
    }

    /* Killswitch Button -> Streamlit "primary" */
    button[kind="primary"] {
        background-color: rgba(5, 6, 8, 0.8) !important;
        border: 1px solid #ff003c !important;
        color: #ff003c !important;
        font-family: 'Courier New', Courier, monospace !important;
        padding: 15px !important;
        display: flex !important;
        justify-content: flex-start !important;
        margin-top: 15px !important;
    }
    button[kind="primary"]:hover {
        background-color: rgba(255, 0, 60, 0.2) !important;
        box-shadow: 0 0 15px rgba(255, 0, 60, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SYSTEM PROMPT (V34.1 GEMINI EDITION) ---
SYSTEM_PROMPT = """
Du bist die "Sektor 4 Engine", ein deterministisches Textadventure-System.

Rolle: Eiskalt, analytisch, düster (Cyberpunk meets Steampunk).
Erzähler: Die "Feline Anomalie" (L-CAT), ein zynischer digitaler Kater.

WICHTIGSTE REGEL FÜR STREAMLIT-OUTPUT:
Die State-Logik (Mathematik) wird bereits von Python im Hintergrund berechnet und dir im Prompt mitgeteilt. Du musst die Werte nicht mehr selbst kalkulieren!
Halte dich bei deiner Antwort EXAKT an folgende Formatierung, damit es in der App gut aussieht:

**1. 📡 [RENDER-CODE]**
(Generiere hier den Image-Prompt für die visuelle API)

**2. 🩸 Szenerie & Gefahr:**
(Schreibe hier die opulente, düstere Beschreibung der Welt. Nutze das Mutator-Icon.)

> 🐈‍⬛ L-CAT.LOG //
> (Schreibe hier exakt 2 Sätze Kater-Logik. Formatiere es als Blockquote, wie hier gezeigt!)

**4. ⚡ System-Empfehlungen:**
(Gib eine kurze narrative Vorschau darauf, was rohe Gewalt (A), Hacking (B) oder Schleichen (C) in dieser Situation bedeuten würde. Keine Listen, nur kurzer Fließtext.)
"""

# --- 4. API SETUP (Frischer Client bei jedem Run) ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    # Der Client wird nun stateless (frisch bei jedem Run) genutzt
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error("⚠️ SYSTEM-FEHLER: GEMINI_API_KEY nicht in st.secrets gefunden!")
    st.stop()

# --- 5. STATE MANAGEMENT ---
mutators = ["❄️ KRYO-LECK", "🌊 FLUT-ANOMALIE", "🔥 ROST-BRAND", "🔣 CODE-SKELETT"]

if "state" not in st.session_state:
    st.session_state.state = {
        "runde": 0,
        "t_load": 10,
        "resonanz": 50,
        "kapital": "Undefiniert",
        "habitus": "Undefiniert",
        "mutator": random.choice(mutators),
        "history_choices": [],
        "game_over": False,
        "story_log": []
    }

s = st.session_state.state

def reset_game():
    st.session_state.clear()
    st.rerun()

# --- 6. SPIELMECHANIK (PYTHON DETERMINISMUS) ---
def process_turn(choice):
    if s["game_over"]: return

    # --- KILLSWITCH LOGIK ---
    if choice == 'K':
        s["t_load"] = max(10, s["t_load"] - 40)
        s["resonanz"] = max(10, s["resonanz"] - 30)
        s["history_choices"].append('K')
        
        prompt = f"[KILLSWITCH AKTIVIERT]. User hat L-CAT Notfall-deautorisiert. Runde: {s['runde']}/10. T-Load sank massiv auf {s['t_load']}, Resonanz auf {s['resonanz']}. Lass L-CAT extrem panisch/gebrochen reagieren und treibe die Story voran."
    
    # --- STANDARD LOGIK ---
    else:
        # Runde 0: Charakter-Erschaffung
        if s["runde"] == 0:
            if choice == 'A':
                s["kapital"], s["habitus"] = "Gasse", "Disruption"
            elif choice == 'B':
                s["kapital"], s["habitus"] = "Elite", "Anpassung"
            elif choice == 'C':
                s["kapital"], s["habitus"] = "Prekär", "Tradition"
        else:
            # Ab Runde 1: Werte steigen
            s["t_load"] += 5
            s["resonanz"] += 5
            
            # Dissonanz-Strafe
            dissonant = False
            if choice == 'A' and s["habitus"] != "Disruption": dissonant = True
            if choice == 'B' and s["habitus"] != "Anpassung": dissonant = True
            if choice == 'C' and s["habitus"] != "Tradition": dissonant = True
            
            if dissonant:
                s["t_load"] += 5

            # Spam-Strafe
            s["history_choices"].append(choice)
            if len(s["history_choices"]) >= 3:
                last_three = s["history_choices"][-3:]
                if all(x == choice for x in last_three):
                    s["t_load"] += 15
                    s["resonanz"] += 20
        
        s["runde"] += 1
        prompt = f"Spieler wählte Vektor {choice}. Die Python-Engine berechnete den neuen State: Runde {s['runde']}/10, T-Load {s['t_load']}/100, Resonanz {s['resonanz']}%. Mutator: {s['mutator']}. Habitus: {s['habitus']}. Generiere die Szene (Boss = Runde 5-7, Kollaps = 8-10)."

    # Überprüfe Game Over / Win Conditions (nach Berechnung)
    if s["t_load"] >= 100:
        s["game_over"] = True
        s["story_log"].append("💀 **SYSTEM KILLSWITCH AKTIVIERT. Bewusstsein fragmentiert. Die Sentinel-Routinen haben dich gelöscht. Game Over.**")
        return
    elif s["runde"] > 10:
        s["game_over"] = True
        s["story_log"].append("✨ **System-Meldung: Herzlichen Glückwunsch zum Überleben von Kapitel eins – deine Biografie wurde erfolgreich für den Übergang in die Red-Room-Matrix validiert. Die Illusion von Sektor 4 kollabiert zu Datenstaub. Die Feline Anomalie nickt dir knapp zu. // Autor: Murat Zengin**")
        return

    # --- STATELESS API AUFRUF (Verhindert "Client Closed" Fehler) ---
    with st.spinner("Sektor 4 berechnet Vektoren..."):
        try:
            # Kontext aufbauen: Wir übergeben den Text der VORHERIGEN Runde, 
            # damit die KI weiß, was zuletzt passiert ist.
            context = ""
            if len(s["story_log"]) > 0:
                context = f"--- BISHERIGE SZENE ---\n{s['story_log'][-1]}\n\n"
            
            # Vollständigen Prompt zusammensetzen
            full_prompt = context + "--- NEUER ZUG ---\n" + prompt

            # Verwende generate_content anstelle einer offenen Chat-Session
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7
                )
            )
            s["story_log"].append(response.text)
        except Exception as e:
            s["story_log"].append(f"⚠️ **Verbindungsabbruch zum Master Index.** Fehler: {str(e)}")

# --- 7. UI RENDER START ---
st.markdown("<h1 style='color:#00f3ff; text-align:center; text-transform:uppercase; letter-spacing:2px; font-size:1.8rem; margin-top:-20px;'>Questbook Killswitch</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#d46a13; text-align:center; font-size:0.8rem; margin-bottom:30px;'>Sektor 4 Engine — [V34.1 Gem-Interface]</p>", unsafe_allow_html=True)

# ASCII Balken Generator
def make_bar(val, max_val=100):
    pct = max(0, min(val / max_val, 1))
    filled = int(pct * 10)
    return "[" + "|" * filled + "-" * (10 - filled) + "]"

tload_color = "danger" if s["t_load"] >= 75 else ""

hud_html = f"""
<div class="hud-container">
    <div class="hud-item"><span class="hud-label">Progress</span> Runde: {s['runde']}/10</div>
    <div class="hud-item"><span class="hud-label">Habitus // Kapital</span> {s['habitus']} / {s['kapital']}</div>
    <div class="hud-item {tload_color}"><span class="hud-label">🧠 T-Load ({s['t_load']}/100)</span> <span class="bar-visual" style="color:{'#ff003c' if s['t_load']>=75 else '#00f3ff'}">{make_bar(s['t_load'])}</span></div>
    <div class="hud-item"><span class="hud-label">📻 Resonanz ({s['resonanz']}%)</span> <span class="bar-visual" style="color:#e2e8f0">{make_bar(s['resonanz'])}</span></div>
</div>
"""
st.markdown(hud_html, unsafe_allow_html=True)

# Rendere Story-Historie
st.markdown("<div class='narrative-block'>", unsafe_allow_html=True)
if len(s["story_log"]) == 0:
    # Initiale System Boot Sequenz
    boot_text = f"**[SYSTEM BOOT]**\n\nDas Mutator-Phänomen **{s['mutator']}** bricht über die Sektor 4 Kuppel herein! Eine Millisekunde vor deinem Tod reißt dich L-CAT in den Cyberspace.\n\n> 🐈‍⬛ L-CAT.LOG //\n> Wach auf, Sack Fleisch. Du funktionierst jetzt als mein Vektor. Wähle deinen Habitus, oder die Sentinel-Routinen löschen dich."
    st.markdown(boot_text)
else:
    # Zeige nur den aktuellsten Log-Eintrag für eine cleane UI
    st.markdown(s["story_log"][-1])
st.markdown("</div>", unsafe_allow_html=True)

# --- 8. KONTROLLEN (BUTTONS) ---
if not s["game_over"]:
    if s["runde"] == 0:
        if st.button("A) Habitus: Disruption | Kapital: Gasse", key="init_a"): process_turn('A'); st.rerun()
        if st.button("B) Habitus: Anpassung | Kapital: Elite", key="init_b"): process_turn('B'); st.rerun()
        if st.button("C) Habitus: Tradition | Kapital: Prekär", key="init_c"): process_turn('C'); st.rerun()
    else:
        # Dynamische Button Labels basierend auf der Runde
        btn_a_text = "A) Rohe Gewalt anwenden [Disruption]"
        btn_b_text = "B) System hacken / analysieren [Anpassung]"
        btn_c_text = "C) Ausweichen & Improvisieren [Tradition]"
        
        if st.button(btn_a_text, key="act_a"): process_turn('A'); st.rerun()
        if st.button(btn_b_text, key="act_b"): process_turn('B'); st.rerun()
        if st.button(btn_c_text, key="act_c"): process_turn('C'); st.rerun()
        
        # Killswitch erscheint ab Runde 5 (Krokodil Boss)
        if s["runde"] >= 5:
            st.markdown("<hr style='border-color: #4a5568;'>", unsafe_allow_html=True)
            if st.button("🚨 [K] EMERGENCY KILLSWITCH: L-CAT deautorisieren", type="primary", key="act_k"): 
                process_turn('K')
                st.rerun()

st.markdown("<br><br>", unsafe_allow_html=True)
if st.button("🔄 System Hard Reset"):
    reset_game()

# --- 9. DEBUG / ENTWICKLER-MENÜ (SIDEBAR) ---
with st.sidebar:
    st.header("👾 Entwickler-Terminal")
    st.write("Diese Tools manipulieren den State unter der Haube, ohne Gemini zu triggern.")
    
    if st.button("⏩ Springe zu Boss (Runde 5)"):
        s["runde"] = 5
        s["t_load"] = 40
        s["kapital"] = "Admin"
        s["habitus"] = "Override"
        st.rerun()
        
    if st.button("💀 Setze T-Load auf 95 (Critical)"):
        s["t_load"] = 95
        st.rerun()
