import gensim
import spacy
import json
import requests
from gensim import corpora
from gensim.parsing.preprocessing import STOPWORDS


# Cargar el modelo de spaCy en español
nlp = spacy.load("en_core_web_md")

# Ampliar stopwords con el conjunto de stopwords de spaCy
stopwords = STOPWORDS.union(nlp.Defaults.stop_words)

def extract_top_keywords(context):
    print('Extracting Keywords')
    # Tokenizar el contexto
    doc = nlp(context)
    tokens = [token.text.lower() for token in doc if token.text.lower() not in stopwords and not token.is_punct and len(token.text) > 2]
    
    # Crear diccionario y corpus
    context_dictionary = corpora.Dictionary([tokens])
    context_corpus = [context_dictionary.doc2bow(doc) for doc in [tokens]]

    # Crear el modelo LDA con un solo tema
    lda_model = gensim.models.LdaMulticore(context_corpus, num_topics=1, id2word=context_dictionary, passes=20, workers=4)

    # Obtener las 5 palabras más importantes del único tema generado
    keywords = lda_model.show_topics(num_topics=1, num_words=3, formatted=False)[0][1]
    
    # Extraer solo las palabras
    top_keywords = [word for word, _ in keywords]
    
    # Mostrar las palabras clave
    print("Top 5 Keywords from the Context:")
    print(", ".join(top_keywords))

    return top_keywords

    
def generate_question_from_context(topics):
    
    data = {
            "model": "llama3.1:8b-instruct-q8_0",
            "system": "You are an expert travel assistant helping users plan trips and answer questions about destinations, museums, landmarks, cuisine, and more. Your task is to generate suggestion questions based only on the provided topics.",
            "prompt":
                """Based on the following topics: {topics}, create a single engaging and meaningful question that relates to them. 
                The question should not simply repeat the topics, but should involve them to form an insightful inquiry.

                ## Answer:
                """.format(topics=topics),
            "stream": False,
        }

    url="http://kumo01:11434/api/generate"

    headers = {"Content-Type": "application/json" }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            print("Generated Response:\n", response.json()['response'])
            return response.json()['response']
        
        else:
            return f"Error: {response.status_code}, {response.text}"

    except Exception as e:
        return f"An error occurred: {str(e)}"
