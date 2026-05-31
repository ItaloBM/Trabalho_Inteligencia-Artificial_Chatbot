@echo off
chcp 65001 >nul
echo ========================================================
echo        INICIANDO O COPABOT COM INTELIGENCIA (RAG)
echo ========================================================
echo.

echo [1/3] Verificando e instalando dependencias (pode demorar um pouco)...
python -m pip install -r requirements.txt
echo.

echo [2/3] Construindo o Banco de Dados Vetorial...
echo (Isso pode demorar na primeira vez para baixar o modelo)
python build_vector_db.py
echo.

echo [3/3] Iniciando o servidor do Chatbot...
echo.
echo Abra o seu navegador e acesse: http://127.0.0.1:5000
echo Para fechar o servidor, feche esta janela ou pressione Ctrl+C.
echo.
python app.py

pause
