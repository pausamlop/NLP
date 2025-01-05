import os 
import json
import requests
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from translator import load_translation_pipeline, translate_forward, translate_backwards
from summarizer import load_summarization_pipeline
# from topics import extract_topics

class CustomTextLoader(TextLoader):
    def load(self):
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        # Wrap the text content into a Document object
        return [Document(page_content=text)]
        
def initialization():
    # Load the document, split it into chunks, embed each chunk and load it into the vector store.
    folder_path = "./guides/"

    # Pipeline de traducción
    translator = load_translation_pipeline()

    # Pipeline de resumen 
    summarizer = load_summarization_pipeline()

    documents = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            # Load the document
            raw_documents = CustomTextLoader(file_path).load()
            # Split the document into chunks
            document = text_splitter.split_documents(raw_documents)
            # Add the chunks to the main list
            documents.extend(document)

    # Initialize an instance of HuggingFaceEmbeddings with the specified parameters
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-l6-v2",     # Provide the pre-trained model's path
        model_kwargs={'device':'cpu'}, # Pass the model configuration options
        encode_kwargs={'normalize_embeddings': False} # Pass the encoding options
    )

    # Vector Stores
    db = FAISS.from_documents(documents, embeddings)
    
    return db, translator, summarizer

def rag(question, db):
    searchDocs = db.similarity_search(question)
    print(searchDocs[0].page_content)
    print(searchDocs[1].page_content)
    print(searchDocs[2].page_content)
    return searchDocs

# Generate response from ollama
def generate_response(question, db, translator):
    searchDocs = rag(question, db)
    if searchDocs !=[]:
        context = "\n\n".join([doc.page_content for doc in searchDocs])
        # extract_topics(context)

        # traducción
        input_lang, question_en = translate_forward(translator, question)
        print(input_lang)
        
        data = {
            "model": "llama3.1:8b-instruct-q8_0",
            "system": "You are an expert travel assistant helping users plan trips and answer questions about destinations, museums, landmarks, cuisine, and more. Respond clearly, concisely, and based only on the provided context. Always reply in the same language as the question.",
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
            "stream": False,
        }

        url="http://kumo01:11434/api/generate"

        headers = {"Content-Type": "application/json" }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                print("Generated Response:\n", response.json()['response'])
                final_response = translate_backwards(translator, response.json()['response'], input_lang)
                print("Translated Response:\n", final_response)

                return json.dumps({'final_response': final_response, 'context': context})
                
            else:
                return f"Error: {response.status_code}, {response.text}"

        except Exception as e:
            return f"An error occurred: {str(e)}"
        
# question = "How many km2 does Vaticano City have?"
# response = json.loads(generate_response(question))['final_response']
# print('response: ', response)