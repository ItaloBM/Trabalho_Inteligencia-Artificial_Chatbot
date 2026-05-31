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


# ─── Busca vetorial ───────────────────────────────────────────────────────────
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


# ─── Geração de resposta por template ─────────────────────────────────────────
def _formatar_copa(meta: dict) -> str:
    """Formata os metadados de uma Copa em resposta amigável."""
    ano = meta["ano"]
    sede = meta["sede"]
    campeao = meta["campeao"]
    vice = meta["vice"]
    terceiro = meta["terceiro"]
    artilheiro = meta["artilheiro"]
    gols = meta["gols_artilheiro"]

    return (
        f"🏆 **Copa de {ano}** — Sede: {sede}\n"
        f"   🥇 Campeão: **{campeao}**\n"
        f"   🥈 Vice: {vice}\n"
        f"   🥉 Terceiro: {terceiro}\n"
        f"   ⚽ Artilheiro: {artilheiro} ({gols} gols)"
    )


def _detectar_intencao(query: str) -> str:
    """Detecta o tipo de pergunta para personalizar a resposta."""
    q = query.lower()
    if re.search(r"campe[ãa]o|venceu|ganhou|quem ganhou|titulo|título", q):
        return "campeao"
    if re.search(r"sede|sediad|pa[íi]s|cidade|onde foi|onde aconteceu", q):
        return "sede"
    if re.search(r"artilheiro|goleador|mais gols|quem fez mais", q):
        return "artilheiro"
    if re.search(r"vice|segundo lugar|perdeu a final|finalista", q):
        return "vice"
    if re.search(r"terceiro|3[oº°]|bronze", q):
        return "terceiro"
    return "geral"


def gerar_resposta_rag(query: str, n_results: int = 3) -> dict:
    """
    Executa o pipeline RAG completo:
        1. Embedding da query
        2. Busca vetorial no ChromaDB
        3. Filtragem por limiar de relevância
        4. Geração de resposta por template

    Retorna um dict com:
        - "resposta": str — texto da resposta ao usuário
        - "fontes": list[dict] — documentos recuperados
        - "modo": "rag" | "sem_resultado"
    """
    contexto = buscar_contexto(query, n_results)

    # Filtra apenas resultados relevantes
    relevantes = [c for c in contexto if c["distancia"] <= SIMILARITY_THRESHOLD]

    if not relevantes:
        return {
            "resposta": (
                "🤔 Não encontrei informações suficientes sobre isso na minha base "
                "de dados de Copas do Mundo. Tente perguntar sobre:\n"
                "• Um ano específico (ex: *'O que aconteceu na Copa de 1970?'*)\n"
                "• O campeão, vice ou artilheiro de uma Copa\n"
                "• A sede de uma Copa"
            ),
            "fontes": [],
            "modo": "sem_resultado",
        }

    intencao = _detectar_intencao(query)
    melhor = relevantes[0]["metadados"]
    ano = melhor["ano"]

    # Personaliza a resposta conforme intenção detectada
    if intencao == "campeao":
        intro = f"🏆 Na Copa de {ano}, o campeão foi **{melhor['campeao']}**!"
    elif intencao == "sede":
        intro = f"📍 A Copa de {ano} foi sediada em **{melhor['sede']}**!"
    elif intencao == "artilheiro":
        intro = (
            f"⚽ O artilheiro da Copa de {ano} foi **{melhor['artilheiro']}** "
            f"com **{melhor['gols_artilheiro']} gols**!"
        )
    elif intencao == "vice":
        intro = f"🥈 O vice-campeão da Copa de {ano} foi **{melhor['vice']}**!"
    elif intencao == "terceiro":
        intro = f"🥉 O terceiro lugar da Copa de {ano} foi **{melhor['terceiro']}**!"
    else:
        intro = f"📊 Encontrei informações sobre a Copa de {ano}:"

    # Monta detalhes completos da Copa principal encontrada
    detalhes = _formatar_copa(melhor)

    # Adiciona outras Copas relevantes (se houver mais de 1 resultado)
    extras = ""
    if len(relevantes) > 1:
        extras_list = [_formatar_copa(r["metadados"]) for r in relevantes[1:]]
        extras = "\n\n📌 **Outras Copas relacionadas:**\n" + "\n\n".join(extras_list)

    resposta = f"{intro}\n\n{detalhes}{extras}"

    return {
        "resposta": resposta,
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
