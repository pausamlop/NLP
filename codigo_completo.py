import os
import requests
import pdfplumber
import chromadb
from ollama import Client  # type: ignore
from langdetect import detect
from googletrans import Translator  # Usaremos Google Translate para traducción (instala googletrans==4.0.0-rc1)


def detect_language(text):
    return detect(text)

def translate_text(text, target_language):
    translator = Translator()
    translated = translator.translate(text, dest=target_language)
    return translated.text

###############################################################################
# Configuración
###############################################################################
# URLs de los PDFs
urls = [
    "https://www.grupomasviajes.com/GuiasViaje/GuiaViajeBARCELONA.pdf",
    "https://www.grupomasviajes.com/guiasviaje/GuiaViajeROMA.pdf",
    "https://www.grupomasviajes.com/GuiasViaje/GuiaViajeLONDRES.pdf",
]

# Ruta para almacenar los textos extraídos
output_path = "guides/"
os.makedirs(output_path, exist_ok=True)  # Crear carpeta si no existe

# Cliente de Ollama
ollama_client = Client(
    host="http://kumo01.tsc.uc3m.es:11434",
    headers={"x-some-header": "some-value"}
)

# Modelo para generar embeddings
llm_model_embeddings = "mxbai-embed-large"

###############################################################################
# Descargar y extraer texto de los PDFs
###############################################################################
documents = []  # Lista donde almacenaremos los textos de los documentos
for i, url in enumerate(urls):
    txt_filename = f"guide_{i + 1}.txt"
    pdf_path = "temp.pdf"

    # Descargar PDF
    response = requests.get(url)
    if response.status_code == 200:
        with open(pdf_path, "wb") as f:
            f.write(response.content)
    else:
        print(f"Error al descargar {url}")
        continue

    # Extraer texto del PDF
    all_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Limpieza del texto
                text = text.replace("\n", " ").replace("", "").replace("Sugerimos contratar", "")
                text = " ".join(text.split())
                all_text += text + " "

    # Guardar el texto extraído en un archivo local
    with open(os.path.join(output_path, txt_filename), "w", encoding="utf-8") as txt_file:
        txt_file.write(all_text)

    # Agregar texto a la lista de documentos
    documents.append(all_text)

###############################################################################
# Crear base de datos vectorial con ChromaDB
###############################################################################
client = chromadb.Client()
collection = client.create_collection(name="docs")  # Crear colección

# Generar embeddings y almacenar en la colección
for i, doc in enumerate(documents):
    response = ollama_client.embeddings(model=llm_model_embeddings, prompt=doc)
    embedding = response["embedding"]
    collection.add(
        ids=[str(i)],
        embeddings=[embedding],
        documents=[doc]
    )

print("Todos los documentos han sido indexados correctamente.")


###############################################################################
# Hacer una consulta a la base de datos + detección idioma
###############################################################################

prompt = "What are the main attractions in Rome?"

#Paso 1: detectar el idioma
language = detect_language(prompt)
print(f"Idioma detectado: {language}")

#Paso 2: Traducir ak español para antes de pasarle la pregunta al modelo
if language != 'es':
    print("Traduciendo pregunta al español...")
    translator = Translator()
    prompt_in_spanish = translator.translate(prompt, dest='es').text
else:
    prompt_in_spanish = prompt

#Paso 3: Consultar la base de datos
response = ollama_client.embeddings(
    prompt=prompt_in_spanish,
    model=llm_model_embeddings
)
results = collection.query(
    query_embeddings=[response["embedding"]],
    n_results=1
)

# El sistema busca el documento relevante
if len(results['documents']) > 0:
    relevant_document = results['documents'][0][0]
    answer = f"Se ha encontrado esta información: {relevant_document}"
    print("Respuesta del chatbot:")
    print(answer)
else:
    print("Lo siento, no encontré información relevante para tu pregunta.")


data = results['documents'][0][0]
print("Documento más relevante:")
print(data)
