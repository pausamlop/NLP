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
python -m spacy download en_core_web_md
streamlit run app.py
~~~

## Referencias

```bibtex
@article{DBLP:journals/corr/abs-1910-13461,
    author        = {Mike Lewis and Yinhan Liu and Naman Goyal and Marjan Ghazvininejad and Abdelrahman Mohamed and Omer Levy and Veselin Stoyanov and Luke Zettlemoyer},
    title         = {{BART:} Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension},
    journal       = {CoRR},
    volume        = {abs/1910.13461},
    year          = {2019},
    url           = {http://arxiv.org/abs/1910.13461},
    eprinttype    = {arXiv},
    eprint        = {1910.13461},
    timestamp     = {Thu, 31 Oct 2019 14:02:26 +0100},
    biburl        = {https://dblp.org/rec/journals/corr/abs-1910-13461.bib},
    bibsource     = {dblp computer science bibliography, https://dblp.org}
}

@article{tang2020multilingual,
    author        = {Yuqing Tang and Chau Tran and Xian Li and Peng-Jen Chen and Naman Goyal and Vishrav Chaudhary and Jiatao Gu and Angela Fan},
    title         = {Multilingual Translation with Extensible Multilingual Pretraining and Finetuning},
    year          = {2020},
    eprint        = {2008.00401},
    archivePrefix = {arXiv},
    primaryClass  = {cs.CL}
}
