import streamlit as st
import requests
import os

# ── Config ──────────────────────────────────────────────────────────────────
API_URL = os.getenv("KRATOS_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Kratos — Dios de la Guerra",
    page_icon="⚔️",
    layout="centered",
)

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');

/* Base */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0a0a;
    color: #c9b99a;
}

[data-testid="stAppViewContainer"] {
    background-image:
        radial-gradient(ellipse at 50% 0%, rgba(139, 0, 0, 0.15) 0%, transparent 60%),
        radial-gradient(ellipse at 50% 100%, rgba(80, 40, 0, 0.1) 0%, transparent 60%);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { display: none; }
.block-container { max-width: 760px; padding-top: 2rem; padding-bottom: 6rem; }

/* Header */
.kratos-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
    border-bottom: 1px solid rgba(139, 0, 0, 0.4);
    margin-bottom: 2rem;
}
.kratos-header h1 {
    font-family: 'Cinzel', serif;
    font-size: 2.6rem;
    font-weight: 900;
    color: #e8d5b0;
    letter-spacing: 0.15em;
    margin: 0;
    text-shadow: 0 0 40px rgba(139, 0, 0, 0.6);
}
.kratos-header p {
    font-family: 'Crimson Text', serif;
    font-style: italic;
    color: #8b0000;
    font-size: 1.05rem;
    margin: 0.4rem 0 0;
    letter-spacing: 0.05em;
}

/* Chat messages */
.msg-user {
    display: flex;
    justify-content: flex-end;
    margin: 1rem 0;
}
.msg-user .bubble {
    background: rgba(139, 0, 0, 0.2);
    border: 1px solid rgba(139, 0, 0, 0.4);
    border-radius: 16px 16px 4px 16px;
    padding: 0.75rem 1.1rem;
    max-width: 75%;
    font-family: 'Crimson Text', serif;
    font-size: 1.05rem;
    color: #e8d5b0;
}

.msg-kratos {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    gap: 0.75rem;
    margin: 1rem 0;
}
.msg-kratos .avatar {
    font-size: 1.6rem;
    margin-top: 0.2rem;
    flex-shrink: 0;
}
.msg-kratos .bubble {
    background: rgba(20, 15, 10, 0.8);
    border: 1px solid rgba(180, 140, 60, 0.2);
    border-left: 3px solid #8b0000;
    border-radius: 4px 16px 16px 16px;
    padding: 0.85rem 1.1rem;
    max-width: 80%;
    font-family: 'Crimson Text', serif;
    font-size: 1.08rem;
    color: #c9b99a;
    line-height: 1.65;
}

/* Thinking indicator */
.thinking {
    font-family: 'Cinzel', serif;
    font-size: 0.75rem;
    color: #8b0000;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    padding: 0.5rem 1rem;
    animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 1; }
}

/* Input area */
[data-testid="stChatInput"] {
    border-top: 1px solid rgba(139, 0, 0, 0.3) !important;
    background: rgba(10, 10, 10, 0.95) !important;
}
[data-testid="stChatInput"] textarea {
    background: rgba(20, 15, 10, 0.9) !important;
    color: #e8d5b0 !important;
    border: 1px solid rgba(139, 0, 0, 0.3) !important;
    border-radius: 8px !important;
    font-family: 'Crimson Text', serif !important;
    font-size: 1.05rem !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(139, 0, 0, 0.5) !important;
}
[data-testid="stChatInput"] button {
    background: #8b0000 !important;
    border-radius: 8px !important;
    color: #e8d5b0 !important;
}
[data-testid="stChatInput"] button:hover {
    background: #a00000 !important;
}

/* Clear button */
.stButton button {
    background: transparent !important;
    border: 1px solid rgba(139, 0, 0, 0.4) !important;
    color: rgba(139, 0, 0, 0.7) !important;
    font-family: 'Cinzel', serif !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.15em !important;
    padding: 0.3rem 1rem !important;
    border-radius: 4px !important;
}
.stButton button:hover {
    border-color: #8b0000 !important;
    color: #8b0000 !important;
    background: rgba(139, 0, 0, 0.05) !important;
}

/* Divider */
hr { border-color: rgba(139, 0, 0, 0.2) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0a; }
::-webkit-scrollbar-thumb { background: rgba(139, 0, 0, 0.4); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="kratos-header">
    <h1>⚔ KRATOS ⚔</h1>
    <p>Fantasma de Esparta · Dios de la Guerra · Padre de Atreus</p>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Clear button ──────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col3:
    if st.button("LIMPIAR", key="clear"):
        st.session_state.messages = []
        st.rerun()

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-user">
            <div class="bubble">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-kratos">
            <div class="avatar">⚔️</div>
            <div class="bubble">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Habla. El Dios de la Guerra te escucha..."):

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f"""
    <div class="msg-user">
        <div class="bubble">{prompt}</div>
    </div>
    """, unsafe_allow_html=True)

    # Build chat history for API (exclude last user message, already in prompt)
    history = [
        {"role": m["role"] if m["role"] == "user" else "assistant", "content": m["content"]}
        for m in st.session_state.messages[:-1]
    ]

    # Call API
    with st.empty():
        st.markdown('<div class="thinking">Kratos medita...</div>', unsafe_allow_html=True)
        try:
            response = requests.post(
                f"{API_URL}/advice",
                json={"message": prompt, "chat_history": history},
                timeout=60,
            )
            response.raise_for_status()
            answer = response.json()["response"]
        except requests.exceptions.ConnectionError:
            answer = "... El Dios de la Guerra no responde. Verifica que el servidor esté corriendo."
        except requests.exceptions.Timeout:
            answer = "... Kratos tarda en responder. El servidor no contestó a tiempo."
        except Exception as e:
            answer = f"... Algo interrumpió la audiencia: {str(e)}"

    # Add and render Kratos response
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.markdown(f"""
    <div class="msg-kratos">
        <div class="avatar">⚔️</div>
        <div class="bubble">{answer}</div>
    </div>
    """, unsafe_allow_html=True)


# Levantar (asegúrate que el backend esté corriendo en :8000)
# streamlit run app.py