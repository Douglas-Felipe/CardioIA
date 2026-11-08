import React, { useEffect, useState } from 'react';
import {
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { api } from '../../src/api';
import { useAuth } from '../../src/auth';

export default function ChatScreen() {
  const { token } = useAuth();
  const [sessionId, setSessionId] = useState(null);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'assistant',
      text: 'Olá! Sou o Assistente CardioIA. Pergunte "como estou?" para consultar seus sinais vitais ou relate sintomas.',
    },
  ]);

  useEffect(() => {
    if (!token) return;
    api('/api/chat/session', { method: 'POST', token })
      .then((d) => setSessionId(d.session_id))
      .catch(() => {});
  }, [token]);

  const send = async (textOverride) => {
    const text = (textOverride ?? input).trim();
    if (!text || loading) return;
    setInput('');
    setMessages((m) => [...m, { id: String(Date.now()), sender: 'user', text }]);
    setLoading(true);
    try {
      const data = await api('/api/chat', {
        method: 'POST',
        token,
        body: { message: text, session_id: sessionId },
      });
      if (data.session_id) setSessionId(data.session_id);
      setMessages((m) => [
        ...m,
        { id: String(Date.now() + 1), sender: 'assistant', text: data.response },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          id: String(Date.now() + 1),
          sender: 'assistant',
          text: 'Falha ao contatar o servidor. Em caso de emergência, ligue 192 (SAMU).',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={90}
    >
      <FlatList
        data={messages}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{ padding: 14, gap: 10 }}
        renderItem={({ item }) => (
          <View
            style={[
              styles.bubble,
              item.sender === 'user' ? styles.userBubble : styles.botBubble,
            ]}
          >
            <Text style={item.sender === 'user' ? styles.userText : styles.botText}>
              {item.text}
            </Text>
          </View>
        )}
      />

      <View style={styles.chips}>
        {['Como estou?', 'Estou com dor no peito', 'Dicas de prevenção'].map((c) => (
          <Pressable key={c} style={styles.chip} onPress={() => send(c)}>
            <Text style={styles.chipText}>{c}</Text>
          </Pressable>
        ))}
      </View>

      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="Digite sua dúvida ou sintoma..."
        />
        <Pressable style={styles.sendBtn} onPress={() => send()} disabled={loading}>
          <Ionicons name="send" size={18} color="#fff" />
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f1f5f9' },
  bubble: { maxWidth: '84%', padding: 12, borderRadius: 12 },
  userBubble: { alignSelf: 'flex-end', backgroundColor: '#0284c7' },
  botBubble: { alignSelf: 'flex-start', backgroundColor: '#fff', borderWidth: 1, borderColor: '#e2e8f0' },
  userText: { color: '#fff', fontSize: 14 },
  botText: { color: '#0f172a', fontSize: 14, lineHeight: 20 },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, paddingHorizontal: 12, paddingBottom: 6 },
  chip: { backgroundColor: '#e0f2fe', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 99 },
  chipText: { color: '#0369a1', fontSize: 12, fontWeight: '600' },
  inputRow: {
    flexDirection: 'row',
    gap: 8,
    padding: 10,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderColor: '#e2e8f0',
  },
  input: {
    flex: 1,
    backgroundColor: '#f8fafc',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  sendBtn: {
    width: 42,
    height: 42,
    borderRadius: 8,
    backgroundColor: '#0284c7',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
