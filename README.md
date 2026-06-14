# ⚽ CopaBot - Agente Conversacional Híbrido (NLTK + RAG + LLM)

Trabalho final desenvolvido para a disciplina de Inteligência Artificial e Machine Learning (Centro Universitário UniAcademia).

**Autores:** Italo Butinholi Mendes, Gustavo Correa, Vitorio Ribeiro, Lucas Nascif e Mateus Cacilhas.  
**Data:** 15/06/2026

## 📌 Sobre o Projeto
O CopaBot é um agente conversacional (chatbot) inteligente especializado em responder perguntas sobre as Copas do Mundo. O projeto evoluiu de uma simples busca em base de dados para uma **Arquitetura Híbrida Avançada**, combinando regras determinísticas com Inteligência Artificial Generativa.

O sistema atua em duas camadas para garantir respostas rápidas, precisas e sem "alucinações":
1. **Processamento Rápido (NLTK + Pandas):** Identifica intenções diretas (ex: "Quem ganhou em 2002?") usando tokenização e stopwords, buscando a resposta instantaneamente em uma base estruturada local (`copa.csv`).
2. **Motor RAG e LLM (Fallback):** Para perguntas complexas ou abertas (ex: "Qual foi a copa mais emocionante?"), o sistema utiliza Busca Vetorial para encontrar o contexto histórico e envia para um Grande Modelo de Linguagem (LLM) da Hugging Face formular uma resposta fluente e natural.

## 🛠️ Decisões de Desenvolvimento e Tecnologias

* **Backend Web (Python + Flask):** Framework leve responsável por hospedar a API do chatbot e servir as páginas de forma ágil.
* **Processamento de Linguagem Natural (NLTK):** Substituiu as expressões regulares (*Regex*). Utiliza `word_tokenize` e remoção de `stopwords` para extrair entidades (anos e países) e compreender a semântica da frase do usuário.
* **Motor RAG (ChromaDB + Sentence Transformers):** Implementação de um banco de dados vetorial local (`chroma_db`) que converte os dados históricos em *embeddings* textuais, permitindo busca por similaridade (busca semântica).
* **Inteligência Artificial (Hugging Face Hub):** Integração via API com modelos LLM (ex: *Zephyr-7b*) para atuar como fallback criativo e contextual, utilizando a técnica de *Retrieval-Augmented Generation* (RAG) para ancorar as respostas aos fatos reais.
* **Frontend (HTML, CSS, Vanilla JS):** Interface responsiva que se comunica de forma assíncrona com o backend, apresentando indicadores visuais de carregamento (*loading*) enquanto a IA processa respostas complexas.

## 🚀 Como Executar Localmente

### Pré-requisitos e Configuração da API
Antes de rodar, é necessário configurar a chave da API do LLM:
1. Crie uma conta gratuita em [Hugging Face](https://huggingface.co/).
2. Gere um Access Token (modo *Read*).
3. Abra o arquivo `rag_engine.py` e cole o seu token na variável `HF_TOKEN`.

### Instalação e Execução (Passo a Passo)
1. Clone este repositório para a sua máquina.
2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate