import os 
import json
import requests
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from bert_score import score
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from translator import load_translation_pipeline, translate_forward, translate_backwards
from summarizer import load_summarization_pipeline

# Clase personalizada para cargar documentos
class CustomTextLoader(TextLoader):
    def load(self):
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        # Envolver el contenido del texto en un objeto Document
        return [Document(page_content=text)]
    
def initialization():
    # Cargar el documento, dividirlo en fragmentos, embed cada fragmento y cargarlo.
    # Ruta de la carpeta que contiene las guías en texto
    folder_path = "./guides/"

    # Inicializar el pipeline de traducción
    translator = load_translation_pipeline()

    # Inicializar pipeline de resumen 
    summarizer = load_summarization_pipeline()

    # Lista para almacenar los documentos procesados
    documents = []

    # Configuración del divisor de texto (chunking)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

    # Cargar y procesar los documentos desde la carpeta especificada
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            # Cargar el documento
            raw_documents = CustomTextLoader(file_path).load()
            # Dividir el documento en fragmentos (chunks)
            document_chunks = text_splitter.split_documents(raw_documents)

            # Añadir la ruta del archivo como metadato en cada fragmento
            for chunk in document_chunks:
                chunk.metadata['source'] = file_path  # Aquí agregamos la ruta al metadato 'source'
            # Agregar los fragmentos procesados a la lista principal
            documents.extend(document_chunks)

    # Ruta al modelo preentrenado para embeddings
    modelPath = "sentence-transformers/all-MiniLM-l6-v2"

    # Configuración del modelo: uso de CPU
    model_kwargs = {'device':'cpu'}

    # Opciones de codificación: desactivar la normalización de embeddings
    encode_kwargs = {'normalize_embeddings': False}

    # Inicializar HuggingFaceEmbeddings con los parámetros especificados
    embeddings = HuggingFaceEmbeddings(
        model_name=modelPath,
        model_kwargs=model_kwargs, 
        encode_kwargs=encode_kwargs
    )

    # Crear el vector store con FAISS
    db = FAISS.from_documents(documents, embeddings)

    return db, translator, summarizer


# Calcula las métricas BERTScore (Precision, Recall, F1) entre una respuesta y un contexto dado.
def bertscore(response, context):

    # Calcula las métricas utilizando el idioma inglés ("en").
    precision, recall, f1score = score([response], [context], lang="en")

    # Guardar los resultados
    f = open("bertscore.txt", "a")
    f.write("Nueva comparacion:\n")
    f.write(f"Precision: {precision[0]}\n")
    f.write(f"Recall: {recall[0]}\n")
    f.write(f"F1 Score: {f1score[0]}\n\n")
    f.close()

    return

# Función para buscar documentos relevantes en el vector store
def rag(question, db):
    searchDocs = db.similarity_search(question)
    print("Documentos relevantes:")
    print(searchDocs[0].page_content)
    print(searchDocs[1].page_content)
    print(searchDocs[2].page_content)
    return searchDocs

# Generar respuesta usando Ollama
def generate_response(question, db, translator):
    # Buscar documentos relevantes usando la función RAG
    searchDocs = rag(question, db)
    if searchDocs !=[]:
        # Crear el contexto concatenando el contenido de los documentos relevantes
        context = "\n\n".join([doc.page_content for doc in searchDocs])

        # Recoger las URLs de los documentos relevantes
        documents = [{"source_url": doc.metadata.get("source")} for doc in searchDocs if 'source' in doc.metadata]

        # Traducir la pregunta al inglés y detectar el idioma original
        input_lang, question_en = translate_forward(translator, question)
        print(f"Idioma detectado: {input_lang}")
        
        data = {
            "model": "llama3.1:8b-instruct-q8_0",
            "system": (
            "You are an expert travel assistant helping users plan trips and answer "
            "questions about destinations, museums, landmarks, cuisine, and more. Respond "
            "clearly, concisely, and based only on the provided context. Always reply in "
            "the same language as the question."
            ),
            "prompt":
                """Using the following context, answer the question. 
                Act as an expert travel agency assistant. 
                Provide clear and accurate answers strictly based on the provided context. 
                Always reply in the same language as the question.


                ## Context:
                {context}

                ## Question:
                {question_en}

                ## Answer:
                """.format(context=context, question_en=question_en),
            "temperature": 0.6,
            "top_p": 0.9,
            "stream": False,
        }

        # Configuración de la URL y encabezados para la solicitud HTTP
        url="http://kumo01:11434/api/generate"
        headers = {"Content-Type": "application/json" }
        
        try:
            # Enviar la solicitud POST a la API
            response = requests.post(url, headers=headers, data=json.dumps(data))
            
            if response.status_code == 200:
                # Procesar la respuesta generada por la API
                print("Generated Response:\n", response.json()['response'])
                # print bertscore   
                bertscore(response.json()['response'], context)
                # Traducir la respuesta de vuelta al idioma original
                final_response = translate_backwards(translator, response.json()['response'], input_lang)
                print("Translated Response:\n", final_response)

                # Devolver la respuesta final, contexto, idioma y documentos relevantes
                return json.dumps({
                    'final_response': final_response,
                    'context': context,
                    'input_lang': input_lang,
                    'documents': documents
                })
            
            # Errores en la respuesta de la API
            else:
                return f"Error: {response.status_code}, {response.text}"
        # Errores durante la solicitud
        except Exception as e:
            return f"An error occurred: {str(e)}"
