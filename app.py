import streamlit as st
import ollama
import json
from main_langchain import initialization, generate_response

st.title(" llama2 (7B) Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Inicializar db y translator si no están definidos
if "db" not in st.session_state or "translator" not in st.session_state:
    db, translator = initialization()
    st.session_state["db"] = db
    st.session_state["translator"] = translator

### Write Message History
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message(msg["role"], avatar="六‍").write(msg["content"])
    else:
        st.chat_message(msg["role"], avatar="烙").write(msg["content"])

if question := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user", avatar="六‍").write(question)
    st.session_state["full_message"] = ""
    # Acceder a db y translator desde session_state
    db = st.session_state["db"]
    translator = st.session_state["translator"]
    response = json.loads(generate_response(question, db, translator))['final_response']
    print('response: ', response)
    st.chat_message("assistant", avatar="烙").write(response)
    st.session_state.messages.append({"role": "assistant", "content": st.session_state["full_message"]})  
