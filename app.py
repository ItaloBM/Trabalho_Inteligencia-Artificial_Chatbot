from flask import Flask, render_template, request, jsonify
import pandas as pd
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.chat.util import Chat, reflections
import os

# ─── CONFIGURAÇÃO DO NLTK  ──────────────────────────────────────
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('stopwords')

# ─── CONFIGURAÇÃO DO RAG  ─────────────────────────────
try:
    from rag_engine import gerar_resposta_rag
    RAG_DISPONIVEL = True
except Exception as e:
    print(f"[AVISO] RAG não disponível: {e}")
    print("[AVISO] Execute 'python build_vector_db.py' para ativar o modo RAG.")
    RAG_DISPONIVEL = False

app = Flask(__name__)

# ─── DADOS LOCAIS ────────────────────────────────────────────────────────────
df_copa = pd.read_csv('copa.csv')

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
    return Counter(df_copa['Campeao'])

def buscar_titulos_selecao(selecao):
    titulos_por_selecao = contar_titulos()
    selecao_normalizada = selecao.strip().title()
    for key in titulos_por_selecao.keys():
        if selecao_normalizada.lower() in key.lower() or key.lower() in selecao_normalizada.lower():
            quantidade = titulos_por_selecao[key]
            anos = df_copa[df_copa['Campeao'] == key]['Ano'].tolist()
            anos_str = ", ".join(map(str, anos))
            return f"🏆 {key} tem {quantidade} título{'s' if quantidade > 1 else ''} de Copa do Mundo! Campeã em: {anos_str}."
    return None

def buscar_artilheiro(ano):
    try:
        ano = int(ano)
        if ano in artilheiros:
            art = artilheiros[ano]
            return f"⚽ O artilheiro da Copa de {ano} foi {art['nome']} com {art['gols']} gols!"
        return None
    except ValueError:
        return None

def listar_todos_campeoes():
    titulos_por_selecao = contar_titulos()
    resultado = "🏆 RANKING DE CAMPEÕES MUNDIAIS:\n\n"
    ranking = sorted(titulos_por_selecao.items(), key=lambda x: x[1], reverse=True)
    for selecao, titulos in ranking:
        anos = df_copa[df_copa['Campeao'] == selecao]['Ano'].tolist()
        anos_str = ", ".join(map(str, anos))
        resultado += f"⭐ {selecao}: {titulos} título{'s' if titulos > 1 else ''} ({anos_str})\n"
    return resultado

def buscar_dados_copa(ano):
    try:
        ano = int(ano)
        resultado = df_copa[df_copa['Ano'] == ano]
        if not resultado.empty:
            campeao = resultado.iloc[0]['Campeao']
            sede = resultado.iloc[0]['Sede']
            vice = resultado.iloc[0]['Vice']
            terceiro = resultado.iloc[0]['Terceiro']
            return f"🏆 Na Copa de {ano} ({sede}), a seleção campeã foi: {campeao}! A {vice} ficou com o vice-campeonato e {terceiro} em terceiro."
        return None
    except ValueError:
        return None

# ─── FUNÇÃO INTELIGENTE DE PLN  ─────────────────────────────────
def processar_pergunta_nltk(pergunta):
    tokens = word_tokenize(pergunta.lower(), language='portuguese')
    stop_words = set(stopwords.words('portuguese'))
    tokens_uteis = [word for word in tokens if word not in stop_words and word.isalnum()]
    
    analise = {'intencao': 'indefinida', 'pais': None, 'ano': None}
    
    for token in tokens_uteis:
        if token.isdigit() and len(token) == 4 and (token.startswith('19') or token.startswith('20')):
            analise['ano'] = token
            break

    paises_conhecidos = ['brasil', 'argentina', 'alemanha', 'frança', 'franca', 'itália', 'italia', 'espanha', 'uruguai', 'inglaterra']
    for pais in paises_conhecidos:
        if pais in tokens_uteis:
            analise['pais'] = pais
            break 
            
    if any(palavra in tokens_uteis for palavra in ['todos', 'ranking', 'lista', 'total']) and any(palavra in tokens_uteis for palavra in ['campeões', 'campeoes', 'títulos', 'titulos']):
        analise['intencao'] = 'listar_todos'
    elif any(palavra in tokens_uteis for palavra in ['artilheiro', 'goleador', 'artilharia', 'gols']):
        analise['intencao'] = 'buscar_artilheiro'
    elif any(palavra in tokens_uteis for palavra in ['campeão', 'campeao', 'vencedor', 'ganhou', 'título', 'títulos', 'titulos', 'copa']):
        if analise['pais']:
            analise['intencao'] = 'buscar_titulos_selecao'
        elif analise['ano']:
            analise['intencao'] = 'buscar_ano'

    if analise['ano'] and analise['intencao'] == 'indefinida':
         analise['intencao'] = 'buscar_ano'
            
    return analise

# Chatbot Básico para saudações
pares = [
    [r"oi|ola|olá|opa|eae|e ai", ["Olá, craque! Sou o CopaBot. Quer saber sobre campeões, artilheiros ou títulos?"]],
    [r"qual( é| e)? o seu nome?", ["Sou o CopaBot, especialista em Copas do Mundo!"]],
    [r"obrigado|vlw|valeu|thanks", ["Tamo junto! Tem mais alguma pergunta sobre a Copa?"]],
]
chatbot_basico = Chat(pares, reflections)

# ─── ROTAS WEB ───────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.json.get("message")
    
    # 1. TENTA PRIMEIRO A SUA INTELIGÊNCIA NLTK (Busca Exata e Rápida)
    entendimento = processar_pergunta_nltk(user_input)
    
    if entendimento['intencao'] == 'buscar_titulos_selecao' and entendimento['pais']:
        resp = buscar_titulos_selecao(entendimento['pais'])
        if resp: return jsonify({"response": resp, "modo": "nltk_local"})
        
    if entendimento['intencao'] == 'listar_todos':
        return jsonify({"response": listar_todos_campeoes(), "modo": "nltk_local"})
        
    if entendimento['intencao'] == 'buscar_artilheiro' and entendimento['ano']:
        resp = buscar_artilheiro(entendimento['ano'])
        if resp: return jsonify({"response": resp, "modo": "nltk_local"})
            
    if entendimento['intencao'] == 'buscar_ano' and entendimento['ano']:
        resp = buscar_dados_copa(entendimento['ano'])
        if resp: return jsonify({"response": resp, "modo": "nltk_local"})
    
    # 2. SE O NLTK NÃO ENCONTRAR, CHAMA O RAG DO SEU COLEGA (Busca Semântica Avançada)
    if RAG_DISPONIVEL:
        resultado_rag = gerar_resposta_rag(user_input)
        if resultado_rag["modo"] == "rag":
            return jsonify({"response": resultado_rag["resposta"], "modo": "rag"})

    # 3. SE NENHUM DOS DOIS FUNCIONAR, TENTA SAUDAÇÃO BÁSICA
    resposta_nltk = chatbot_basico.respond(user_input.lower())
    if resposta_nltk:
        return jsonify({"response": resposta_nltk, "modo": "nltk_basico"})

    # 4. FALLBACK GROQ
    from hf_engine import gerar_resposta_hf
    print("CHEGOU NO GROQ")
    print(f"CHAVE: {os.getenv('GROQ_API_KEY')}")
    resposta_hf = gerar_resposta_hf(user_input)
    return jsonify({"response": resposta_hf, "modo": "groq"})

if __name__ == "__main__":
    app.run(debug=True)