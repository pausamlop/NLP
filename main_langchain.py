import os 
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import requests
import json

# Load the document, split it into chunks, embed each chunk and load it into the vector store.
folder_path = "./guides/"

documents = []
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

class CustomTextLoader(TextLoader):
    def load(self):
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        # Wrap the text content into a Document object
        return [Document(page_content=text)]
    
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path):
        # Load the document
        raw_documents = CustomTextLoader(file_path).load()
        # Split the document into chunks
        document = text_splitter.split_documents(raw_documents)
        # Add the chunks to the main list
        documents.extend(document)


# Define the path to the pre-trained model you want to use
modelPath = "sentence-transformers/all-MiniLM-l6-v2"

# Create a dictionary with model configuration options, specifying to use the CPU for computations
model_kwargs = {'device':'cpu'}

# Create a dictionary with encoding options, specifically setting 'normalize_embeddings' to False
encode_kwargs = {'normalize_embeddings': False}

# Initialize an instance of HuggingFaceEmbeddings with the specified parameters
embeddings = HuggingFaceEmbeddings(
    model_name=modelPath,     # Provide the pre-trained model's path
    model_kwargs=model_kwargs, # Pass the model configuration options
    encode_kwargs=encode_kwargs # Pass the encoding options
)

# Vector Stores
db = FAISS.from_documents(documents, embeddings)
question = "¿Cuántos km2 tiene la Ciudad del Vaticano?"
searchDocs = db.similarity_search(question)
print(searchDocs[0].page_content)


from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama

CHROMA_PATH = "./chroma"
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3:8b"

#---------------------------------------------------------------------------------

# Ensure Ollama Models are Downloaded
def ensure_ollama_model(model_name):
    try:
        Ollama(model=model_name)  # Attempt to load the model
        print(f"Ollama model '{model_name}' found.")
    except Exception as e:
        raise Exception(f"Ollama model '{model_name}' not found. Please download it using 'ollama pull {model_name}'")

ensure_ollama_model(EMBEDDING_MODEL)
ensure_ollama_model(LLM_MODEL)

#---------------------------------------------------------------------------------

# Generate response from ollama
def generate_response(system, prompt):
    data = {
        "model": "llama3.1:8b-instruct-q8_0",
        "system": system,
        "prompt": prompt,
        "stream": False,
    }

    url="http://kumo01:11434/api/generate"

    headers = {"Content-Type": "application/json" }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error: {response.status_code}, {response.text}"

    except Exception as e:
        return f"An error occurred: {str(e)}"

#---------------------------------------------------------------------------------
if searchDocs != []:

    # prompt
    context = "\n\n".join([doc.page_content for doc in searchDocs])
    prompt = PromptTemplate(
        template="""Using the following context, answer the question. 

        ## Context:
        {context}

        ## Question:
        {question}

        ## Answer:
        """,
        input_variables=["context", "query"]
    )

    system = "You are a helpful AI Assistant"
    prompt = "what are you?"
    
    response = generate_response(system, prompt)
    print("Generated Response:\n", response)
