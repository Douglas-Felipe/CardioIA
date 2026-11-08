import React, { createContext, useContext, useEffect, useState } from 'react';
import { api, session } from './api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => (session.token ? session.user : null));

  useEffect(() => {
    const onLogout = () => setUser(null);
    window.addEventListener('cardioia:logout', onLogout);
    return () => window.removeEventListener('cardioia:logout', onLogout);
  }, []);

  const login = async (username, password) => {
    const data = await api('/api/auth/login', {
      method: 'POST',
      body: { username, password },
      auth: false,
    });
    session.save(data.access_token, data.user);
    setUser(data.user);
    return data.user;
  };

  const logout = () => {
    session.clear();
    sessionStorage.removeItem('cardioia_chat_session');
    setUser(null);
  };

  return <AuthContext.Provider value={{ user, login, logout }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
