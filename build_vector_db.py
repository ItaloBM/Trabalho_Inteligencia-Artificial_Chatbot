"""
build_vector_db.py
==================
Execute este script UMA VEZ para popular o banco vetorial (ChromaDB)
com os dados do copa.csv.

Uso:
    python build_vector_db.py

O banco será salvo na pasta ./chroma_db/ e reutilizado pelo rag_engine.py.
"""

import os
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

# Diretório base: sempre a pasta onde este script está
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Configurações ────────────────────────────────────────────────────────────
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "copa_mundo"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # Suporta Português
CSV_PATH = os.path.join(BASE_DIR, "copa.csv")


def documento_para_texto(row: pd.Series) -> str:
    """Converte uma linha do CSV em texto natural para embedding."""
    return (
        f"Na Copa do Mundo de {row['Ano']}, sediada em {row['Sede']}, "
        f"a seleção campeã foi {row['Campeao']}. "
        f"O vice-campeão foi {row['Vice']} e o terceiro lugar ficou com {row['Terceiro']}. "
        f"Participaram {row['Selecoes_Participantes']} seleções. "
        f"O artilheiro foi {row['Artilheiro']} com {row['Gols_Artilheiro']} gols."
    )


def build_database():
    print("📂 Carregando base de dados...")
    df = pd.read_csv(CSV_PATH)
    print(f"   → {len(df)} copas carregadas do {CSV_PATH}")

    print(f"\n🤖 Carregando modelo de embedding: {MODEL_NAME}")
    print("   (Pode demorar na primeira vez — baixando o modelo ~50MB)")
    model = SentenceTransformer(MODEL_NAME)

    print("\n📝 Convertendo registros para texto natural...")
    documentos = []
    ids = []
    metadados = []

    for _, row in df.iterrows():
        texto = documento_para_texto(row)
        documentos.append(texto)
        ids.append(f"copa_{row['Ano']}")
        metadados.append({
            "ano": int(row['Ano']),
            "sede": str(row['Sede']),
            "campeao": str(row['Campeao']),
            "vice": str(row['Vice']),
            "terceiro": str(row['Terceiro']),
            "artilheiro": str(row['Artilheiro']),
            "gols_artilheiro": int(row['Gols_Artilheiro']),
        })
        print(f"   ✓ Copa {row['Ano']} — {row['Campeao']}")

    print(f"\n🔢 Gerando embeddings para {len(documentos)} documentos...")
    embeddings = model.encode(documentos, show_progress_bar=True).tolist()

    print(f"\n💾 Salvando no ChromaDB em '{CHROMA_PATH}'...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Remove coleção existente para evitar duplicatas ao re-executar
    try:
        client.delete_collection(COLLECTION_NAME)
        print("   → Coleção anterior removida (re-indexando)")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # Similaridade por cosseno
    )

    collection.add(
        documents=documentos,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadados,
    )

    print(f"\n✅ Banco vetorial criado com sucesso!")
    print(f"   Coleção: '{COLLECTION_NAME}'")
    print(f"   Documentos indexados: {collection.count()}")
    print(f"   Local: {CHROMA_PATH}/\n")


if __name__ == "__main__":
    build_database()
