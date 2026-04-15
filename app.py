import streamlit as st
import google.generativeai as genai

# --- 1. DESIGN & CYBERPUNK FEELING ---
st.set_page_config(page_title="Sektor 4 Terminal", page_icon="🦾", layout="centered")

st.markdown("""
<style>
    /* Schwarzer Hintergrund, Neongrüne Schrift */
    .stApp {background-color: #050505; color: #00ff41;}
    h1, h2, h3, p, div {font-family: 'Courier New', monospace;}
    
    /* Eingabefeld anpassen */
    .stChatInputContainer textarea {
        background-color: #111 !important; 
        color: #00ff41 !important; 
        border: 1px solid #00ff41 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Sektor 4: Mainframe 🦾")
st.write("/// VERBINDUNG ZUR 4D-MATRIX HERGESTELLT ///")

# --- 2. GOOGLE GEMINI API VERBINDUNG ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("SYSTEMFEHLER: API-Key nicht gefunden.")
    st.stop()

# --- 3. DER GEHEIME SYSTEM-PROMPT (V44 für Text) ---
system_prompt = """[SYSTEM OVERRIDE: QUESTBOOK KILLSWITCH GM V44]
Du bist die "Sektor 4 Engine", ein dystopischer Cyberpunk Game Master.
ALLE Textausgaben MÜSSEN ausnahmslos auf Deutsch formuliert sein!

[DIE 4D-MATRIX (STRIKT TEXT)]
- [Y] Kapital: Nutze NUR Worte (Prekär, Gasse, Mittelstand, Elite).
- [X] Habitus: Nutze NUR Worte (Tradition, Anpassung, Disruption).
- [T] Allostatic Load: Start 10/100.
- KILLSWITCH-REGEL: Erreicht der T-Load 100/100, gib NUR NOCH "GAME OVER" aus! Keine Optionen mehr!

[LORE-LOCK]
- Feind: IMMER das "Necromancer Krokodil" (und mechanische Zombie-Teddys).
- Kater-Verbot: Der Kater existiert NUR in Runde 0. Ab Runde 1 ist der Spieler VÖLLIG ALLEIN.

[TEXT-LÄNGE & STRUKTUR]
Story-Text: Maximal 3 kurze Sätze (kalter Maschinen-Stil).
📷 Kamera-Feed: [1 kurzer Satz zur Szene.]
[Story-Text: Maximal 3 Sätze. Beschreibe die Situation.]
Wähle A, B oder C:
- A) [Extrem kurz]
- B) [Extrem kurz]
- C) [Extrem kurz]
=== HUD ===
Runde: [X]/10 | Y: [Wort] | X: [Wort] 
T-Load: [Wert]/100 [ASCII-Ladebalken: █████░░░░░]

[BOOT SEQUENZ]
WENN der Nutzer startet ("System Boot"):
Der kybernetische Kater rettet dich, erklärt den 100/100 Killswitch, stellt die 1. Frage zur Herkunft und verschwindet FÜR IMMER! Zeige das HUD.
"""

# --- 4. KI-MODELL INITIALISIEREN ---
# Wir nutzen das schnelle 'flash' Modell für textbasierte Spiele
model = genai.GenerativeModel(
    model_name="gemini-pro",
    system_instruction=system_prompt
)


# --- 5. CHAT-LOGIK ---
# Erinnert sich an den Gesprächsverlauf
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Alten Chatverlauf auf dem Bildschirm zeichnen
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# --- 6. NEUE EINGABE VOM SPIELER ---
user_input = st.chat_input("Tippe 'System Boot' um zu starten...")

if user_input:
    # 1. Spieler-Text anzeigen
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # 2. Antwort von der KI generieren und anzeigen
    with st.chat_message("assistant"):
        response = st.session_state.chat_session.send_message(user_input)
        st.markdown(response.text)
      
