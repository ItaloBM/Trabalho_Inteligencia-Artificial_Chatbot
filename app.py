from flask import Flask, render_template, request, jsonify
import pandas as pd
from nltk.chat.util import Chat, reflections
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# --- CONFIGURAÇÃO DO NLTK ---
# Baixa os pacotes necessários na primeira execução
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

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
    selecao_normalizada = selecao.strip().title()
    
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
    ranking = sorted(titulos_por_selecao.items(), key=lambda x: x[1], reverse=True)
    
    for selecao, titulos in ranking:
        anos = df_copa[df_copa['Campeao'] == selecao]['Ano'].tolist()
        anos_str = ", ".join(map(str, anos))
        resultado += f"⭐ {selecao}: {titulos} título{'s' if titulos > 1 else ''} ({anos_str})\n"
    
    resultado += "\nQuer detalhes de alguma seleção específica?"
    return resultado

def buscar_dados_copa(ano):
    """Busca dados gerais de uma copa pelo ano"""
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

# Configura o NLTK para conversas de saudação (Chatbot Básico)
pares = [
    [r"oi|ola|olá|opa|eae|e ai", ["Olá, craque! Sou o CopaBot. Quer saber sobre campeões, artilheiros ou títulos?"]],
    [r"qual( é| e)? o seu nome?", ["Sou o CopaBot, especialista em Copas do Mundo! O que você quer descobrir?"]],
    [r"obrigado|vlw|valeu|thanks", ["Tamo junto! Tem mais alguma pergunta sobre a Copa?"]],
    [r"tchau|ate|até|bye", ["Até a próxima Copa! ⚽🏆"]],
]
chatbot_basico = Chat(pares, reflections)

# --- IMPLEMENTAÇÃO DE PLN  ---
def processar_pergunta_nltk(pergunta):
    """
    Realiza Tokenização e Análise Semântica (remoção de stopwords) 
    para extrair a intenção e entidades (país, ano).
    """
    # 1. Tokenização
    tokens = word_tokenize(pergunta.lower(), language='portuguese')
    
    # 2. Remoção de Stopwords (Análise Semântica)
    stop_words = set(stopwords.words('portuguese'))
    tokens_uteis = [word for word in tokens if word not in stop_words and word.isalnum()]
    
    analise = {
        'intencao': 'indefinida',
        'pais': None,
        'ano': None
    }
    
    # Identificar Entidade Numérica (Ano)
    for token in tokens_uteis:
        if token.isdigit() and len(token) == 4 and (token.startswith('19') or token.startswith('20')):
            analise['ano'] = token
            break

    # Identificar Entidade (País)
    paises_conhecidos = ['brasil', 'argentina', 'alemanha', 'frança', 'franca', 'itália', 'italia', 'espanha', 'uruguai', 'inglaterra']
    for pais in paises_conhecidos:
        if pais in tokens_uteis:
            analise['pais'] = pais
            break 
            
    # Identificar Intenção
    if any(palavra in tokens_uteis for palavra in ['todos', 'ranking', 'lista', 'total']) and any(palavra in tokens_uteis for palavra in ['campeões', 'campeoes', 'títulos', 'titulos']):
        analise['intencao'] = 'listar_todos'
    elif any(palavra in tokens_uteis for palavra in ['artilheiro', 'goleador', 'artilharia', 'gols']):
        analise['intencao'] = 'buscar_artilheiro'
    elif any(palavra in tokens_uteis for palavra in ['campeão', 'campeao', 'vencedor', 'ganhou', 'título', 'títulos', 'titulos', 'copa']):
        if analise['pais']:
            analise['intencao'] = 'buscar_titulos_selecao'
        elif analise['ano']:
            analise['intencao'] = 'buscar_ano'

    # Se só mencionou um ano sem intenção clara, assume que quer os dados daquele ano
    if analise['ano'] and analise['intencao'] == 'indefinida':
         analise['intencao'] = 'buscar_ano'
            
    return analise

# Rotas Web
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.json.get("message")
    
    # 1. Pipeline de Linguagem Natural (PLN)
    entendimento = processar_pergunta_nltk(user_input)
    
    # 2. Responde baseado na extração semântica
    if entendimento['intencao'] == 'buscar_titulos_selecao' and entendimento['pais']:
        return jsonify({"response": buscar_titulos_selecao(entendimento['pais'])})
        
    if entendimento['intencao'] == 'listar_todos':
        return jsonify({"response": listar_todos_campeoes()})
        
    if entendimento['intencao'] == 'buscar_artilheiro':
        if entendimento['ano']:
            return jsonify({"response": buscar_artilheiro(entendimento['ano'])})
        else:
            return jsonify({"response": "De qual ano você quer saber o artilheiro? Digite algo como 'artilheiro 2014'."})
            
    if entendimento['intencao'] == 'buscar_ano' and entendimento['ano']:
        return jsonify({"response": buscar_dados_copa(entendimento['ano'])})
    
    # 3. Tenta o Chatbot Básico NLTK (Saudações)
    resposta_nltk = chatbot_basico.respond(user_input)
    if resposta_nltk:
        return jsonify({"response": resposta_nltk})

    # 4. Fallback Temporário (Até a Pessoa 1 implementar o Hugging Face)
    resposta_padrao = "Desculpe, não captei a jogada. Pergunte sobre:\n• Campeão de um ano (ex: '2014')\n• Títulos de uma seleção (ex: 'títulos Brasil')\n• Artilheiro (ex: 'artilheiro 2018')\n• Ranking completo (ex: 'todos os campeões')"
    return jsonify({"response": resposta_padrao})

if __name__ == "__main__":
    app.run(debug=True)