# Asignatura de Procesamiento del Lenguaje Natural

- Camino Rodríguez
- Natalia Centeno
- Lucía Yan 
- Paula Samper
  
## Chatbot para responder preguntas de una base de datos documental de guías de viajes

EL chatbot responde preguntas sobre Barcelona, Los Ángeles, París, Roma y Zurich según la información que encuentra en una serie de guías de viaje.
A parte de responder preguntas, se han implementado las siguientes funcionalidades adicionales:
- Generación de resúmenes opcionales de los documentos de los que se extrae la información
- Traducción (+50 idiomas) para que la comunicación se haga en el idioma que utilice el usuario.
- Sugerencias de preguntas personalizadas.
- Historial de preguntas.
- Leer la respuesta en voz alta en el idioma de entrada (siempre que el idioma esté soportado).

## Ejecución

Para correr la aplicación, ejecutar:

~~~
conda env create -f streamlit-env.yml
conda activate streamlit-env
streamlit run app.py
~~~
