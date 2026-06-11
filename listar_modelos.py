import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

print("Testando conexao com a API do Google...")
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key or api_key == "sua_chave_aqui":
    print("ERRO: Chave API nao encontrada no arquivo .env!")
    exit(1)

genai.configure(api_key=api_key)

print("\nModelos disponiveis para a sua chave:")
try:
    models = genai.list_models()
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"ERRO AO LISTAR MODELOS: {e}")
