import os 
import json
import requests
from flask import jsonify
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from translator import load_translation_pipeline, translate_forward, translate_backwards

from topics import extract_topics

# Load the document, split it into chunks, embed each chunk and load it into the vector store.
folder_path = "./guides/"

# Pipeline de traducción
translator = load_translation_pipeline()

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

question = "¿Dónde está el Vaticano?"

def rag(question):
    searchDocs = db.similarity_search(question)
    print(searchDocs[0].page_content)
    print(searchDocs[1].page_content)
    print(searchDocs[2].page_content)
    return searchDocs

# Generate response from ollama
def generate_response():
    searchDocs = rag(question)
    if searchDocs !=[]:
        context = "\n\n".join([doc.page_content for doc in searchDocs])
        extract_topics(context)

        # traducción
        lang, question_en = translate_forward(translator, question)
        print(lang)
        
        data = {
            "model": "llama3.1:8b-instruct-q8_0",
            "system": "You are a helpful AI Assistant",
            "prompt": PromptTemplate(template=
                """Using the following context, answer the question. 

                    ## Context:
                    {context}

                    ## Question:
                    {question_en}

                    ## Answer:
                    """,
                    input_variables=["context", "question_en"]
                )
,
            "stream": False,
        }

        url="http://kumo01:11434/api/generate"

        headers = {"Content-Type": "application/json" }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                print("Generated Response:\n", final_response)
                final_response = translate_backwards(translator, response['response'], lang)
                print("Translated Response:\n", final_response)
                return jsonify({'final_response': final_response})
                
            else:
                return f"Error: {response.status_code}, {response.text}"

        except Exception as e:
            return f"An error occurred: {str(e)}"

