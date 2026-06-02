import sys
print("Python:", sys.version)
print("Caminho Python:", sys.executable)

try:
    import chromadb
    print("chromadb OK - versao:", chromadb.__version__)
except Exception as e:
    print("ERRO chromadb:", e)

try:
    from sentence_transformers import SentenceTransformer
    print("sentence_transformers OK")
except Exception as e:
    print("ERRO sentence_transformers:", e)

try:
    import chromadb
    client = chromadb.PersistentClient(path="./chroma_db_test")
    col = client.create_collection("teste")
    col.add(documents=["teste doc"], ids=["id1"])
    print("ChromaDB PersistentClient OK - count:", col.count())
    client.delete_collection("teste")
    import shutil
    shutil.rmtree("./chroma_db_test", ignore_errors=True)
except Exception as e:
    print("ERRO ChromaDB persistente:", e)

print("--- Fim do teste ---")
