"""
rag_engine.py
=============
Motor RAG (Retrieval-Augmented Generation) do CopaBot.

Expõe duas funções principais:
    - buscar_contexto(query, n_results) → lista de documentos relevantes
    - gerar_resposta_rag(query)         → resposta completa ao usuário
"""

import os
import re
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq

# Diretório base: sempre a pasta onde este módulo está
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Configurações ────────────────────────────────────────────────────────────
CHROMA_PATH = os.path.join(_BASE_DIR, "chroma_db")
COLLECTION_NAME = "copa_mundo"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
SIMILARITY_THRESHOLD = 0.35  # Distância mínima de coseno (abaixo = não relevante)

# ─── Singleton: carrega modelo e banco apenas uma vez ────────────────────────
_model = None
_collection = None
_groq_client = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection

def _get_groq_client():
    """Configura e retorna o cliente da Groq, se a chave estiver disponível."""
    global _groq_client
    if _groq_client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key or api_key == "sua_chave_aqui":
            return None
        _groq_client = Groq(api_key=api_key)
    return _groq_client


# busca vetorial
def buscar_contexto(query: str, n_results: int = 3) -> list[dict]:
    """
    Busca os documentos mais similares à query no ChromaDB.

    Retorna uma lista de dicts com:
        - "texto": o documento em linguagem natural
        - "metadados": dict com campos do CSV
        - "distancia": float (0 = idêntico, 1 = completamente diferente)
    """
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([query]).tolist()

    resultados = collection.query(
        query_embeddings=query_embedding,
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    contexto = []
    for doc, meta, dist in zip(
        resultados["documents"][0],
        resultados["metadatas"][0],
        resultados["distances"][0],
    ):
        contexto.append({"texto": doc, "metadados": meta, "distancia": dist})

    return contexto

def _formatar_copa(meta: dict) -> str:
    """Formata os metadados de uma Copa para servir de contexto para o LLM."""
    ano = meta["ano"]
    sede = meta["sede"]
    campeao = meta["campeao"]
    vice = meta["vice"]
    terceiro = meta["terceiro"]
    artilheiro = meta["artilheiro"]
    gols = meta["gols_artilheiro"]

    return (
        f"Ano da Copa: {ano} | Sede: {sede} | Campeão: {campeao} | "
        f"Vice: {vice} | Terceiro: {terceiro} | "
        f"Artilheiro: {artilheiro} ({gols} gols)"
    )


def gerar_resposta_rag(query: str, n_results: int = 3) -> dict:
    """
    Executa o pipeline RAG completo usando IA Generativa (Groq):
        1. Busca vetorial no ChromaDB
        2. Envia contexto + pergunta para a Groq
    """
    contexto_bruto = buscar_contexto(query, n_results)

    # Filtra apenas resultados relevantes
    relevantes = [c for c in contexto_bruto if c["distancia"] <= SIMILARITY_THRESHOLD]

    client = _get_groq_client()

    if not client:
        # Fallback de segurança caso o usuário não tenha configurado o .env ainda
        return {
            "resposta": "⚠️ O modelo de IA Generativa (Groq) não está configurado. Crie o arquivo `.env` com sua `GROQ_API_KEY` para que eu consiga gerar respostas completas!",
            "fontes": [],
            "modo": "erro_api"
        }

    # Se não encontrou dados no banco (pergunta fora do escopo do CSV)
    if not relevantes:
        sistema_prompt = (
            "Você é o CopaBot, um assistente especializado em Copas do Mundo de Futebol. "
            "Você pode responder sobre dois temas: "
            "(1) Copas do Mundo — campeões, artilheiros, sedes, resultados, seleções, curiosidades e histórias; "
            "(2) Regras básicas do futebol — como funcionam cartões, impedimento, pênalti, tempo de jogo, VAR, etc. "
            "NÃO responda sobre outras competições (ligas nacionais, Champions League, clubes, etc.) "
            "nem sobre assuntos que não tenham relação com futebol ou Copas do Mundo. "
            "Se a pergunta estiver fora desses temas, recuse educadamente e sugira que o usuário pergunte "
            "sobre Copas do Mundo ou regras do futebol."
        )
        
        try:
            resposta_llm = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": sistema_prompt},
                    {"role": "user", "content": query}
                ],
                model="llama-3.3-70b-versatile",
            )
            texto_final = resposta_llm.choices[0].message.content
        except Exception as e:
            texto_final = f"Ops! Tive um problema ao conectar com o cérebro da IA (Groq): {str(e)}"
            
        return {
            "resposta": texto_final,
            "fontes": [],
            "modo": "llm_fallback",
        }

    # Se encontrou dados (RAG Verdadeiro)
    contexto_texto = "\n".join([_formatar_copa(r["metadados"]) for r in relevantes])
    
    sistema_rag = (
        "Você é o CopaBot, um assistente especializado em Copas do Mundo de Futebol. "
        "Use APENAS os dados fornecidos no CONTEXTO abaixo para responder à pergunta do usuário sobre Copas do Mundo. "
        "Você também pode responder perguntas sobre regras básicas do futebol (cartões, impedimento, pênalti, VAR, etc.) "
        "usando seu próprio conhecimento, mesmo que não estejam no contexto. "
        "NÃO responda sobre outras competições (ligas, clubes, etc.) nem sobre assuntos sem relação com futebol. "
        "Se a resposta de Copa não estiver no contexto, diga que não tem essa informação.\n\n"
        "CONTEXTO OBTIDO DO BANCO DE DADOS:\n"
        f"{contexto_texto}"
    )
    
    try:
        resposta_llm = client.chat.completions.create(
            messages=[
                {"role": "system", "content": sistema_rag},
                {"role": "user", "content": query}
            ],
            model="llama-3.3-70b-versatile",
        )
        texto_final = resposta_llm.choices[0].message.content
    except Exception as e:
        texto_final = f"Ops! Tive um problema ao conectar com o cérebro da IA (Groq): {str(e)}"

    return {
        "resposta": texto_final,
        "fontes": [c["texto"] for c in relevantes],
        "modo": "rag",
    }


# ─── Diagnóstico rápido ───────────────────────────────────────────────────────
if __name__ == "__main__":
    queries_teste = [
        "quem ganhou a copa de 2002?",
        "qual foi a sede da copa de 1970?",
        "quem foi o artilheiro da copa de 2014?",
        "quem ficou em segundo lugar em 2018?",
        "copa mais emocionante da história",  # Deve retornar sem_resultado
    ]

    print("=" * 60)
    print("  TESTE DO RAG ENGINE — CopaBot")
    print("=" * 60)

    for q in queries_teste:
        print(f"\n🔍 Pergunta: {q}")
        resultado = gerar_resposta_rag(q)
        print(f"📍 Modo: {resultado['modo']}")
        print(f"💬 Resposta:\n{resultado['resposta']}")
        print("-" * 60)
