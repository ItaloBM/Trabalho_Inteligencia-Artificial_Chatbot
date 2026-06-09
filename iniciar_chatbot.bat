@echo off
chcp 65001 >nul
echo ========================================================
echo        INICIANDO O COPABOT COM INTELIGENCIA (RAG)
echo ========================================================
echo.

echo [1/3] Verificando e instalando dependencias (pode demorar um pouco)...
python -m pip install -r requirements.txt
echo.

echo [2/4] Verificando arquivo de configuracao (.env)...
if not exist .env (
    echo Criando arquivo .env a partir do .env.example...
    copy .env.example .env >nul
    echo ========================================================
    echo AVISO IMPORTANTE:
    echo Um arquivo .env foi criado na pasta do seu projeto.
    echo Para que a Inteligencia Artificial Generativa funcione,
    echo abra o arquivo .env e coloque sua GROQ_API_KEY nele!
    echo ========================================================
    echo.
    pause
) else (
    echo Arquivo .env encontrado!
)
echo.

echo [3/4] Construindo o Banco de Dados Vetorial...
echo (Isso pode demorar na primeira vez para baixar o modelo de embeddings)
python build_vector_db.py
echo.

echo [4/4] Iniciando o servidor do Chatbot...
echo.
echo Abra o seu navegador e acesse: http://127.0.0.1:5000
echo Para fechar o servidor, feche esta janela ou pressione Ctrl+C.
echo.
python app.py

pause
