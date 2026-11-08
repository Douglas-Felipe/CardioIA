import React, { useEffect, useRef, useState } from 'react';
import { AlertTriangle, RotateCcw, Send, User } from 'lucide-react';
import { api } from '../api';
import '../App.css';

const SESSION_KEY = 'cardioia_chat_session';
const now = () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

const WELCOME = {
  id: 'welcome-msg',
  sender: 'assistant',
  text: `Olá! Sou o **Assistente Cardiológico CardioIA** 🫀.\n\nEstou preparado para auxiliar na triagem inicial de sintomas, interpretar dados de pressão arterial e tirar dúvidas sobre saúde do coração com base em diretrizes clínicas.\n\nPergunte *"como estou?"* para ver seus sinais vitais em tempo real.`,
  time: now(),
};

const quickChips = [
  { label: '📡 Como estou agora?', text: 'Como estou? Quero ver meus sinais vitais' },
  { label: '🚨 Dor no Peito / Urgência', text: 'Estou sentindo forte dor no peito e suor frio' },
  { label: '📊 Informar Pressão', text: 'Minha pressão arterial deu 14 por 9 e batimento 85' },
  { label: '💡 Dicas de Prevenção', text: 'Como posso prevenir doenças do coração?' },
  { label: 'ℹ️ Sobre o CardioIA', text: 'O que é o projeto CardioIA?' },
];

const RISK_BADGES = {
  EMERGENCIA: ['badge-emergencia', '🚨 Emergência'],
  ALTO_RISCO: ['badge-alto', '⚠️ Alto Risco'],
  MODERADO: ['badge-moderado', 'Risco: Moderado'],
  BAIXO_RISCO: ['badge-baixo', 'Risco: Baixo'],
};

function formatText(content) {
  if (!content) return null;
  return content.split('\n').map((line, idx) => {
    const parts = line.split(/(\*\*.*?\*\*)/g).map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) return <strong key={i}>{part.slice(2, -2)}</strong>;
      return part.split(/(\*.*?\*)/g).map((sub, j) =>
        sub.startsWith('*') && sub.endsWith('*') && sub.length > 2 ? <em key={j}>{sub.slice(1, -1)}</em> : sub
      );
    });
    if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
      return <li key={idx} className="chat-list-item">{parts}</li>;
    }
    return <p key={idx} className="chat-paragraph">{parts}</p>;
  });
}

export default function Chat() {
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [riskLevel, setRiskLevel] = useState('BAIXO_RISCO');
  const [engine, setEngine] = useState('');
  const [sessionId, setSessionId] = useState(() => sessionStorage.getItem(SESSION_KEY));
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const newSession = async () => {
    try {
      const data = await api('/api/chat/session', { method: 'POST' });
      setSessionId(data.session_id);
      setEngine(data.engine);
      if (data.session_id) sessionStorage.setItem(SESSION_KEY, data.session_id);
    } catch (err) {
      console.warn('Backend offline ou erro ao iniciar sessão:', err);
    }
  };

  useEffect(() => { if (!sessionId) newSession(); }, []); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, loading]);

  const handleSend = async (textToSend) => {
    const text = (textToSend || input).trim();
    if (!text || loading) return;

    setMessages(prev => [...prev, { id: String(Date.now()), sender: 'user', text, time: now() }]);
    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setLoading(true);

    try {
      const data = await api('/api/chat', { method: 'POST', body: { message: text, session_id: sessionId } });
      if (data.session_id && data.session_id !== sessionId) {
        setSessionId(data.session_id);
        sessionStorage.setItem(SESSION_KEY, data.session_id);
      }
      if (data.risk_level) setRiskLevel(data.risk_level);
      if (data.engine) setEngine(data.engine);
      setMessages(prev => [...prev, {
        id: String(Date.now() + 1), sender: 'assistant',
        text: data.response || 'Não foi possível obter uma resposta.', time: now(),
      }]);
    } catch (err) {
      console.error('Erro ao enviar mensagem:', err);
      setMessages(prev => [...prev, {
        id: String(Date.now() + 1), sender: 'assistant',
        text: '⚠️ Ocorreu uma instabilidade na conexão com o servidor. Por favor, tente novamente.', time: now(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (!window.confirm('Deseja reiniciar o atendimento conversacional?')) return;
    sessionStorage.removeItem(SESSION_KEY);
    setSessionId(null);
    setRiskLevel('BAIXO_RISCO');
    setMessages([{ id: 'reset', sender: 'assistant', text: 'Atendimento reiniciado! Como posso ajudar você com sua saúde cardiovascular hoje? 🫀', time: now() }]);
    await newSession();
  };

  const [badgeClass, badgeLabel] = RISK_BADGES[riskLevel] || RISK_BADGES.BAIXO_RISCO;

  return (
    <div className="react-app-container chat-page">
      <header className="react-header">
        <div className="react-brand">
          <div className="avatar-wrapper">
            <img src="/cardioia-avatar.svg" alt="CardioIA" className="brand-avatar" />
            <span className="status-indicator online" title="Assistente Online"></span>
          </div>
          <div className="brand-info">
            <h1 className="brand-title">Assistente CardioIA</h1>
            <p className="brand-subtitle">Fase 5 integrada · motor: {engine || '...'}</p>
          </div>
        </div>
        <div className="header-actions">
          <span className={`risk-badge ${badgeClass}`}>{badgeLabel}</span>
          <button onClick={handleReset} className="btn-icon" title="Reiniciar Atendimento">
            <RotateCcw size={16} /><span>Limpar</span>
          </button>
        </div>
      </header>

      <main className="chat-viewport">
        <div className="messages-container" aria-live="polite">
          {messages.map(msg => (
            <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
              <div className="message-avatar">
                {msg.sender === 'user'
                  ? <div className="user-avatar-icon"><User size={18} /></div>
                  : <img src="/cardioia-avatar.svg" alt="Bot" />}
              </div>
              <div className="message-bubble">
                <div className="message-header">
                  <span className="sender-name">{msg.sender === 'user' ? 'Você' : 'CardioIA'}</span>
                  <span className="message-time">{msg.time}</span>
                </div>
                <div className="message-text">{formatText(msg.text)}</div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="typing-indicator">
              <div className="dot"></div><div className="dot"></div><div className="dot"></div>
              <span>CardioIA está processando...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="quick-chips-container">
          {quickChips.map((chip, i) => (
            <button key={i} className="chip" onClick={() => handleSend(chip.text)} disabled={loading}>{chip.label}</button>
          ))}
        </div>
      </main>

      <footer className="chat-footer">
        <form className="input-form" onSubmit={(e) => { e.preventDefault(); handleSend(); }}>
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              e.target.style.height = 'auto';
              e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
            }}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
            placeholder="Digite sua mensagem, sintoma ou dúvida sobre saúde..."
            aria-label="Mensagem"
            rows={1}
            disabled={loading}
          />
          <button type="submit" className="btn-send" disabled={loading || !input.trim()} title="Enviar Mensagem">
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
