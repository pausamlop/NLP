import gensim
import spacy
from gensim import corpora
from gensim.parsing.preprocessing import STOPWORDS
from langchain.schema import Document
from transformers import pipeline


# Cargar el modelo de spaCy en español
nlp = spacy.load("es_core_news_md")

# Ampliar stopwords con el conjunto de stopwords de spaCy
stopwords = STOPWORDS.union(nlp.Defaults.stop_words)

# Preprocesar los documentos
def preprocess_documents(documents):
    processed_docs = []
    
    for doc in documents:
        spacy_doc = nlp(doc.page_content)
        tokens = [
            token.text.lower()
            for token in spacy_doc
            if token.text.lower() not in stopwords and not token.is_punct and len(token.text) > 2
        ]
        processed_docs.append(tokens)
    
    return processed_docs

def extract_top_keywords(context):
    # Preprocesar el texto
    processed_context = preprocess_documents([Document(page_content=context)])
    
    # Crear diccionario y corpus
    context_dictionary = corpora.Dictionary(processed_context)
    context_corpus = [context_dictionary.doc2bow(doc) for doc in processed_context]

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

# Cargar el pipeline de generación de preguntas
qg_pipeline = pipeline("text2text-generation", model="t5-base")

def generate_question_from_context(topics):
    # Crear un contexto más enfocado para generar preguntas sobre los temas
    prompt = f"""
    Based on the following topics: {', '.join(topics)}, create a single engaging and meaningful question that relates to them. 
    The question should not simply repeat the topics, but should involve them to form an insightful inquiry.
    """
    question = qg_pipeline(prompt)
    return question[0]['generated_text']
