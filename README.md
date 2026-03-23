# Trabalho_Inteligencia-Artificial_Chatbot

# ⚽ CopaBot - O Especialista em Copas do Mundo

Trabalho desenvolvido para a disciplina de Inteligência Artificial e Machine Learning.

## 📌 Sobre o Projeto
O CopaBot é um chatbot temático focado em responder perguntas sobre os campeões das Copas do Mundo. Ele foi projetado para iniciar de forma "simples" utilizando uma base de dados estruturada em CSV, com a intenção de ser aprimorado ao longo do semestre com integração de APIs e modelos de Machine Learning.

## 🛠️ Decisões de Desenvolvimento e Tecnologias
Para cumprir os requisitos de uma interface web interativa e processamento de linguagem natural, a equipe optou pela seguinte arquitetura modular:

* **Backend (Python + Flask):** Escolhemos o Flask por ser um framework web leve e ágil, ideal para conectar a lógica do chatbot com a interface visual sem overhead de configurações complexas.
* **Processamento de Linguagem Natural (NLTK):** Utilizado para mapear intenções básicas e saudações através de expressões regulares, preparando o terreno para futuras implementações de tokenização avançada.
* **Manipulação de Dados (Pandas):** A biblioteca Pandas foi escolhida para ler e filtrar a base de conhecimento `copa.csv` de forma rápida e eficiente.
* **Frontend (HTML, CSS, JS):** Desenvolvemos uma interface web responsiva e separada em arquivos estáticos (padrão de projeto). O JavaScript utiliza a API `fetch` para realizar requisições assíncronas (POST) ao servidor Flask, permitindo conversas fluidas sem recarregar a página.

## 🚀 Como Executar Localmente
1. Clone este repositório.
2. Crie um ambiente virtual: `python -m venv venv`
3. Ative o ambiente virtual e instale as dependências: `pip install flask nltk pandas`
4. Execute o servidor: `python app.py`
5. Acesse `http://127.0.0.1:5000` no seu navegador.