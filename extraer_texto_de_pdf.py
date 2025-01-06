import os
import requests
import pdfplumber

#Se descarga el PDF desde la URL y se guarda localmente
urls = [
    "https://www.grupomasviajes.com/GuiasViaje/GuiaViajeBARCELONA.pdf",
    "https://www.grupomasviajes.com/GuiasViaje/GuiaViajeLOSANGELES.pdf",
    "https://www.grupomasviajes.com/GuiasViaje/GuiaViajePARIS.pdf",
    "https://www.grupomasviajes.com/guiasviaje/GuiaViajeROMA.pdf",
    "https://www.grupomasviajes.com/GuiasViaje/GuiaViajeZURICH.pdf",
]
output_path = "guides/"
# Download and extract content
for i, url in enumerate(urls):
    txt_filename = f"guide_{i + 1}.txt"
    # Step 1: Download the PDF
    response = requests.get(url)
    if response.status_code == 200:
        # Save the content to a local file
        pdf_path = "temp.pdf"
        with open(pdf_path, "wb") as f:
            f.write(response.content)

    #Se extrae el texto del PDF
    all_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            #Se eliminan los saltos de línea. Todo el texto queda separado por punto y seguidos.
            text = text.replace("\n", " ")
            text = " ".join(text.split())
            text = text.replace("", "")
            # Se elimina la frase "Sugerimos contratar" en los documentos de "grupomasviajes"
            text = text.replace("Sugerimos contratar", "")
            all_text += text
    with open(os.path.join(output_path, txt_filename), "w", encoding="utf-8") as txt_file:
        txt_file.write(all_text)
