import subprocess, sys, os

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pip_info.txt")

result = subprocess.run(
    [sys.executable, "-m", "pip", "show", "chromadb", "sentence-transformers"],
    capture_output=True, text=True
)

with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"Python: {sys.version}\n")
    f.write(f"Exec: {sys.executable}\n\n")
    f.write("=== STDOUT ===\n")
    f.write(result.stdout or "(vazio)\n")
    f.write("=== STDERR ===\n")
    f.write(result.stderr or "(vazio)\n")
    f.write(f"Exit code: {result.returncode}\n")
