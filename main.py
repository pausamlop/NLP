import os
import chromadb
from ollama import Client  # type: ignore

###############################################################################
# Crear cliente de ollama
# ---------------------------------------------------------------------------
# Ha debido de haber una actualización en la API de Ollama, por lo que poner la dirección como variable de entorno no funciona; hay que crearse un cliente en su lugar.
ollama_client = Client(
    host='http://kumo01.tsc.uc3m.es:11434',
    headers={'x-some-header': 'some-value'}
)

###############################################################################
# Indexado en la base de datos vectorial (ChromaDB) con embeddings de Ollama
# ---------------------------------------------------------------------------
# El código que usabais antes no os funcionaba porque estabais intentando generar embeddings con un modelo llama3.2, el cual no los proporciona. He descargado el modelo mxbai-embed-large y ya con eso sí podemos generar embeddings.
###############################################################################
llm_model_embeddings = 'mxbai-embed-large'
folder_path = "guides/"

documents = []
for filename in os.listdir(folder_path):
    with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as file:
        content = file.read()
        documents.append(content)


client = chromadb.Client()
collection = client.create_collection(name="docs")

# store each document in a vector embedding database
for i, d in enumerate(documents):
    response = ollama_client.embeddings(model=llm_model_embeddings, prompt=d)
    embedding = response["embedding"]
    collection.add(
        ids=[str(i)],
        embeddings=[embedding],
        documents=[d]
    )

###############################################################################
# Aquí lo que hacéis es dada una query (e.g., una pregunta) generar un embedding para esa query y buscar en la base de datos de embeddings el documento más relevante.
query = "How many km2 does the Ciudad del Vaticano have?"  # an example prompt

# generate an embedding for the prompt and retrieve the most relevant doc
response = ollama_client.embeddings(
    prompt=query,
    model=llm_model_embeddings
)
results = collection.query(
    query_embeddings=[response["embedding"]],
    n_results=1
)
data = results['documents'][0][0]
print(data)

llm_model = 'llama3.2'
# TODO: Continuad aquí con la parte de promting para dar respuesta a las preguntas de los usuarios
# generate a response combining the prompt and data we retrieved in step 2
output = ollama_client.generate(
  model="llama2",
  prompt=f"Using this data: {data}. Respond to this prompt: {query}"
)

print(output['response'])