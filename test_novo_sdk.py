import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
print("Testando o NOVO SDK google.genai...")

api_key = os.environ.get("GEMINI_API_KEY")
try:
    client = genai.Client(api_key=api_key)
    # Tenta usar um dos modelos mais novos
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Diga a palavra SUCESSO e nada mais.'
    )
    print("RESPOSTA DA IA:", response.text)
except Exception as e:
    print("ERRO:", e)
