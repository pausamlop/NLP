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

# Definir los lugares y sus emojis
places_info =[ 
    {"name": "Barcelona", "emoji": "🏖"}, 
    {"name": "Los Angeles", "emoji": "🌴"}, 
    {"name": "Paris", "emoji": "🗼"}, 
    {"name": "Rome", "emoji": "🏛"}, 
    {"name": "Zurich", "emoji": "⛰"}, 
] 

# Título y subtítulo de la aplicación
st.title("💬 AI Travel Guide")
st.subheader("🌎 Places I have information about:")

# Mostrar los lugares con emojis en diferentes columnas
cols = st.columns(len(places_info))
for col, place in zip (cols, places_info):
    with col:
        st.markdown(f"{place['emoji']} {place['name']}")

# Inicializar las variables de sesión para mensajes y preguntas pasadas
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

if "last_questions" not in st.session_state:
    st.session_state["last_questions"] = []

# Inicializar base de datos, traductor y resumen si no están definidos
if "db" not in st.session_state or "translator" not in st.session_state:
    db, translator, summarizer = initialization()
    st.session_state["db"] = db
    st.session_state["translator"] = translator
    st.session_state["summarizer"] = summarizer

# Mostrar el historial de mensajes en la interfaz
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message(msg["role"], avatar="🧑‍💻").write(msg["content"])
    else:
        st.chat_message(msg["role"], avatar="🤖").write(msg["content"])

# Procesar nueva entrada del usuario
if question := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user", avatar="🧑‍💻").write(question)

    # Medir el tiempo de generación de la respuesta
    start_time = time.time() # Tiempo inicial

    # Obtener los datos de la sesión
    db = st.session_state["db"]
    translator = st.session_state["translator"]
    summarizer = st.session_state["summarizer"]

    # Generar la respuesta utilizando RAG
    output = generate_response(question, db, translator)

    end_time = time.time()  # Tiempo final
    # Calcular tiempo transcurrido
    elapsed_time = end_time - start_time

    # Procesar la respuesta
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

    # Generar respuesta con referencias a archivos relevantes
    response_with_references = response
    if documents:
        file_path = documents[0].get('source_url', '') 
        file_path = file_path.replace("./guides", "/app/static/guides")  # Cambia la ruta para usar "static/guides"
        file_path = file_path.replace(".txt", ".pdf")
        
        # Traducir mensaje según el idioma del usuario
        translation_message = "You can find more information in the [file]({})".format(file_path)
        translated_message = translate_backwards(translator, translation_message, input_lang)
        # Agregar el mensaje traducido a la respuesta
        response_with_references += f"\n\n{translated_message}"

    # Mostrar la respuesta en la interfaz
    st.chat_message("assistant", avatar="🤖").write(response_with_references)
    st.session_state.messages.append({"role": "assistant", "content": response_with_references})

    # Mostrar el tiempo de generación de la respuesta
    st.caption(f"⏱️ Response generated in {elapsed_time:.2f} seconds.") 

    # Activar opciones de generación de resumen, leer la respuesta y mostrar sugerencias
    st.session_state["show_summary_button"] = True
    if language_supported(input_lang):
        st.session_state["show_play_button"] = True
    st.session_state["suggest_questions"] = True

# Generación de resumen del documento
if st.session_state.get("show_summary_button"):
    translator = st.session_state["translator"]
    # Preguntar al usuario si desea un resumen
    summary_question = translate_backwards(translator, "Would you like a summary of the document?", st.session_state['input_lang'])
    if st.button(summary_question):
        with st.spinner("Generating summary..."):
            # Crear un documento simulado para poder resumirlo
            document = [Document(page_content=st.session_state["context"])]
            # Llamar a la función summarize
            summarizer = st.session_state["summarizer"]
            summary = summarize(summarizer, document)
            translated_summary = translate_backwards(translator, summary, st.session_state['input_lang'])
            # Mostrar el resumen
            st.chat_message("assistant", avatar="🤖").write(f"Here is the summary:\n\n{translated_summary}")
            st.session_state.messages.append({"role": "assistant", "content": translated_summary})

# Reproducir la respuesta como audio
if st.session_state.get("show_play_button"): 
    input_lang = st.session_state["input_lang"]
    play_question = translate_backwards(translator, "Would you like me to read the answer out loud?", input_lang)
    if st.button(play_question):
        response = st.session_state["response"]
        play_audio(response, input_lang)

# Mostrar preguntas sugeridas basadas en temas clave
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

# Barra lateral con historial de preguntas
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
