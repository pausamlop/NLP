import streamlit as st
import ollama
import json
from main_langchain import initialization, generate_response
from summarizer import load_summarization_pipeline, summarize

st.title("💬 AI Travel Guide")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

if "last_questions" not in st.session_state:
    st.session_state["last_questions"] = []

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
    # Agregar la pregunta al historial
    st.session_state["last_questions"].append(question)
    # Limitar el historial a las últimas 5 preguntas
    st.session_state["last_questions"] = st.session_state["last_questions"][-5:]

   # print('response: ', response)
   # print('summary: ', summary)
    st.chat_message("assistant", avatar="🤖").write(response)
    st.session_state.messages.append({"role": "assistant", "content": response}) 

    # Preguntar al usuario si desea un resumen
    if st.button("Would you like a summary of the document?"):
        with st.spinner("Generating summary..."):
            # Crear un documento simulado para resumir
            from langchain.schema import Document
            document = [Document(page_content=context)]

            # Llamar a la función summarize
            summarizer2 = load_summarization_pipeline()
            summary = summarize(summarizer2, document)
            
            st.chat_message("assistant", avatar="🤖").write(f"Here is the summary:\n\n{summary}")
            st.session_state.messages.append({"role": "assistant", "content": summary})

with st.sidebar:
    st.subheader("Last 5 questions")
    for i, past_question in enumerate(st.session_state["last_questions"]):
        if st.button(f"Resend: {past_question}", key=f"resend_{i}"):
            st.session_state.messages.append({"role": "user", "content": past_question})
            db = st.session_state["db"]
            translator = st.session_state["translator"]
            summarizer = st.session_state["summarizer"]
            output = generate_response(past_question, db, translator)
            response = json.loads(output)['final_response']
            st.chat_message("assistant", avatar="🤖").write(response)
            st.session_state.messages.append({"role": "assistant", "content": response}) 
