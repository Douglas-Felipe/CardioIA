import React, { createContext, useContext, useEffect, useState } from 'react';
import { api, storage } from './api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    storage.getSession().then((s) => {
      if (s.token && s.user) {
        setToken(s.token);
        setUser(s.user);
      }
      setReady(true);
    });
  }, []);

  const login = async (username, password) => {
    const data = await api('/api/auth/login', {
      method: 'POST',
      body: { username, password },
    });
    await storage.saveSession(data.access_token, data.user);
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  };

  const logout = async () => {
    await storage.clearSession();
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, ready, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
