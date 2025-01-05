Before execution

conda create --name my_env

conda activate my_env

pip install -r requirements_v2.txt

python -m spacy download es_core_news_md

pip install -U langchain-huggingface


-------------------------------------------------------
(conda env export > streamlit-env.yml)

conda env create -f streamlit-env.yml

(conda remove -n streamlit-env --all)


Run app:

streamlit run app.py

