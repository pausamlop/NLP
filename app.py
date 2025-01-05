import streamlit as st
import ollama
import json
from main_langchain import initialization, generate_response

st.title("💬 AI Travel Guide")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Inicializar db y translator si no están definidos
if "db" not in st.session_state or "translator" not in st.session_state:
    db, translator, summarizer = initialization()
    st.session_state["db"] = db
    st.session_state["translator"] = translator
    st.session_state["summarizer"] = summarizer

### Write Message History
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message(msg["role"], avatar="🧑‍💻").write(msg["content"])
    else:
        st.chat_message(msg["role"], avatar="🤖").write(msg["content"])

if question := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user", avatar="🧑‍💻").write(question)
    # Acceder a db y translator desde session_state
    db = st.session_state["db"]
    translator = st.session_state["translator"]
    summarizer = st.session_state["summarizer"]
    output = generate_response(question, db, translator)
    response = json.loads(output)['final_response']
    context = json.loads(output)['context']

   # print('response: ', response)
   # print('summary: ', summary)
    st.chat_message("assistant", avatar="🤖").write(response)
    st.session_state.messages.append({"role": "assistant", "content": response}) 
