from flask import Flask, render_template, request, jsonify
import pandas as pd
import re
from nltk.chat.util import Chat, reflections

app = Flask(__name__)

# Carrega a base de dados
df_copa = pd.read_csv('copa.csv')

# Configura o NLTK para conversas rápidas
pares = [
    [r"oi|ola|olá|opa", ["Olá, craque! Sou o CopaBot. Quer saber quem levantou a taça em qual ano?"]],
    [r"qual( é| e)? o seu nome?", ["Sou o CopaBot, o camisa 10 dos dados da Copa do Mundo!"]],
    [r"obrigado|vlw|valeu", ["Tamo junto! Se precisar de mais estatísticas, é só chamar."]]
]
chatbot_basico = Chat(pares, reflections)

# Função de busca no Pandas
def buscar_dados_copa(ano):
    try:
        ano = int(ano)
        resultado = df_copa[df_copa['Ano'] == ano]
        
        if not resultado.empty:
            campeao = resultado.iloc[0]['Campeao']
            sede = resultado.iloc[0]['Sede']
            vice = resultado.iloc[0]['Vice']
            return f"🏆 Na Copa de {ano} ({sede}), a seleção campeã foi: {campeao}! A {vice} ficou com o vice-campeonato."
        else:
            return f"Putz, o VAR me avisou aqui que não temos dados sobre a Copa de {ano} ou ela não existiu. Tente anos entre 1994 e 2022."
    except ValueError:
        return "Formato de ano inválido. Digite algo como 2002."

# Rotas Web
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.json.get("message")
    ano_encontrado = re.search(r'\b(19|20)\d{2}\b', user_input)
    
    if ano_encontrado:
        resposta = buscar_dados_copa(ano_encontrado.group())
    else:
        resposta = chatbot_basico.respond(user_input)
        if not resposta:
            resposta = "Desculpe, não captei a jogada. Tente perguntar sobre o campeão de um ano específico, tipo: 'Quem ganhou em 2014?'"
            
    return jsonify({"response": resposta})

if __name__ == "__main__":
    app.run(debug=True)