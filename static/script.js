// ─── Utilitário: converte markdown simples em HTML ────────────────────────────
function markdownParaHtml(texto) {
    return texto
        // **negrito**
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // *itálico*
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // `código`
        .replace(/`(.*?)`/g, '<code>$1</code>')
        // Quebra de linha simples
        .replace(/\n/g, '<br>');
}

// ─── Badge de modo ────────────────────────────────────────────────────────────
function criarBadgeModo(modo) {
    if (!modo || modo === 'nltk' || modo === 'regex') return '';
    const badge = document.createElement('span');
    badge.className = 'rag-badge';
    badge.innerHTML = '🔍 RAG';
    badge.title = 'Resposta gerada por busca vetorial semântica (RAG)';
    return badge;
}

// ─── Adiciona mensagem no chat ─────────────────────────────────────────────────
function addMessage(text, className, modo = null) {
    const chatBox = document.getElementById("chat-box");
    const messageDiv = document.createElement("div");
    messageDiv.className = "message " + className;
    
    const messageContent = document.createElement("div");
    messageContent.className = "message-content";
    
    if (className === "bot-message") {
        const avatar = document.createElement("span");
        avatar.className = "bot-avatar";
        avatar.innerText = "⚽";
        messageContent.appendChild(avatar);
    }
    
    const textContent = document.createElement("div");
    textContent.className = "text-content";

    // Renderiza markdown simples se for mensagem do bot
    if (className === "bot-message") {
        textContent.innerHTML = markdownParaHtml(text);
    } else {
        textContent.innerText = text;
    }

    // Adiciona badge RAG se aplicável
    const badge = criarBadgeModo(modo);
    if (badge) {
        const badgeWrapper = document.createElement('div');
        badgeWrapper.className = 'badge-wrapper';
        badgeWrapper.appendChild(badge);
        textContent.prepend(badgeWrapper);
    }

    messageContent.appendChild(textContent);
    messageDiv.appendChild(messageContent);
    chatBox.appendChild(messageDiv);
    
    // Scroll automático suave
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: 'smooth'
    });
}

// ─── Indicador de digitação ───────────────────────────────────────────────────
function mostrarDigitando() {
    const chatBox = document.getElementById("chat-box");
    const typingDiv = document.createElement("div");
    typingDiv.className = "message bot-message typing-indicator-wrapper";
    typingDiv.id = "typing-indicator";
    typingDiv.innerHTML = `
        <div class="message-content">
            <span class="bot-avatar">⚽</span>
            <div class="text-content">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>`;
    chatBox.appendChild(typingDiv);
    chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
}

function removerDigitando() {
    const el = document.getElementById("typing-indicator");
    if (el) el.remove();
}

// ─── Tecla Enter ──────────────────────────────────────────────────────────────
function handleKeyPress(event) {
    if (event.key === "Enter") { 
        sendMessage(); 
    }
}

// ─── Envia mensagem ao Flask ──────────────────────────────────────────────────
function sendMessage() {
    const inputField = document.getElementById("user-input");
    const message = inputField.value.trim();
    
    if (message === "") return;

    addMessage(message, "user-message");
    inputField.value = "";
    inputField.disabled = true;

    mostrarDigitando();

    fetch("/get_response", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        removerDigitando();
        addMessage(data.response, "bot-message", data.modo);
        inputField.disabled = false;
        inputField.focus();
    })
    .catch(error => {
        removerDigitando();
        console.error("Erro:", error);
        addMessage("O árbitro interrompeu o jogo. Erro de ligação com o servidor.", "bot-message");
        inputField.disabled = false;
    });
}