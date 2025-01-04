import json
from main_langchain import generate_response

question = "How many km2 does Vaticano City have?"
response = json.loads(generate_response(question))['final_response']
print('Response: ', response)