import React, { useState, useEffect, useRef } from 'react';
import { 
  Heart, 
  Send, 
  RotateCcw, 
  AlertTriangle, 
  ShieldAlert, 
  Activity, 
  Stethoscope, 
  User, 
  Sparkles,
  Info
} from 'lucide-react';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome-msg',
      sender: 'assistant',
      text: `Olá! Sou o **Assistente Cardiológico CardioIA** 🫀.\n\nEstou preparado para auxiliar na triagem inicial de sintomas, interpretar dados de pressão arterial e tirar dúvidas sobre saúde do coração com base em diretrizes clínicas.\n\n*Como posso ajudar você hoje?*`,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [riskLevel, setRiskLevel] = useState('BAIXO_RISCO');
  const [sessionId, setSessionId] = useState(() => sessionStorage.getItem('cardioia_react_session') || null);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Inicializa sessão
  useEffect(() => {
    async function initSession() {
      if (!sessionId) {
        try {
          const res = await fetch(`${API_BASE_URL}/api/session`, { method: 'POST' });
          if (res.ok) {
            const data = await res.json();
            setSessionId(data.session_id);
            sessionStorage.setItem('cardioia_react_session', data.session_id);
          }
        } catch (err) {
          console.warn('Backend offline ou erro ao iniciar sessão:', err);
        }
      }
    }
    initSession();
  }, [sessionId]);

  // Scroll automático
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const quickChips = [
    { label: '🚨 Dor no Peito / Urgência', text: 'Estou sentindo forte dor no peito e suor frio' },
    { label: '🩺 Relatar Sintomas', text: 'Gostaria de relatar sintomas que estou sentindo' },
    { label: '📊 Informar Pressão', text: 'Minha pressão arterial deu 14 por 9 e batimento 85' },
    { label: '💡 Dicas de Prevenção', text: 'Como posso prevenir doenças do coração?' },
    { label: 'ℹ️ Sobre o CardioIA', text: 'O que é o projeto CardioIA?' },
  ];

  const handleSend = async (textToSend) => {
    const text = (textToSend || input).trim();
    if (!text || loading) return;

    const userMessage = {
      id: String(Date.now()),
      sender: 'user',
      text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: sessionId
        })
      });

      if (!res.ok) {
        throw new Error(`Erro status: ${res.status}`);
      }

      const data = await res.json();
      if (data.session_id && data.session_id !== sessionId) {
        setSessionId(data.session_id);
        sessionStorage.setItem('cardioia_react_session', data.session_id);
      }

      if (data.risk_level) {
        setRiskLevel(data.risk_level);
      }

      const botMessage = {
        id: String(Date.now() + 1),
        sender: 'assistant',
        text: data.response || 'Não foi possível obter uma resposta.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('Erro ao enviar mensagem:', err);
      const errorMessage = {
        id: String(Date.now() + 1),
        sender: 'assistant',
        text: '⚠️ Ocorreu uma instabilidade na conexão com o servidor. Por favor, tente novamente.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  const handleResetChat = async () => {
    if (window.confirm('Deseja reiniciar o atendimento conversacional?')) {
      sessionStorage.removeItem('cardioia_react_session');
      setSessionId(null);
      setRiskLevel('BAIXO_RISCO');
      setMessages([
        {
          id: 'reset-welcome',
          sender: 'assistant',
          text: 'Atendimento reiniciado! Como posso ajudar você com sua saúde cardiovascular hoje? 🫀',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
      try {
        const res = await fetch(`${API_BASE_URL}/api/session`, { method: 'POST' });
        if (res.ok) {
          const data = await res.json();
          setSessionId(data.session_id);
          sessionStorage.setItem('cardioia_react_session', data.session_id);
        }
      } catch (err) {
        console.warn('Erro ao reiniciar sessão:', err);
      }
    }
  };

  const formatText = (content) => {
    if (!content) return null;
    const lines = content.split('\n');
    return lines.map((line, idx) => {
      // Formatação de negrito **
      const parts = line.split(/(\*\*.*?\*\*)/g).map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={i}>{part.slice(2, -2)}</strong>;
        }
        // Formatação de itálico *
        const subParts = part.split(/(\*.*?\*)/g).map((sub, j) => {
          if (sub.startsWith('*') && sub.endsWith('*')) {
            return <em key={j}>{sub.slice(1, -1)}</em>;
          }
          return sub;
        });
        return subParts;
      });

      // Item de lista
      if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
        return (
          <li key={idx} className="chat-list-item">
            {parts}
          </li>
        );
      }

      return (
        <p key={idx} className="chat-paragraph">
          {parts}
        </p>
      );
    });
  };

  const getRiskBadgeClass = () => {
    switch (riskLevel) {
      case 'EMERGENCIA': return 'badge-emergencia';
      case 'ALTO_RISCO': return 'badge-alto';
      case 'MODERADO': return 'badge-moderado';
      default: return 'badge-baixo';
    }
  };

  const getRiskBadgeLabel = () => {
    switch (riskLevel) {
      case 'EMERGENCIA': return '🚨 Emergência';
      case 'ALTO_RISCO': return '⚠️ Alto Risco';
      case 'MODERADO': return 'Risco: Moderado';
      default: return 'Risco: Baixo';
    }
  };

  return (
    <div className="react-app-container">
      {/* Header */}
      <header className="react-header">
        <div className="react-brand">
          <div className="avatar-wrapper">
            <img src="/cardioia-avatar.svg" alt="CardioIA" className="brand-avatar" />
            <span className="status-indicator online" title="Assistente Online"></span>
          </div>
          <div className="brand-info">
            <h1 className="brand-title">CardioIA Assistant</h1>
            <p className="brand-subtitle">Triagem & Orientação Cardiológica (React)</p>
          </div>
        </div>
        <div className="header-actions">
          <span className={`risk-badge ${getRiskBadgeClass()}`}>
            {getRiskBadgeLabel()}
          </span>
          <button onClick={handleResetChat} className="btn-icon" title="Reiniciar Atendimento">
            <RotateCcw size={16} />
            <span>Limpar</span>
          </button>
        </div>
      </header>

      {/* Main Chat Area */}
      <main className="chat-viewport">
        <div className="messages-container">
          {messages.map((msg) => (
            <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
              <div className="message-avatar">
                {msg.sender === 'user' ? (
                  <div className="user-avatar-icon">
                    <User size={18} />
                  </div>
                ) : (
                  <img src="/cardioia-avatar.svg" alt="Bot" />
                )}
              </div>
              <div className="message-bubble">
                <div className="message-header">
                  <span className="sender-name">{msg.sender === 'user' ? 'Você' : 'CardioIA'}</span>
                  <span className="message-time">{msg.time}</span>
                </div>
                <div className="message-text">
                  {formatText(msg.text)}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="typing-indicator">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
              <span>CardioIA está processando...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Action Chips */}
        <div className="quick-chips-container">
          {quickChips.map((chip, i) => (
            <button 
              key={i} 
              className="chip" 
              onClick={() => handleSend(chip.text)}
              disabled={loading}
            >
              {chip.label}
            </button>
          ))}
        </div>
      </main>

      {/* Footer Input */}
      <footer className="chat-footer">
        <form 
          className="input-form" 
          onSubmit={(e) => { e.preventDefault(); handleSend(); }}
        >
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Digite sua mensagem, sintoma ou dúvida sobre saúde..."
            rows={1}
            disabled={loading}
          />
          <button 
            type="submit" 
            className="btn-send" 
            disabled={loading || !input.trim()}
            title="Enviar Mensagem"
          >
            <Send size={18} />
          </button>
        </form>
        <div className="disclaimer-bar">
          <AlertTriangle size={14} />
          <span><strong>Aviso de Saúde:</strong> Protótipo acadêmico para triagem e orientação educacional. Em situações de emergência, ligue <strong>192 (SAMU)</strong>.</span>
        </div>
      </footer>
    </div>
  );
}
