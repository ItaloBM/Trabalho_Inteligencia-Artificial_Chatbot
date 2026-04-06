from flask import Flask, render_template, request, jsonify
import pandas as pd
import re
from nltk.chat.util import Chat, reflections
from collections import Counter

app = Flask(__name__)

# Carrega a base de dados
df_copa = pd.read_csv('copa.csv')

# Dados extras: Artilheiros por Copa
artilheiros = {
    1994: {"nome": "Oleg Salenko e Hristo Stoichkov", "gols": 6},
    1998: {"nome": "Davor Šuker", "gols": 6},
    2002: {"nome": "Ronaldo", "gols": 8},
    2006: {"nome": "Miroslav Klose", "gols": 5},
    2010: {"nome": "Thomas Müller", "gols": 5},
    2014: {"nome": "James Rodríguez", "gols": 6},
    2018: {"nome": "Harry Kane", "gols": 6},
    2022: {"nome": "Kylian Mbappé", "gols": 8}
}

def contar_titulos():
    """Retorna um dicionário com a contagem de títulos por seleção"""
    titulos = Counter(df_copa['Campeao'])
    return titulos

def buscar_titulos_selecao(selecao):
    """Busca quantos títulos uma seleção tem"""
    titulos_por_selecao = contar_titulos()
    
    # Normaliza o nome da seleção
    selecao_normalizada = selecao.strip().title()
    
    # Busca com variações
    for key in titulos_por_selecao.keys():
        if selecao_normalizada.lower() in key.lower() or key.lower() in selecao_normalizada.lower():
            quantidade = titulos_por_selecao[key]
            anos = df_copa[df_copa['Campeao'] == key]['Ano'].tolist()
            anos_str = ", ".join(map(str, anos))
            return f"🏆 {key} tem {quantidade} título{'s' if quantidade > 1 else ''} de Copa do Mundo! Campeã em: {anos_str}. Quer saber sobre outra seleção?"
    
    return f"Hmm, não encontrei títulos para '{selecao}'. Tente: Brasil, Argentina, Alemanha, França, Itália, Espanha... Qual você quer consultar?"

def buscar_artilheiro(ano):
    """Busca o artilheiro de uma Copa específica"""
    try:
        ano = int(ano)
        if ano in artilheiros:
            art = artilheiros[ano]
            return f"⚽ O artilheiro da Copa de {ano} foi {art['nome']} com {art['gols']} gols! Quer saber de outro ano?"
        else:
            return f"Não tenho dados do artilheiro da Copa de {ano}. Tenho informações de 1994 a 2022. Qual ano você quer?"
    except ValueError:
        return "Formato inválido. Digite algo como 'artilheiro 2014'."

def listar_todos_campeoes():
    """Lista todos os campeões e seus títulos"""
    titulos_por_selecao = contar_titulos()
    resultado = "🏆 RANKING DE CAMPEÕES MUNDIAIS:\n\n"
    
    # Ordena por quantidade de títulos
    ranking = sorted(titulos_por_selecao.items(), key=lambda x: x[1], reverse=True)
    
    for selecao, titulos in ranking:
        anos = df_copa[df_copa['Campeao'] == selecao]['Ano'].tolist()
        anos_str = ", ".join(map(str, anos))
        resultado += f"⭐ {selecao}: {titulos} título{'s' if titulos > 1 else ''} ({anos_str})\n"
    
    resultado += "\nQuer detalhes de alguma seleção específica?"
    return resultado
 
titulos_por_selecao = contar_titulos()

# Configura o NLTK para conversas e mantém o ciclo ativo
pares = [
    [r"oi|ola|olá|opa|eae|e ai", ["Olá, craque! Sou o CopaBot. Quer saber sobre campeões, artilheiros ou títulos?"]],
    [r"qual( é| e)? o seu nome?", ["Sou o CopaBot, especialista em Copas do Mundo! O que você quer descobrir?"]],
    [r"obrigado|vlw|valeu|thanks", ["Tamo junto! Tem mais alguma pergunta sobre a Copa?"]],
    [r"tchau|ate|até|bye", ["Até a próxima Copa! ⚽🏆"]],
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
            terceiro = resultado.iloc[0]['Terceiro']
            return f"🏆 Na Copa de {ano} ({sede}), a seleção campeã foi: {campeao}! A {vice} ficou com o vice-campeonato e {terceiro} em terceiro. Sobre qual outro ano você quer saber?"
        else:
            return f"Putz, o VAR me avisou aqui que não temos dados sobre a Copa de {ano}. Tente anos entre 1994 e 2022. Qual ano vamos buscar agora?"
    except ValueError:
        return "Formato de ano inválido. Digite algo como 2002. Qual ano você quer tentar?"

# Rotas Web
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.json.get("message").lower()
    
    # Verifica se é pergunta sobre títulos de uma seleção
    if re.search(r'(titulo|titulos|quantos|quantas|copa).*?(brasil|argentina|alemanha|franca|italia|espanha|uruguai|inglaterra)', user_input):
        match = re.search(r'(brasil|argentina|alemanha|franca|italia|espanha|uruguai|inglaterra)', user_input)
        if match:
            resposta = buscar_titulos_selecao(match.group(1))
            return jsonify({"response": resposta})
    
    # Verifica se quer listar todos os campeões
    if re.search(r'(todos|ranking|lista|campeoes|campeões|total)', user_input) and re.search(r'(titulo|titulos|campe)', user_input):
        resposta = listar_todos_campeoes()
        return jsonify({"response": resposta})
    
    # Verifica se é pergunta sobre artilheiro
    if re.search(r'artilheiro|goleador|artilharia', user_input):
        ano_encontrado = re.search(r'\b(19|20)\d{2}\b', user_input)
        if ano_encontrado:
            resposta = buscar_artilheiro(ano_encontrado.group())
        else:
            resposta = "De qual ano você quer saber o artilheiro? Digite algo como 'artilheiro 2014'."
        return jsonify({"response": resposta})
    
    # Busca por ano específico
    ano_encontrado = re.search(r'\b(19|20)\d{2}\b', user_input)
    if ano_encontrado:
        resposta = buscar_dados_copa(ano_encontrado.group())
    else:
        resposta = chatbot_basico.respond(user_input)
        if not resposta:
            resposta = "Desculpe, não captei a jogada. Pergunte sobre:\n• Campeão de um ano (ex: '2014')\n• Títulos de uma seleção (ex: 'títulos Brasil')\n• Artilheiro (ex: 'artilheiro 2018')\n• Ranking completo (ex: 'todos os campeões')"
            
    return jsonify({"response": resposta})

if __name__ == "__main__":
    app.run(debug=True)