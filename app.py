from flask import Flask, render_template, request, jsonify
import pandas as pd
import re
from nltk.chat.util import Chat, reflections

app = Flask(__name__)

# Carrega a base de dados
df_copa = pd.read_csv('copa.csv')

# Configura o NLTK para conversas e mantém o ciclo ativo
pares = [
    [r"oi|ola|olá|opa", ["Olá, craque! Sou o CopaBot. Quer saber quem levantou a taça em qual ano?"]],
    [r"qual( é| e)? o seu nome?", ["Sou o CopaBot, o camisa 10 dos dados da Copa do Mundo! Qual ano você quer consultar agora?"]],
    [r"obrigado|vlw|valeu", ["Tamo junto! Tem mais algum ano da Copa que você queira descobrir?"]]
]
chatbot_basico = Chat(pares, reflections)

# Função de busca no Pandas com perguntas de engajamento
def buscar_dados_copa(ano):
    try:
        ano = int(ano)
        resultado = df_copa[df_copa['Ano'] == ano]
        
        if not resultado.empty:
            campeao = resultado.iloc[0]['Campeao']
            sede = resultado.iloc[0]['Sede']
            vice = resultado.iloc[0]['Vice']
            # Adicionamos uma pergunta no final da resposta de sucesso!
            return f"🏆 Na Copa de {ano} ({sede}), a seleção campeã foi: {campeao}! A {vice} ficou com o vice-campeonato. Sobre qual outro ano você quer saber?"
        else:
            # Mantém o usuário no jogo mesmo se a Copa não for encontrada
            return f"Putz, o VAR me avisou aqui que não temos dados sobre a Copa de {ano} ou ela não existiu. Tente anos entre 1994 e 2022. Qual ano vamos buscar agora?"
    except ValueError:
        return "Formato de ano inválido. Digite algo como 2002. Qual ano você quer tentar?"

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
            # Devolve a bola para o usuário
            resposta = "Desculpe, não captei a jogada. Me pergunte sobre o campeão de um ano específico, tipo: 'Quem ganhou em 2014?'"
            
    return jsonify({"response": resposta})

if __name__ == "__main__":
    app.run(debug=True)