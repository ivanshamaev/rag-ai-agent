from openai import OpenAI
from dotenv import load_dotenv
import os

# Загружаем .env в окружение
load_dotenv()
my_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=my_api_key) 

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Привет! Что ты умеешь?"}]
)

print(response.choices[0].message.content)
