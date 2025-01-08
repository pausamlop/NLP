import streamlit as st
import ollama
import json
from main_langchain import initialization, generate_response
from translator import translate_backwards
from summarizer import summarize
from topics import extract_top_keywords, generate_question_from_context
from langchain.schema import Document
from audio import language_supported, play_audio
import time

places_info =[ 
    {"name": "Barcelona", "emoji": "🏖"}, 
    {"name": "Los Angeles", "emoji": "🌴"}, 
    {"name": "Paris", "emoji": "🗼"}, 
    {"name": "Rome", "emoji": "🏛"}, 
    {"name": "Zurich", "emoji": "⛰"}, 
] 

st.title("💬 AI Travel Guide")

st.subheader("🌎 Places I have information about:") 
cols = st.columns(len(places_info))
for col, place in zip (cols, places_info):
    with col:
        st.markdown(f"{place['emoji']} {place['name']}")

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

    # Medir el tiempo de generación de la respuesta
    start_time = time.time()  # Tiempo inicial

    # Acceder a db y translator desde session_state
    db = st.session_state["db"]
    translator = st.session_state["translator"]
    summarizer = st.session_state["summarizer"]
    output = generate_response(question, db, translator)

    end_time = time.time()  # Tiempo final
    elapsed_time = end_time - start_time  # Calcular tiempo transcurrido

    response = json.loads(output)['final_response']
    st.session_state["response"] = response
    context = json.loads(output)['context']
    st.session_state["context"] = context
    input_lang = json.loads(output)['input_lang']
    st.session_state["input_lang"] = input_lang
    documents = json.loads(output)['documents']

    # Agregar la pregunta al historial
    st.session_state["last_questions"].append(question)
    # Limitar el historial a las últimas 5 preguntas
    st.session_state["last_questions"] = st.session_state["last_questions"][-5:]

    # Generar respuesta con referencias
    response_with_references = response
    if documents:
        file_path = documents[0].get('source_url', '') 
        file_path = file_path.replace("./guides", "/app/static/guides")  # Cambia la ruta para usar "static/guides"
        file_path = file_path.replace(".txt", ".pdf")
        
        # Traducir la parte del mensaje según el idioma de la pregunta
        translation_message = "You can find more information in the [file]({})".format(file_path)

        # Traducir al idioma de la pregunta
        translated_message = translate_backwards(translator, translation_message, input_lang)
        
        # Agregar el mensaje traducido a la respuesta
        response_with_references += f"\n\n{translated_message}"

    
    st.chat_message("assistant", avatar="🤖").write(response_with_references)
    st.session_state.messages.append({"role": "assistant", "content": response_with_references})

    st.caption(f"⏱️ Response generated in {elapsed_time:.2f} seconds.") 

    # Mostrar botón de generación de resumen
    st.session_state["show_summary_button"] = True

    # Añadir audio read out loud
    if language_supported(input_lang):
        st.session_state["show_play_button"] = True

    # Mostrar sugerencias
    st.session_state["suggest_questions"] = True

if st.session_state.get("show_summary_button"):
    translator = st.session_state["translator"]
    # Preguntar al usuario si desea un resumen
    summary_question = translate_backwards(translator, "Would you like a summary of the document?", st.session_state['input_lang'])
    if st.button(summary_question):
        with st.spinner("Generating summary..."):
            # Crear un documento simulado para resumir
            document = [Document(page_content=st.session_state["context"])]

            # Llamar a la función summarize
            summarizer = st.session_state["summarizer"]
            summary = summarize(summarizer, document)
            translated_summary = translate_backwards(translator, summary, st.session_state['input_lang'])
            
            st.chat_message("assistant", avatar="🤖").write(f"Here is the summary:\n\n{translated_summary}")
            st.session_state.messages.append({"role": "assistant", "content": translated_summary})

# Reproducir la respuesta
if st.session_state.get("show_play_button"): 
    input_lang = st.session_state["input_lang"]
    play_question = translate_backwards(translator, "Would you like me to read the answer out loud?", input_lang)
    if st.button(play_question):
        response = st.session_state["response"]
        play_audio(response, input_lang)

if st.session_state.get("suggest_questions"):
    topics = extract_top_keywords(st.session_state['response'])
    suggested_questions = generate_question_from_context(topics)
    # translated_question = translate_backwards(translator, suggested_questions, st.session_state['input_lang'])
    if st.button(suggested_questions):
        st.session_state.messages.append({"role": "user", "content": suggested_questions})
        db = st.session_state["db"]
        translator = st.session_state["translator"]
        summarizer = st.session_state["summarizer"]
        output = generate_response(suggested_questions, db, translator)
        response = json.loads(output)['final_response']
        st.chat_message("assistant", avatar="🤖").write(response)
        st.session_state.messages.append({"role": "assistant", "content": response}) 


with st.sidebar:
    st.subheader("Last 5 questions 📋")
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
