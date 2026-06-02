from flask import Flask, render_template, request, jsonify
import pandas as pd
import re
# pyrefly: ignore [missing-import]
from nltk.chat.util import Chat, reflections
from collections import Counter
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# ─── RAG Engine ───────────────────────────────────────────────────────────────
# Importa o motor RAG. Se o banco vetorial ainda não foi criado, o sistema
# funciona normalmente apenas com regex (degradação graciosa).
try:
    from rag_engine import gerar_resposta_rag
    RAG_DISPONIVEL = True
except Exception as e:
    print(f"[AVISO] RAG não disponível: {e}")
    print("[AVISO] Execute 'python build_vector_db.py' para ativar o modo RAG.")
    RAG_DISPONIVEL = False

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
            # Lógica inteligente para anos sem Copa
            if ano < 1930:
                return f"Putz, em {ano} ainda não existia Copa do Mundo! A primeira foi só em 1930. Qual outro ano quer saber?"
            elif ano > 2022 and ano <= 2026:
                return f"A Copa de {ano} ainda vai acontecer! Mas tenho dados até 2022. Qual Copa passada você quer consultar?"
            elif ano > 2026:
                return f"Calma lá, viajante do tempo! Ainda não chegamos em {ano}. Minha base vai até 2022."
            elif ano == 1942 or ano == 1946:
                return f"Triste lembrança... Não teve Copa do Mundo em {ano} por causa da Segunda Guerra Mundial. Tente outro ano!"
            elif ano % 4 != 2: # As Copas acontecem em anos que deixam resto 2 quando divididos por 4 (ex: 2014, 2018, 2022)
                return f"VAR em ação: Não teve Copa do Mundo no ano de {ano}! As Copas acontecem de 4 em 4 anos. Tente um ano válido como 2018 ou 2022."
            else:
                return f"O VAR me avisou aqui que não tenho os dados sobre a Copa de {ano} no meu banco. Tente anos entre 1930 e 2022!"
    except ValueError:
        return "Formato de ano inválido. Digite algo como 2002. Qual ano você quer tentar?"

# Rotas Web
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.json.get("message").lower()
    
    # ─── Tenta usar a IA Generativa (Gemini) PRIMEIRO ────────────────────────
    if RAG_DISPONIVEL:
        resultado_rag = gerar_resposta_rag(user_input)
        # Se não deu erro de API (ou seja, a chave do Gemini foi configurada)
        if resultado_rag["modo"] != "erro_api":
            return jsonify({"response": resultado_rag["resposta"], "modo": resultado_rag["modo"]})
        # Se deu erro_api, o código continua e cai no Fallback antigo (Regex + NLTK)

    # ─── Fallback: Regex e NLTK (Usado apenas se não tiver API Key configurada) ───
    
    # Verifica se é pergunta sobre títulos de uma seleção
    if re.search(r'(titulo|titulos|quantos|quantas|copa).*?(brasil|argentina|alemanha|franca|italia|espanha|uruguai|inglaterra)', user_input):
        match = re.search(r'(brasil|argentina|alemanha|franca|italia|espanha|uruguai|inglaterra)', user_input)
        if match:
            resposta = buscar_titulos_selecao(match.group(1))
            return jsonify({"response": resposta, "modo": "regex"})
    
    # Verifica se quer listar todos os campeões
    if re.search(r'(todos|ranking|lista|campeoes|campeões|total)', user_input) and re.search(r'(titulo|titulos|campe)', user_input):
        resposta = listar_todos_campeoes()
        return jsonify({"response": resposta, "modo": "regex"})
    
    # Verifica se é pergunta sobre artilheiro
    if re.search(r'artilheiro|goleador|artilharia', user_input):
        ano_encontrado = re.search(r'\b(19|20)\d{2}\b', user_input)
        if ano_encontrado:
            resposta = buscar_artilheiro(ano_encontrado.group())
        else:
            resposta = "De qual ano você quer saber o artilheiro? Digite algo como 'artilheiro 2014'."
        return jsonify({"response": resposta, "modo": "regex"})
    
    # Busca por ano específico
    ano_encontrado = re.search(r'\b(19|20)\d{2}\b', user_input)
    if ano_encontrado:
        resposta = buscar_dados_copa(ano_encontrado.group())
        return jsonify({"response": resposta, "modo": "regex"})

    # ─── Fallback NLTK ───────────────────────────────────────────────────────
    resposta = chatbot_basico.respond(user_input)
    if not resposta:
        resposta = (
            "Desculpe, não captei a jogada. Pergunte sobre:\n"
            "• Campeão de um ano (ex: '2014')\n"
            "• Títulos de uma seleção (ex: 'títulos Brasil')\n"
            "• Artilheiro (ex: 'artilheiro 2018')\n"
            "• Ranking completo (ex: 'todos os campeões')\n"
            "• Perguntas livres (ex: 'quem ganhou a copa de 1970?')"
        )
    return jsonify({"response": resposta, "modo": "nltk"})


# ─── Rota de status do RAG (útil para debug) ─────────────────────────────────
@app.route("/rag_status")
def rag_status():
    return jsonify({
        "rag_disponivel": RAG_DISPONIVEL,
        "mensagem": (
            "RAG ativo e funcionando!" if RAG_DISPONIVEL
            else "Execute 'python build_vector_db.py' para ativar o RAG."
        )
    })

if __name__ == "__main__":
    app.run(debug=True)