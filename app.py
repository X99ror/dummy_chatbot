import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from datetime import datetime


load_dotenv()

api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

CHAT_FOLDER = "chats"
os.makedirs(CHAT_FOLDER, exist_ok=True)

if "chat_name" not in st.session_state:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.chat_name = f"chat_{timestamp}.json"


def save_chat(chat_name, messages):
    filepath = os.path.join(CHAT_FOLDER, chat_name)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(messages, f)

def load_chat(chat_name):
    filepath = os.path.join(CHAT_FOLDER, chat_name)

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    return [{"role": "system", "content": "You are a helpful assistant."}]





    
if st.sidebar.button("Delete Chat"):
    os.remove(os.path.join(CHAT_FOLDER, st.session_state.chat_name))
    st.rerun()

if st.sidebar.button("New Chat"):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    st.session_state.chat_name = f"chat_{timestamp}.json"

    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        }
    ]

    save_chat(
        st.session_state.chat_name,
        st.session_state.messages
    )

    st.rerun()


st.sidebar.divider()
search = st.sidebar.text_input("Search Chats")
chat_files = sorted(os.listdir(CHAT_FOLDER), reverse=True)
if search:
    chat_files = [
        chat for chat in chat_files
        if search.lower() in chat.lower()
    ]

for chat in chat_files:
    display_name = chat.replace(".json", "")
    if st.sidebar.button(display_name):

        st.session_state.chat_name = chat

        st.session_state.messages = load_chat(chat)

        st.rerun()

if 'messages' not in st.session_state:
    st.session_state['messages'] = [{"role": "system", "content": "You are a helpful assistant."}]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.chat_name = f"chat_{timestamp}.json"
    save_chat(st.session_state.chat_name, st.session_state.messages)

st.title("OpenAI Chatbot")
for message in st.session_state.messages:
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask something...")
if prompt:
    st.session_state['messages'].append({"role": "user", "content": prompt})
    with st.spinner("Assistant is typing..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state["messages"]
        )
    assistant_reply = response.choices[0].message.content

    st.session_state["messages"].append(
        {"role": "assistant", "content": assistant_reply}
    )

    save_chat(
        st.session_state["chat_name"],
        st.session_state["messages"]
    )

    st.rerun()
    
