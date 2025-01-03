

import os 
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import requests
import json
import gensim
from translator import load_translation_pipeline, translate_forward, translate_backwards
from gensim import corpora

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


def preprocess_documents(documents):
    # Tokenization and stopword removal
    stopwords = set(gensim.parsing.preprocessing.STOPWORDS)
    processed_docs = []
    for doc in documents:
        tokens = gensim.utils.simple_preprocess(doc.page_content)
        tokens = [token for token in tokens if token not in stopwords]
        processed_docs.append(tokens)
    return processed_docs

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
question = "¿Cual es la zona más cercana a la playa de Barelona?"
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

    context = "\n\n".join([doc.page_content for doc in searchDocs])
    # Preprocess the context (relevant documents) for LDA topic extraction
    processed_context = preprocess_documents([Document(page_content=context)])
    
    # Create a dictionary and corpus for the search context
    context_dictionary = corpora.Dictionary(processed_context)
    context_corpus = [context_dictionary.doc2bow(doc) for doc in processed_context]

    # Build the LDA model for the search context
    context_lda_model = gensim.models.LdaMulticore(context_corpus, num_topics=5, id2word=context_dictionary, passes=10, workers=2)

    # Get the topics
    context_topics = context_lda_model.print_topics(num_words=5)  # Show top 5 words for each topic
    print("Top Topics from the Search Results:")
    for topic in context_topics:
        print(topic)

    #prompt
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
    prompt = "What to visit in Barcelona?"

    # traducción
    lang, prompt = translate_forward(translator, prompt)
    response = generate_response(system, prompt)
    print(response)
    print(lang)
    final_response = translate_backwards(translator, response['response'], lang)
    print("Generated Response:\n", final_response)

