import os
import ollama
import chromadb

folder_path = "guides/"
documents = []

for filename in os.listdir(folder_path):
    with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as file:
        content = file.read()
        documents.append(content)

os.environ["OLLAMA_HOST"] = "http://kumo01:11434/api/generate"
llm_model = 'llama3.2'
client = chromadb.Client()
collection = client.create_collection(name="docs")

# store each document in a vector embedding database
for i, d in enumerate(documents):
  response = ollama.embeddings(model=llm_model, prompt=d)
  embedding = response["embedding"]
  collection.add(
    ids=[str(i)],
    embeddings=[embedding],
    documents=[d]
  )

# an example prompt
prompt = "How many km2 does the Ciudad del Vaticano have?"

# generate an embedding for the prompt and retrieve the most relevant doc
response = ollama.embeddings(
  prompt=prompt,
  model=llm_model
)
results = collection.query(
  query_embeddings=[response["embedding"]],
  n_results=1
)
data = results['documents'][0][0]