Before execution
conda create --name my_env
conda activate my_env
pip install -r requirements_v2.txt
python -m spacy download es_core_news_md
pip install -U langchain-huggingface


Run app:
python /usr/local/anaconda3/lib/python3.11/site-packages/streamlit/web/cli.py run app.py

