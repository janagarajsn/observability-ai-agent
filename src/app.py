import os
import logging
import streamlit as st
from dotenv import load_dotenv
from observability_engine import agentic_query

# ---- Streamlit config ----
st.set_page_config(page_title="Observability AI Engine", layout="wide", page_icon=":mag_right:")

# ---- Logging ----
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s")
logger = logging.getLogger(__name__)

# ---- Load environment ----
load_dotenv()

st.title("Query Observability Logs and System Tickets")

# ---- Helpers ----
def human_msg(content: str) -> dict:
    return {"role": "human", "content": content}

def ai_msg(content: str) -> dict:
    return {"role": "ai", "content": content}

# ---- Session state ----
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [ai_msg("Hello! You can query observability logs and system tickets here.")]

# ---- Render chat history ----
for msg in st.session_state.chat_history:
    if msg["role"] == "human":
        st.chat_message("Human").markdown(msg["content"])
    else:
        st.chat_message("AI").markdown(msg["content"])

# ---- Chat input ----
user_query = st.chat_input("Type your message here...")
if user_query:
    # Add human message to chat history
    st.session_state.chat_history.append(human_msg(user_query))
    st.chat_message("Human").markdown(user_query)

    # Query the agent
    with st.spinner("Querying..."):
        try:
            answer = agentic_query(user_query)
            # Add AI response to chat history
            st.session_state.chat_history.append(ai_msg(answer))
            st.chat_message("AI").markdown(answer)
        except Exception as e:
            logger.error(f"Query failed: {type(e).__name__}: {e}")
            st.error(f"Error querying logs: {e}")

# ---- Footer ----
st.markdown("---")
st.write("Powered by [OpenAI](https://openai.com) and [Streamlit](https://streamlit.io)")
