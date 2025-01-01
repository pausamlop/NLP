import os
import requests
import pdfplumber
import chromadb
from ollama import Client  # type: ignore
from translator import load_translation_pipeline, translate_forward, translate_backwards

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

# Pipeline de traducción
translator = load_translation_pipeline()

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

prompt = "In which country is Rome? Please, answer briefly"

# traducción
lang, prompt = translate_forward(translator, prompt)


#Paso 3: Consultar la base de datos
response = ollama_client.embeddings(
    prompt=prompt,
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
    answer = translate_backwards(translator, answer[:1024], lang)
else:
    print("Lo siento, no encontré información relevante para tu pregunta.")


data = results['documents'][0][0]
print("Documento más relevante:")
# print(data)
