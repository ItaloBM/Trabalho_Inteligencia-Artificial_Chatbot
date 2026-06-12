import requests
import json

URL = "http://127.0.0.1:5000/get_response"

testes = [
    {
        "id": 1,
        "descricao": "Saudação",
        "mensagem": "Oi",
        "palavras_chave": ["copabot", "olá", "ola"],
    },
    {
        "id": 2,
        "descricao": "Campeão de um ano específico (2002)",
        "mensagem": "Quem ganhou a copa de 2002?",
        "palavras_chave": ["brasil"],
    },
    {
        "id": 3,
        "descricao": "Títulos de uma seleção (Brasil)",
        "mensagem": "Quantos títulos o Brasil tem?",
        "palavras_chave": ["título", "titulo"],
    },
    
]


def rodar_testes():
    linhas_relatorio = []
    linhas_relatorio.append("RELATÓRIO DE TESTES - COPABOT")
    linhas_relatorio.append("=" * 50)

    total = len(testes)
    passou = 0

    for teste in testes:
        print(f"\n[Teste {teste['id']}] {teste['descricao']}")
        print(f"  Enviando: \"{teste['mensagem']}\"")

        try:
            resp = requests.post(
                URL,
                json={"message": teste["mensagem"]},
                timeout=10,
            )
            resp.raise_for_status()
            dados = resp.json()
            resposta = dados.get("response", "")
            modo = dados.get("modo", "desconhecido")
        except Exception as e:
            resposta = f"ERRO ao conectar: {e}"
            modo = "erro"

        resposta_lower = resposta.lower()
        encontrou = any(p.lower() in resposta_lower for p in teste["palavras_chave"])

        status = "OK" if encontrou else "FALHOU"
        if encontrou:
            passou += 1

        print(f"  Modo: {modo}")
        print(f"  Resposta: {resposta}")
        print(f"  Resultado: {status}")

        # Monta bloco para o relatório em arquivo
        linhas_relatorio.append("")
        linhas_relatorio.append(f"Teste {teste['id']}: {teste['descricao']}")
        linhas_relatorio.append(f"Mensagem enviada: {teste['mensagem']}")
        linhas_relatorio.append(f"Modo retornado: {modo}")
        linhas_relatorio.append(f"Resposta do bot: {resposta}")
        linhas_relatorio.append(f"Palavras-chave esperadas: {', '.join(teste['palavras_chave'])}")
        linhas_relatorio.append(f"Resultado: {status}")

    linhas_relatorio.append("")
    linhas_relatorio.append("=" * 50)
    linhas_relatorio.append(f"RESUMO: {passou}/{total} testes passaram")

    with open("relatorio_testes.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_relatorio))

    print("\n" + "=" * 50)
    print(f"RESUMO: {passou}/{total} testes passaram")
    print("Relatório salvo em 'relatorio_testes.txt'")


if __name__ == "__main__":
    rodar_testes()