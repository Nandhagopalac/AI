from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

user_input = input("Enter your your input prompt here: ")
system_input = " Restrict the usage of tockes not more than 200, results should be in bullet in points always"

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
responces = client.responses.create(

model="gpt-4.1-mini",
input=user_input,
instructions=system_input

)

print(responces.output_text)