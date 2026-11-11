import AsyncStorage from '@react-native-async-storage/async-storage';
import Constants from 'expo-constants';

export const API_BASE_URL = (
  process.env.EXPO_PUBLIC_API_URL ||
  Constants.expoConfig?.extra?.apiUrl ||
  'https://cardioia-backend-ewbv.onrender.com'
).replace(/\/$/, '');

const TOKEN_KEY = 'cardioia_token';
const USER_KEY = 'cardioia_user';

export const storage = {
  async getSession() {
    const [token, rawUser] = await Promise.all([
      AsyncStorage.getItem(TOKEN_KEY),
      AsyncStorage.getItem(USER_KEY),
    ]);
    return { token, user: rawUser ? JSON.parse(rawUser) : null };
  },
  async saveSession(token, user) {
    await Promise.all([
      AsyncStorage.setItem(TOKEN_KEY, token),
      AsyncStorage.setItem(USER_KEY, JSON.stringify(user)),
    ]);
  },
  async clearSession() {
    await Promise.all([
      AsyncStorage.removeItem(TOKEN_KEY),
      AsyncStorage.removeItem(USER_KEY),
    ]);
  },
};

export async function api(path, { method = 'GET', body, token } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let detail = `Erro ${res.status}`;
    try {
      const errJson = await res.json();
      detail = errJson.detail || detail;
    } catch {
      // sem corpo JSON
    }
    const err = new Error(detail);
    err.status = res.status;
    throw err;
  }
  return res.json();
}
