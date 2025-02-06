import streamlit as st
import asyncio
from ollama import AsyncClient

# Custom CSS for styling
st.markdown("""
<style>
    .stChatInput {position: fixed; bottom: 20px; width: 95%;}
    .stChatMessage {
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {background-color: #f0f2f6;}
    .assistant-message {background-color: #e6f4ff;}
</style>
""", unsafe_allow_html=True)

st.title("🤖 Local AI Chatbot")
st.sidebar.title("About")
st.sidebar.markdown("""
This chatbot uses a local Ollama model for responses.
- Maintains last 5 conversations
- Real-time streaming
- Custom UI design
""")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your local AI assistant. How can I help you today?"}
    ]

MODEL_NAME = "deepseek-r1:1.5b"
HISTORY_LENGTH = 10  # Last 5 conversations (User + Assistant)

# Display all previous messages
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    css_class = "assistant-message" if message["role"] == "assistant" else "user-message"

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(f'<div class="{css_class}">{message["content"]}</div>', unsafe_allow_html=True)

# Async function to fetch response
async def get_response(prompt):
    client = AsyncClient()
    async for chunk in await client.chat(
        model=MODEL_NAME,
        messages=st.session_state.messages[-HISTORY_LENGTH:],
        stream=True
    ):
        if 'message' in chunk and 'content' in chunk['message']:
            yield chunk['message']['content']

# Handle user input
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="👤"):
        st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        st.session_state["full_response"] = ""  # Store response in session state

        async def stream_response():
            async for chunk in get_response(prompt):
                st.session_state["full_response"] += chunk
                message_placeholder.markdown(f'<div class="assistant-message">{st.session_state["full_response"]}▌</div>', unsafe_allow_html=True)

            message_placeholder.markdown(f'<div class="assistant-message">{st.session_state["full_response"]}</div>', unsafe_allow_html=True)

            # Append assistant response to session state
            st.session_state.messages.append({"role": "assistant", "content": st.session_state["full_response"]})

            # Maintain history length
            if len(st.session_state.messages) > HISTORY_LENGTH:
                st.session_state.messages = st.session_state.messages[-HISTORY_LENGTH:]

        # Run the async function properly in Streamlit
        asyncio.run(stream_response())
