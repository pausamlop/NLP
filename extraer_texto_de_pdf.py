import os
import requests
import pdfplumber

# Se descarga el PDF desde la URL y se guarda localmente
# URLs de las guías en PDF
urls = [
    "https://www.grupomasviajes.com/GuiasViaje/GuiaViajeBARCELONA.pdf",
    "https://www.grupomasviajes.com/GuiasViaje/GuiaViajeLOSANGELES.pdf",
    "https://www.grupomasviajes.com/GuiasViaje/GuiaViajePARIS.pdf",
    "https://www.grupomasviajes.com/guiasviaje/GuiaViajeROMA.pdf",
    "https://www.grupomasviajes.com/GuiasViaje/GuiaViajeZURICH.pdf",
]

# Directorio donde se guardarán los archivos .txt extraídos
output_path = "guides/"

# Procesar cada URL de la lista
for i, url in enumerate(urls):
    # Nombre del archivo de texto extraído
    txt_filename = f"guide_{i + 1}.txt"

    # Paso 1: Descargar el PDF desde la URL
    response = requests.get(url)
    if response.status_code == 200:
        # Guardar el PDF temporalmente
        pdf_path = "temp.pdf"
        with open(pdf_path, "wb") as f:
            f.write(response.content)

    # Paso 2: Extraer texto del PDF
    all_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            # Limpiar el texto extraído:
            # Reemplazar saltos de línea por espacios
            text = text.replace("\n", " ")
            # Eliminar espacios redundantes
            text = " ".join(text.split())
            # Eliminar caracteres no deseados
            text = text.replace("", "")
            # Se elimina la frase "Sugerimos contratar" en los documentos de "grupomasviajes"
            text = text.replace("Sugerimos contratar", "")

            # Agregar el texto limpio
            all_text += text

    # Paso 3: Guardar el texto extraído en un archivo .txt
    with open(os.path.join(output_path, txt_filename), "w", encoding="utf-8") as txt_file:
        txt_file.write(all_text)
