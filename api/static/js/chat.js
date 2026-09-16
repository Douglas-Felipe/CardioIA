document.addEventListener('DOMContentLoaded', () => {
    const messagesContainer = document.getElementById('messages-container');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const typingIndicator = document.getElementById('typing-indicator');
    const riskBadge = document.getElementById('risk-badge');
    const btnReset = document.getElementById('btn-reset-chat');
    const quickChips = document.getElementById('quick-chips');

    let sessionId = sessionStorage.getItem('cardioia_session_id') || null;

    // Inicializa a sessão com o backend
    async function initSession() {
        if (!sessionId) {
            try {
                const res = await fetch('/api/session', { method: 'POST' });
                if (res.ok) {
                    const data = await res.json();
                    sessionId = data.session_id;
                    sessionStorage.setItem('cardioia_session_id', sessionId);
                }
            } catch (err) {
                console.warn('Erro ao obter sessão do backend:', err);
            }
        }
    }
    initSession();

    // Formatação simples de Markdown em HTML
    function formatMarkdown(text) {
        if (!text) return '';
        let formatted = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Negrito **texto**
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Itálico *texto* ou _texto_
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        formatted = formatted.replace(/_(.*?)_/g, '<em>$1</em>');
        // Listas • ou -
        formatted = formatted.replace(/^[•\-]\s*(.*)$/gm, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        // Quebras de linha
        formatted = formatted.replace(/\n/g, '<br>');

        return formatted;
    }

    function getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function appendMessage(sender, text) {
        const isUser = sender === 'user';
        const wrapper = document.createElement('div');
        wrapper.className = `message-wrapper ${isUser ? 'user' : 'assistant'}`;

        const avatarImg = isUser 
            ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'
            : '<img src="/static/images/cardioia-avatar.svg" alt="Bot">';

        wrapper.innerHTML = `
            <div class="message-avatar">${avatarImg}</div>
            <div class="message-bubble">
                <div class="message-header">
                    <span class="sender-name">${isUser ? 'Você' : 'CardioIA'}</span>
                    <span class="message-time">${getCurrentTime()}</span>
                </div>
                <div class="message-text">${isUser ? text.replace(/\n/g, '<br>') : formatMarkdown(text)}</div>
            </div>
        `;

        messagesContainer.appendChild(wrapper);
        scrollToBottom();
    }

    function scrollToBottom() {
        const viewport = document.querySelector('.chat-viewport');
        viewport.scrollTop = viewport.scrollHeight;
    }

    function updateRiskBadge(riskLevel) {
        riskBadge.className = 'risk-badge';
        if (riskLevel === 'EMERGENCIA') {
            riskBadge.classList.add('badge-emergencia');
            riskBadge.textContent = '🚨 Emergência';
        } else if (riskLevel === 'ALTO_RISCO') {
            riskBadge.classList.add('badge-alto');
            riskBadge.textContent = '⚠️ Alto Risco';
        } else if (riskLevel === 'MODERADO') {
            riskBadge.classList.add('badge-moderado');
            riskBadge.textContent = 'Risco: Moderado';
        } else {
            riskBadge.classList.add('badge-baixo');
            riskBadge.textContent = 'Risco: Baixo';
        }
    }

    async function sendMessage(text) {
        const cleanText = text.trim();
        if (!cleanText) return;

        appendMessage('user', cleanText);
        userInput.value = '';
        userInput.style.height = 'auto';

        // Exibe indicador de digitação
        typingIndicator.classList.remove('hidden');
        scrollToBottom();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: cleanText,
                    session_id: sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`Erro na API: ${response.status}`);
            }

            const data = await response.json();
            if (data.session_id) {
                sessionId = data.session_id;
                sessionStorage.setItem('cardioia_session_id', sessionId);
            }

            typingIndicator.classList.add('hidden');
            appendMessage('assistant', data.response || 'Não consegui processar a resposta.');

            if (data.risk_level) {
                updateRiskBadge(data.risk_level);
            }
        } catch (error) {
            console.error('Falha ao comunicar com o servidor:', error);
            typingIndicator.classList.add('hidden');
            appendMessage('assistant', '⚠️ Ocorreu uma instabilidade na conexão com o assistente. Por favor, tente novamente.');
        }
    }

    // Eventos do formulário
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        sendMessage(userInput.value);
    });

    // Auto-resize do textarea e envio com Enter
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(userInput.value);
        }
    });

    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = `${Math.min(userInput.scrollHeight, 120)}px`;
    });

    // Chips de atalho
    if (quickChips) {
        quickChips.addEventListener('click', (e) => {
            const chip = e.target.closest('.chip');
            if (chip && chip.dataset.msg) {
                sendMessage(chip.dataset.msg);
            }
        });
    }

    // Reiniciar conversa
    btnReset.addEventListener('click', async () => {
        if (confirm('Deseja reiniciar a conversa e limpar o histórico?')) {
            sessionStorage.removeItem('cardioia_session_id');
            sessionId = null;
            await initSession();

            messagesContainer.innerHTML = `
                <div class="message-wrapper assistant">
                    <div class="message-avatar">
                        <img src="/static/images/cardioia-avatar.svg" alt="Bot">
                    </div>
                    <div class="message-bubble">
                        <div class="message-header">
                            <span class="sender-name">CardioIA</span>
                            <span class="message-time">Agora</span>
                        </div>
                        <div class="message-text">
                            Atendimento reiniciado! Como posso ajudar você com sua saúde cardiovascular hoje? 🫀
                        </div>
                    </div>
                </div>
            `;
            updateRiskBadge('BAIXO_RISCO');
        }
    });
});
