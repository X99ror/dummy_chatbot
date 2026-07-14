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

PINNED_FILE = "pinned_chats.json"

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


def load_pinned():
    if os.path.exists(PINNED_FILE):
        with open(PINNED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_pinned(pinned_list):
    with open(PINNED_FILE, "w", encoding="utf-8") as f:
        json.dump(pinned_list, f)

def toggle_pin(chat_name):
    pinned = load_pinned()
    if chat_name in pinned:
        pinned.remove(chat_name)
    else:
        pinned.append(chat_name)
    save_pinned(pinned)


if st.sidebar.button("Delete Chat"):
    os.remove(os.path.join(CHAT_FOLDER, st.session_state.chat_name))
    pinned = load_pinned()
    if st.session_state.chat_name in pinned:
        pinned.remove(st.session_state.chat_name)
        save_pinned(pinned)
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

pinned = load_pinned()
pinned = [p for p in pinned if p in chat_files]

pinned_chats = [c for c in chat_files if c in pinned]
unpinned_chats = [c for c in chat_files if c not in pinned]


def render_chat_row(chat, is_pinned):
    display_name = chat.replace(".json", "")
    col1, col2 = st.sidebar.columns([5, 1])
    with col1:
        if st.button(display_name, key=f"open_{chat}"):
            st.session_state.chat_name = chat
            st.session_state.messages = load_chat(chat)
            st.rerun()
    with col2:
        pin_icon = "📌" if is_pinned else "📍"
        if st.button(pin_icon, key=f"pin_{chat}"):
            toggle_pin(chat)
            st.rerun()


if pinned_chats:
    st.sidebar.markdown("**Pinned**")
    for chat in pinned_chats:
        render_chat_row(chat, is_pinned=True)
    st.sidebar.divider()

if unpinned_chats:
    st.sidebar.markdown("**All Chats**")
    for chat in unpinned_chats:
        render_chat_row(chat, is_pinned=False)

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