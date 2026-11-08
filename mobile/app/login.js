import React, { useState } from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../src/auth';
import { API_BASE_URL } from '../src/api';

export default function LoginScreen() {
  const { login } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState('medico');
  const [password, setPassword] = useState('cardio123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setError('');
    setLoading(true);
    try {
      await login(username.trim(), password);
      router.replace('/(tabs)/dashboard');
    } catch (err) {
      setError(err.message || 'Falha ao autenticar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={styles.card}>
        <View style={styles.brand}>
          <View style={styles.logo}>
            <Ionicons name="heart" size={26} color="#fff" />
          </View>
          <View>
            <Text style={styles.title}>CardioIA Mobile</Text>
            <Text style={styles.subtitle}>Inteligência Cardíaca · Fase 7</Text>
          </View>
        </View>

        <View style={styles.roleRow}>
          {['medico', 'paciente'].map((role) => (
            <Pressable
              key={role}
              onPress={() => {
                setUsername(role);
                setPassword('cardio123');
              }}
              style={[styles.roleBtn, username === role && styles.roleBtnActive]}
            >
              <Ionicons
                name={role === 'medico' ? 'medkit-outline' : 'person-outline'}
                size={16}
                color={username === role ? '#0369a1' : '#64748b'}
              />
              <Text style={[styles.roleText, username === role && styles.roleTextActive]}>
                {role === 'medico' ? 'Médico' : 'Paciente'}
              </Text>
            </Pressable>
          ))}
        </View>

        <Text style={styles.label}>Usuário</Text>
        <TextInput
          style={styles.input}
          value={username}
          onChangeText={setUsername}
          autoCapitalize="none"
        />

        <Text style={styles.label}>Senha</Text>
        <TextInput
          style={styles.input}
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />

        {error ? <Text style={styles.error}>{error}</Text> : null}

        <Pressable style={styles.submitBtn} onPress={handleLogin} disabled={loading}>
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.submitText}>Entrar</Text>
          )}
        </Pressable>

        <Text style={styles.hint}>API: {API_BASE_URL}</Text>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f1f5f9',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  card: {
    width: '100%',
    maxWidth: 400,
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 24,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  brand: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 18 },
  logo: {
    width: 46,
    height: 46,
    borderRadius: 12,
    backgroundColor: '#e11d48',
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: { fontSize: 20, fontWeight: '700', color: '#0f172a' },
  subtitle: { fontSize: 12, color: '#64748b' },
  roleRow: { flexDirection: 'row', gap: 8, marginBottom: 14 },
  roleBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingVertical: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  roleBtnActive: { borderColor: '#0284c7', backgroundColor: '#e0f2fe' },
  roleText: { fontWeight: '600', color: '#64748b' },
  roleTextActive: { color: '#0369a1' },
  label: { fontSize: 13, fontWeight: '600', color: '#334155', marginBottom: 4 },
  input: {
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: '#f8fafc',
    marginBottom: 12,
    fontSize: 15,
  },
  error: { color: '#b91c1c', backgroundColor: '#fef2f2', padding: 8, borderRadius: 6, marginBottom: 10 },
  submitBtn: {
    backgroundColor: '#0284c7',
    paddingVertical: 13,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 4,
  },
  submitText: { color: '#fff', fontWeight: '700', fontSize: 15 },
  hint: { fontSize: 11, color: '#94a3b8', textAlign: 'center', marginTop: 12 },
});
