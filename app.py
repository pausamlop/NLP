import streamlit as st
import ollama
import json
from main_langchain import generate_response

st.title("💬 llama2 (7B) Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

### Write Message History
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message(msg["role"], avatar="🧑‍💻").write(msg["content"])
    else:
        st.chat_message(msg["role"], avatar="🤖").write(msg["content"])

if question := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user", avatar="🧑‍💻").write(question)
    st.session_state["full_message"] = ""
    response = json.loads(generate_response(question))['final_response']
    print('response: ', response)
    st.chat_message("assistant", avatar="🤖").write_stream(response)
    st.session_state.messages.append({"role": "assistant", "content": st.session_state["full_message"]})  