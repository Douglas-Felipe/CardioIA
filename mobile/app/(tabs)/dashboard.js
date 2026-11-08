import React, { useCallback, useEffect, useState } from 'react';
import {
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { api } from '../../src/api';
import { useAuth } from '../../src/auth';

const COLORS = {
  NORMAL: { bg: '#ecfdf5', border: '#10b981', text: '#065f46' },
  ATENCAO: { bg: '#fffbeb', border: '#f59e0b', text: '#92400e' },
  CRITICO: { bg: '#fff1f2', border: '#e11d48', text: '#9f1239' },
};

function VitalBox({ label, value, unit, status = 'NORMAL' }) {
  const c = COLORS[status] || COLORS.NORMAL;
  return (
    <View style={[styles.vitalBox, { borderLeftColor: c.border }]}>
      <Text style={styles.vitalLabel}>{label}</Text>
      <Text style={styles.vitalValue}>
        {value !== null && value !== undefined ? value : '--'}{' '}
        <Text style={styles.vitalUnit}>{unit}</Text>
      </Text>
      <Text style={[styles.vitalPill, { color: c.text, backgroundColor: c.bg }]}>{status}</Text>
    </View>
  );
}

export default function DashboardScreen() {
  const { token, user, logout } = useAuth();
  const isMedico = user?.role === 'medico';
  const [data, setData] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    if (!token) return;
    try {
      const res = await api('/api/dashboard?limit=20', { token });
      setData(res);
      setError('');
    } catch (err) {
      if (err.status === 401) logout();
      setError(err.message);
    }
  }, [token, logout]);

  useEffect(() => {
    load();
    const id = setInterval(load, 3000);
    return () => clearInterval(id);
  }, [load]);

  const simulate = async (scenario) => {
    try {
      await api('/api/simulate', { method: 'POST', token, body: { scenario } });
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const latest = data?.latest;
  const analysis = data?.analysis;
  const per = analysis?.status_por_sinal || {};
  const level = analysis?.nivel || 'NORMAL';
  const palette = COLORS[level] || COLORS.NORMAL;
  const ml = analysis?.ml;

  return (
    <ScrollView
      style={styles.screen}
      contentContainerStyle={{ padding: 16, gap: 14 }}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={async () => {
            setRefreshing(true);
            await load();
            setRefreshing(false);
          }}
        />
      }
    >
      <View style={styles.iotRow}>
        <View style={[styles.dot, { backgroundColor: data?.device?.online ? '#10b981' : '#94a3b8' }]} />
        <Text style={styles.iotText}>
          Wokwi MicroPython: {data?.device?.online ? 'ONLINE' : 'Aguardando'} · leituras:{' '}
          {data?.device?.total_readings || 0}
        </Text>
      </View>

      {isMedico && (
        <View style={styles.simRow}>
          {['normal', 'atencao', 'critico'].map((sc) => (
            <Pressable key={sc} style={styles.simBtn} onPress={() => simulate(sc)}>
              <Text style={styles.simBtnText}>Simular {sc}</Text>
            </Pressable>
          ))}
        </View>
      )}

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <View style={[styles.banner, { backgroundColor: palette.bg, borderColor: palette.border }]}>
        <Text style={[styles.bannerTitle, { color: palette.text }]}>
          Status: {level} {ml ? `· ML: ${Math.round(ml.probabilidade * 100)}% (${ml.classificacao})` : ''}
        </Text>
        <Text style={[styles.bannerBody, { color: palette.text }]}>
          {!latest
            ? 'Nenhuma leitura recebida ainda.'
            : isMedico
              ? analysis?.resumo_ia || analysis?.recomendacao
              : analysis?.mensagem_paciente}
        </Text>
      </View>

      <View style={styles.grid}>
        <VitalBox
          label="Freq. Cardíaca"
          value={latest ? Math.round(latest.bpm) : null}
          unit="bpm"
          status={per.bpm}
        />
        <VitalBox
          label="Saturação SpO₂"
          value={latest ? Math.round(latest.spo2) : null}
          unit="%"
          status={per.spo2}
        />
        <VitalBox
          label="Temperatura"
          value={latest ? latest.temperature.toFixed(1) : null}
          unit="°C"
          status={per.temperature}
        />
        <VitalBox
          label="PA Sistólica"
          value={latest ? Math.round(latest.systolic) : null}
          unit="mmHg"
          status={per.systolic}
        />
      </View>

      {isMedico && analysis?.protocolos?.length > 0 && (
        <View style={styles.panel}>
          <Text style={styles.panelTitle}>Protocolos Clínicos Acionados (Fase 6)</Text>
          {analysis.protocolos.map((p, idx) => (
            <Text key={idx} style={styles.protocolItem}>
              • {p}
            </Text>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#f1f5f9' },
  iotRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 10,
  },
  dot: { width: 10, height: 10, borderRadius: 5 },
  iotText: { fontSize: 13, color: '#334155', fontWeight: '600' },
  simRow: { flexDirection: 'row', gap: 8 },
  simBtn: {
    flex: 1,
    backgroundColor: '#fff',
    paddingVertical: 8,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#cbd5e1',
  },
  simBtnText: { fontSize: 12, fontWeight: '600', color: '#0369a1' },
  error: { backgroundColor: '#fef2f2', color: '#b91c1c', padding: 10, borderRadius: 8 },
  banner: { borderWidth: 1, borderRadius: 12, padding: 14 },
  bannerTitle: { fontWeight: '700', fontSize: 15, marginBottom: 4 },
  bannerBody: { fontSize: 13, lineHeight: 19 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  vitalBox: {
    width: '48%',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 14,
    borderLeftWidth: 5,
  },
  vitalLabel: { fontSize: 12, color: '#64748b' },
  vitalValue: { fontSize: 24, fontWeight: '700', color: '#0f172a', marginVertical: 6 },
  vitalUnit: { fontSize: 13, fontWeight: '500', color: '#64748b' },
  vitalPill: { alignSelf: 'flex-start', fontSize: 11, fontWeight: '700', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 99 },
  panel: { backgroundColor: '#fff', borderRadius: 12, padding: 14, gap: 6 },
  panelTitle: { fontWeight: '700', fontSize: 14, marginBottom: 4 },
  protocolItem: { fontSize: 13, color: '#334155', lineHeight: 18 },
});
