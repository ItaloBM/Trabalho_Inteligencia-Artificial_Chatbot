import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

# Em vez de passar na URL como key=..., vamos tentar como Bearer Token
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "contents": [{"parts": [{"text": "Diga SUCESSO e nada mais."}]}]
}

print("Testando a API via REST com Bearer Token...")
response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print("SUCESSO ABSOLUTO!")
    print("Resposta:", response.json()['candidates'][0]['content']['parts'][0]['text'])
else:
    print("FALHA. Status:", response.status_code)
    print("Detalhes:", response.text)
