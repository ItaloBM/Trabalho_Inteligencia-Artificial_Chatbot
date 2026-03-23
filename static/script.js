// Função para adicionar a mensagem no ecrã de chat
function addMessage(text, className) {
    const chatBox = document.getElementById("chat-box");
    const messageDiv = document.createElement("div");
    messageDiv.className = "message " + className;
    messageDiv.innerText = text;
    chatBox.appendChild(messageDiv);
    // Faz o scroll automático para o fundo
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Deteta se o utilizador pressionou a tecla "Enter"
function handleKeyPress(event) {
    if (event.key === "Enter") { 
        sendMessage(); 
    }
}

// Envia a mensagem para o servidor Flask
function sendMessage() {
    const inputField = document.getElementById("user-input");
    const message = inputField.value.trim();
    
    // Se estiver vazio, não faz nada
    if (message === "") return;

    // Adiciona a mensagem do utilizador no ecrã
    addMessage(message, "user-message");
    
    // Limpa a caixa de texto
    inputField.value = "";

    // Faz o pedido ao Backend (app.py) via POST
    fetch("/get_response", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        // Adiciona a resposta do Bot (CopaBot) no ecrã
        addMessage(data.response, "bot-message");
    })
    .catch(error => {
        console.error("Erro:", error);
        addMessage("O árbitro interrompeu o jogo. Erro de ligação com o servidor.", "bot-message");
    });
}