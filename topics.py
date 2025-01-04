import gensim
import spacy
from gensim import corpora
from gensim.parsing.preprocessing import STOPWORDS
from langchain.schema import Document


# Cargar el modelo de spaCy en español
nlp = spacy.load("es_core_news_md")

# Ampliar stopwords con el conjunto de stopwords de spaCy
stopwords = STOPWORDS.union(nlp.Defaults.stop_words)

# Preprocesar los documentos
def preprocess_documents(documents):
    processed_docs = []
    
    for doc in documents:
        # Realizar análisis de dependencias y entidades con SpaCy
        spacy_doc = nlp(doc.page_content)
        
        # Crear una lista para almacenar los tokens procesados
        tokens = []
        
        # Primero, identificamos las entidades nombradas y las unificamos
        # Usaremos un diccionario para almacenar entidades ya detectadas
        entity_tokens = []
        
        for ent in spacy_doc.ents:
            # Detectamos si la entidad es un lugar, monumento, etc.
            # Por ejemplo, "Big Ben" o "La Sagrada Familia"
            entity_tokens.append(ent.text)
        
        # Ahora sustituimos las entidades detectadas por un token único
        doc_text = doc.page_content
        for entity in entity_tokens:
            doc_text = doc_text.replace(entity, entity.replace(" ", "_"))  # Usamos un guion bajo para mantenerlo unido
        
        # Ahora tokenizamos de nuevo el texto
        spacy_doc = nlp(doc_text)  # Volvemos a procesar el texto con entidades unificadas
        
        for token in spacy_doc:
            # Si el token es una entidad nombrada o no es stopword y no es puntuación, lo agregamos
            if token.ent_type_ != "" or (token.text.lower() not in stopwords and not token.is_punct):
                tokens.append(token.text)

        processed_docs.append(tokens)
    
    return processed_docs

def extract_topics(context):
    # Preprocess the context (relevant documents) for LDA topic extraction
    processed_context = preprocess_documents([Document(page_content=context)])
    
    # Create a dictionary and corpus for the search context
    context_dictionary = corpora.Dictionary(processed_context)
    context_corpus = [context_dictionary.doc2bow(doc) for doc in processed_context]

    # Build the LDA model for the search context
    context_lda_model = gensim.models.LdaMulticore(context_corpus, num_topics=5, id2word=context_dictionary, passes=20, workers=4)

    # Get the topics
    context_topics = context_lda_model.print_topics(num_words=5)  # Show top 5 words for each topic
    print("Top Topics from the Search Results:")
    for topic in context_topics:
        print(topic)