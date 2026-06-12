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
    {
        "id": 4,
        "descricao": "Títulos de outra seleção (Argentina)",
        "mensagem": "títulos argentina",
        "palavras_chave": ["argentina"],
    },
    {
        "id": 5,
        "descricao": "Ranking completo de campeões",
        "mensagem": "Quero ver o ranking de todos os campeões",
        "palavras_chave": ["ranking", "campe"],
    },
    {
        "id": 6,
        "descricao": "Artilheiro de um ano específico (2014)",
        "mensagem": "artilheiro 2014",
        "palavras_chave": ["james", "rodríguez", "rodriguez"],
    },
    {
        "id": 7,
        "descricao": "Artilheiro sem informar o ano (lista geral)",
        "mensagem": "quem foi o artilheiro da copa?",
        "palavras_chave": ["artilheiro", "artilheiros"],
    },
    {
        "id": 8,
        "descricao": "Ano antes da primeira Copa (1920)",
        "mensagem": "copa de 1920",
        "palavras_chave": ["1930"],
    },
    {
        "id": 9,
        "descricao": "Ano sem Copa por causa da Guerra (1942)",
        "mensagem": "o que aconteceu na copa de 1942?",
        "palavras_chave": ["guerra"],
    },
    {
        "id": 10,
        "descricao": "Ano muito no futuro (2030)",
        "mensagem": "quem vai ganhar a copa de 2030?",
        "palavras_chave": ["viajante", "2026"],
    },
    {
        "id": 11,
        "descricao": "Ano futuro ainda não realizado (2026)",
        "mensagem": "quem ganhou a copa de 2026?",
        "palavras_chave": ["ainda", "vai acontecer"],
    },
    {
        "id": 12,
        "descricao": "Ano fora do ciclo de 4 em 4 anos (2015)",
        "mensagem": "copa de 2015",
        "palavras_chave": ["var", "4 em 4", "não teve"],
    },
    {
        "id": 13,
        "descricao": "Agradecimento",
        "mensagem": "Obrigado!",
        "palavras_chave": ["junto", "pergunta"],
    },
    {
        "id": 14,
        "descricao": "Despedida",
        "mensagem": "Tchau",
        "palavras_chave": ["copa", "até"],
    },
    {
        "id": 15,
        "descricao": "Pergunta fora do escopo",
        "mensagem": "Qual a capital da França?",
        "palavras_chave": ["paris", "não captei", "campeão", "artilheiro"],
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