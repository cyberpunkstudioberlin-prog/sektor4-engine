import streamlit as st
import google.generativeai as genai

# --- 1. DESIGN ---
st.set_page_config(page_title="Sektor 4 Emergency", page_icon="🦾")
st.markdown("<style>.stApp {background-color: #050505; color: #00ff41;} h1,p,div{font-family: 'Courier New', monospace; color: #00ff41;}</style>", unsafe_allow_html=True)

st.title("Sektor 4: Emergency Terminal 🦾")

# --- 2. API ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 3. SESSION FIX ---
if "matrix_session" not in st.session_state:
    model = genai.GenerativeModel("gemini-1.5-flash")
    st.session_state.matrix_session = model.start_chat(history=[])
    st.session_state.last_text = "SYSTEM BEREIT. Bitte 'System Boot' eingeben."

# --- 4. DIE SCHNELLE LOGIK (OHNE BLOCKIEREN) ---
def run_action(user_input):
    try:
        # NUR TEXT - Das muss schnell gehen!
        response = st.session_state.matrix_session.send_message(user_input)
        st.session_state.last_text = response.text
    except Exception as e:
        st.error(f"VERBINDUNGSFEHLER: {str(e)}")

# --- 5. INTERFACE ---
# Textausgabe
st.markdown(f"### AKTUELLER STATUS\n{st.session_state.last_text}")

# Buttons (Direkt-Trigger)
st.write("---")
c1, c2, c3 = st.columns(3)
if c1.button("Option A"): 
    run_action("A")
    st.rerun()
if c2.button("Option B"): 
    run_action("B")
    st.rerun()
if c3.button("Option C"): 
    run_action("C")
    st.rerun()

# Freitext
cmd = st.chat_input("Befehl...")
if cmd:
    run_action(cmd)
    st.rerun()

# Notfall-Reset in der Sidebar
if st.sidebar.button("HARD RESET"):
    st.session_state.clear()
    st.rerun()
    
