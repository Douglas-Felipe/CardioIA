import React from 'react';
import { Navigate, NavLink, Route, Routes } from 'react-router-dom';
import { Activity, Heart, LogOut, MessageSquare, Stethoscope, User } from 'lucide-react';
import { useAuth } from './auth';
import Chat from './pages/Chat';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import './App.css';

function ProtectedLayout({ children }) {
  const { user, logout } = useAuth();
  if (!user) return <Navigate to="/login" replace />;

  return (
    <div className="app-shell">
      <header className="top-nav">
        <div className="nav-brand">
          <div className="nav-logo">
            <Heart size={20} />
          </div>
          <div>
            <strong>CardioIA</strong>
            <span>Plataforma de Inteligência Cardíaca</span>
          </div>
        </div>

        <nav className="nav-links" aria-label="Navegação principal">
          <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <Activity size={16} />
            <span>Monitoramento</span>
          </NavLink>
          <NavLink to="/chat" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <MessageSquare size={16} />
            <span>Assistente IA</span>
          </NavLink>
        </nav>

        <div className="nav-user">
          <span className={`user-pill role-${user.role}`}>
            {user.role === 'medico' ? <Stethoscope size={14} /> : <User size={14} />}
            <span>{user.name}</span>
          </span>
          <button type="button" onClick={logout} className="btn-icon" title="Sair">
            <LogOut size={16} />
            <span>Sair</span>
          </button>
        </div>
      </header>

      <main className="shell-main">{children}</main>
    </div>
  );
}

export default function App() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/dashboard" replace /> : <Login />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedLayout>
            <Dashboard />
          </ProtectedLayout>
        }
      />
      <Route
        path="/chat"
        element={
          <ProtectedLayout>
            <Chat />
          </ProtectedLayout>
        }
      />
      <Route path="*" element={<Navigate to={user ? '/dashboard' : '/login'} replace />} />
    </Routes>
  );
}
