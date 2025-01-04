import json
from main_langchain import initialization, generate_response

db, translator = initialization()
question = "How many km2 does Vaticano City have?"
response = json.loads(generate_response(question, db, translator))['final_response']
print('Response: ', response)