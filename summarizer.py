from transformers import pipeline

# Cargar pipeline de resumen del modelo
def load_summarization_pipeline():
    # Cargar el modelo de resumen preentrenado
    summarizer = pipeline(task="summarization", model="facebook/bart-large-cnn")
    return summarizer


# Generar resumen de los documentos
def summarize(summarizer, documents):
    summary = ""
    # Acceder al tokenizador asociado al modelo
    tokenizer = summarizer.tokenizer

    for doc in documents:
        # Calcular el número de tokens en el contenido del documento
        num_tokens = len(tokenizer(doc.page_content).get("input_ids"))

        # Generar el resumen del documento con un límite proporcional a los tokens
        doc_summary = summarizer(
            doc.page_content, 
            max_length = int(num_tokens*0.6)
            )
        # Agregar el texto resumido al resultado final
        summary += " " + doc_summary[0].get("summary_text")

    # Devolver el resumen completo, eliminando el primer espacio en blanco
    return summary[1:]
