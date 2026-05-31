import os, sys

# Escreve para arquivo para confirmar que o script roda
script_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_dir, "diag_output.txt")

with open(log_path, "w", encoding="utf-8") as f:
    f.write(f"Python: {sys.version}\n")
    f.write(f"Executavel: {sys.executable}\n")
    f.write(f"Diretorio do script: {script_dir}\n")

    try:
        import chromadb
        f.write(f"chromadb OK: {chromadb.__version__}\n")
    except Exception as e:
        f.write(f"ERRO chromadb: {e}\n")

    try:
        from sentence_transformers import SentenceTransformer
        f.write("sentence_transformers OK\n")
    except Exception as e:
        f.write(f"ERRO sentence_transformers: {e}\n")

    try:
        import pandas as pd
        df = pd.read_csv(os.path.join(script_dir, "copa.csv"))
        f.write(f"pandas OK: {len(df)} linhas no copa.csv\n")
    except Exception as e:
        f.write(f"ERRO pandas: {e}\n")

    try:
        client = chromadb.PersistentClient(path=os.path.join(script_dir, "chroma_db_diag"))
        col = client.create_collection("diag_test")
        col.add(documents=["teste"], ids=["id1"])
        f.write(f"ChromaDB PersistentClient OK\n")
        client.delete_collection("diag_test")
        import shutil
        shutil.rmtree(os.path.join(script_dir, "chroma_db_diag"), ignore_errors=True)
    except Exception as e:
        f.write(f"ERRO ChromaDB: {e}\n")

    f.write("FIM DO DIAGNOSTICO\n")

print(f"Diagnostico salvo em: {log_path}")
