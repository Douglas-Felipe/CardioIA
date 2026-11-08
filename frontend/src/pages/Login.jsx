import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, Lock, Stethoscope, User, AlertCircle } from 'lucide-react';
import { useAuth } from '../auth';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('medico');
  const [password, setPassword] = useState('cardio123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err.message || 'Falha ao autenticar. Verifique se o backend está online.');
    } finally {
      setLoading(false);
    }
  };

  const quickFill = (role) => {
    setUsername(role);
    setPassword('cardio123');
    setError('');
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-brand">
          <div className="login-logo">
            <Heart size={28} />
          </div>
          <div>
            <h1>CardioIA</h1>
            <p>Plataforma de Inteligência Cardíaca Total · Fase 7</p>
          </div>
        </div>

        <div className="role-selector" role="group" aria-label="Perfis de demonstração">
          <button
            type="button"
            className={`role-btn ${username === 'medico' ? 'active' : ''}`}
            onClick={() => quickFill('medico')}
          >
            <Stethoscope size={18} />
            <div>
              <strong>Perfil Médico</strong>
              <span>Dashboard completo + ML + Protocolos</span>
            </div>
          </button>
          <button
            type="button"
            className={`role-btn ${username === 'paciente' ? 'active' : ''}`}
            onClick={() => quickFill('paciente')}
          >
            <User size={18} />
            <div>
              <strong>Perfil Paciente</strong>
              <span>Visão simplificada + Assistente</span>
            </div>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <label>
            <span>Usuário</span>
            <div className="input-with-icon">
              <User size={16} />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoComplete="username"
              />
            </div>
          </label>

          <label>
            <span>Senha</span>
            <div className="input-with-icon">
              <Lock size={16} />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
            </div>
          </label>

          {error && (
            <div className="login-error" role="alert">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Autenticando...' : 'Entrar na Plataforma'}
          </button>
        </form>

        <p className="login-hint">
          Credenciais demo: <code>medico / cardio123</code> ou <code>paciente / cardio123</code>
        </p>
      </div>
    </div>
  );
}
