from transformers import pipeline



##################################################
# cargar pipeline de resumen del modelo
##################################################
def load_summarization_pipeline():

    # load summarizer model
    summarizer = pipeline(task="summarization", model="facebook/bart-large-cnn")

    return summarizer



##################################################
# generar resumen de los documentos
##################################################
def summarize(summarizer, documents):

    summary = ""
    tokenizer = summarizer.tokenizer

    for doc in documents:

        # calculate num of tokens
        num_tokens = len(tokenizer(doc.page_content).get("input_ids"))

        # compute summary
        doc_summary = summarizer(doc.page_content, max_length=int(num_tokens*0.6))
        summary += " " + doc_summary[0].get("summary_text")

    return summary[1:]

