import React, { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  AlertTriangle,
  Brain,
  CheckCircle2,
  ClipboardList,
  Cpu,
  Gauge,
  HeartPulse,
  MessageSquare,
  Radio,
  RefreshCw,
  ShieldAlert,
  Sparkles,
  Thermometer,
  Wind,
} from 'lucide-react';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { api } from '../api';
import { useAuth } from '../auth';

const POLL_MS = 3000;

const LEVEL_META = {
  NORMAL: {
    cls: 'level-normal',
    title: 'Estável · Baixo Risco',
    icon: CheckCircle2,
  },
  ATENCAO: {
    cls: 'level-atencao',
    title: 'Atenção · Monitorização Intensiva',
    icon: AlertTriangle,
  },
  CRITICO: {
    cls: 'level-critico',
    title: 'Crítico · Intervenção Imediata',
    icon: ShieldAlert,
  },
};

function VitalCard({ icon: Icon, label, value, unit, reference, status = 'NORMAL' }) {
  return (
    <div className={`vital-card status-${status.toLowerCase()}`}>
      <div className="vital-header">
        <span className="vital-label">{label}</span>
        <Icon size={20} className="vital-icon" />
      </div>
      <div className="vital-value">
        {value !== null && value !== undefined ? value : '--'}
        <span className="vital-unit">{unit}</span>
      </div>
      <div className="vital-footer">
        <span className="vital-ref">Ref: {reference}</span>
        <span className={`vital-pill pill-${status.toLowerCase()}`}>{status}</span>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const isMedico = user?.role === 'medico';

  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [simLoading, setSimLoading] = useState(false);

  const fetchDashboard = useCallback(async () => {
    try {
      const res = await api('/api/dashboard?limit=40');
      setData(res);
      setError('');
    } catch (err) {
      setError(err.message || 'Erro ao buscar dados do servidor.');
    }
  }, []);

  useEffect(() => {
    fetchDashboard();
    const id = setInterval(fetchDashboard, POLL_MS);
    return () => clearInterval(id);
  }, [fetchDashboard]);

  const simulate = async (scenario) => {
    setSimLoading(true);
    try {
      await api('/api/simulate', { method: 'POST', body: { scenario } });
      await fetchDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setSimLoading(false);
    }
  };

  const latest = data?.latest;
  const analysis = data?.analysis;
  const perSignal = analysis?.status_por_sinal || {};
  const level = analysis?.nivel || 'NORMAL';
  const meta = LEVEL_META[level] || LEVEL_META.NORMAL;
  const StatusIcon = meta.icon;

  const chartData = (data?.history || []).map((pt) => ({
    ...pt,
    hora: new Date(pt.ts * 1000).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }),
  }));

  const ml = analysis?.ml;
  const probPct = ml ? Math.round(ml.probabilidade * 100) : null;

  return (
    <div className="dashboard">
      {/* Barra de status IoT + Simulador */}
      <section className="iot-bar">
        <div className="iot-status">
          <span className={`dot-live ${data?.device?.online ? 'on' : 'off'}`} />
          <Radio size={16} />
          <span>
            Dispositivo Wokwi (MicroPython):{' '}
            <strong>{data?.device?.online ? 'ONLINE' : 'Aguardando telemetria'}</strong>
          </span>
          {latest && (
            <span className="iot-meta">
              · fonte: <code>{latest.source}</code> · leituras: {data?.device?.total_readings || 0}
            </span>
          )}
        </div>

        {isMedico && (
          <div className="sim-controls">
            <span className="sim-label">
              <Cpu size={14} /> Simular leitura:
            </span>
            <button
              type="button"
              className="btn-sim normal"
              disabled={simLoading}
              onClick={() => simulate('normal')}
            >
              Normal
            </button>
            <button
              type="button"
              className="btn-sim atencao"
              disabled={simLoading}
              onClick={() => simulate('atencao')}
            >
              Atenção
            </button>
            <button
              type="button"
              className="btn-sim critico"
              disabled={simLoading}
              onClick={() => simulate('critico')}
            >
              Crítico
            </button>
            <button
              type="button"
              className="btn-icon"
              onClick={fetchDashboard}
              title="Atualizar agora"
            >
              <RefreshCw size={14} />
            </button>
          </div>
        )}
      </section>

      {error && (
        <div className="banner-error" role="alert">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Semáforo principal de risco */}
      <section className={`risk-banner ${meta.cls}`} aria-live="polite">
        <div className="risk-banner-main">
          <StatusIcon size={32} />
          <div>
            <div className="risk-kicker">
              Status Clínico Consolidado · Paciente: <strong>João da Silva</strong>
            </div>
            <h2>{latest ? meta.title : 'Sem leituras recebidas ainda'}</h2>
            <p>
              {!latest
                ? isMedico
                  ? 'Inicie a simulação no Wokwi ou use os botões "Simular leitura" acima para testar o fluxo.'
                  : 'Aguardando envio de sinais do seu dispositivo.'
                : isMedico
                  ? analysis?.resumo_ia || analysis?.recomendacao
                  : analysis?.mensagem_paciente}
            </p>
          </div>
        </div>

        {isMedico && ml && (
          <div className="risk-gauge">
            <span className="gauge-label">Pico de Risco (ML Fase 6)</span>
            <strong className="gauge-value">{probPct}%</strong>
            <span className="gauge-sub">{ml.classificacao}</span>
          </div>
        )}
      </section>

      {/* Cards de sinais vitais */}
      <section className="vitals-grid" aria-label="Sinais vitais em tempo real">
        <VitalCard
          icon={HeartPulse}
          label="Frequência Cardíaca"
          value={latest ? Math.round(latest.bpm) : null}
          unit="bpm"
          reference="60–100 bpm"
          status={perSignal.bpm || 'NORMAL'}
        />
        <VitalCard
          icon={Wind}
          label="Saturação (SpO₂)"
          value={latest ? Math.round(latest.spo2) : null}
          unit="%"
          reference="95–100 %"
          status={perSignal.spo2 || 'NORMAL'}
        />
        <VitalCard
          icon={Thermometer}
          label="Temperatura"
          value={latest ? latest.temperature.toFixed(1) : null}
          unit="°C"
          reference="36,0–37,5 °C"
          status={perSignal.temperature || 'NORMAL'}
        />
        <VitalCard
          icon={Gauge}
          label="PA Sistólica"
          value={latest ? Math.round(latest.systolic) : null}
          unit="mmHg"
          reference="90–139 mmHg"
          status={perSignal.systolic || 'NORMAL'}
        />
      </section>

      {/* Visão do Paciente: atalho para o assistente */}
      {!isMedico && (
        <section className="patient-cta card-panel">
          <div>
            <h3>Sentindo algum sintoma ou tem dúvidas?</h3>
            <p>
              Converse com o Assistente CardioIA para relatar sintomas ou receber orientações em
              linguagem simples.
            </p>
          </div>
          <Link to="/chat" className="btn-primary">
            <MessageSquare size={18} /> Conversar com o Assistente
          </Link>
        </section>
      )}

      {/* Gráfico de evolução temporal */}
      <section className="card-panel">
        <div className="panel-header">
          <h3>
            <Activity size={18} /> Evolução em Tempo Real (últimas leituras)
          </h3>
          <span className="panel-sub">Atualização automática a cada 3 s</span>
        </div>
        {chartData.length === 0 ? (
          <p className="empty-state">Nenhuma leitura disponível para plotar o gráfico.</p>
        ) : (
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="hora" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} domain={[30, 210]} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="bpm"
                  name="FC (bpm)"
                  stroke="#e11d48"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="systolic"
                  name="PA Sistólica (mmHg)"
                  stroke="#0284c7"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="spo2"
                  name="SpO₂ (%)"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </section>

      {/* Seções exclusivas do Perfil Médico */}
      {isMedico && analysis && (
        <div className="medico-grid">
          <section className="card-panel">
            <div className="panel-header">
              <h3>
                <ClipboardList size={18} /> Protocolos Clínicos Acionados (Fase 6)
              </h3>
              <span className="panel-sub">{ml?.agente_emissor || 'Motor de Regras'}</span>
            </div>

            {analysis.alertas?.length > 0 && (
              <div className="alert-tags">
                {analysis.alertas.map((a, i) => (
                  <span key={i} className="alert-tag">
                    {a}
                  </span>
                ))}
              </div>
            )}

            {analysis.protocolos?.length > 0 ? (
              <ul className="protocol-list">
                {analysis.protocolos.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            ) : (
              <p className="empty-state">
                Nenhum protocolo de emergência disparado para os parâmetros atuais.
              </p>
            )}

            {analysis.resumo_ia && (
              <div className="llm-box">
                <Sparkles size={16} />
                <div>
                  <strong>Síntese LLM ({analysis.llm_provider}):</strong>
                  <p>{analysis.resumo_ia}</p>
                </div>
              </div>
            )}
          </section>

          <section className="card-panel">
            <div className="panel-header">
              <h3>
                <Brain size={18} /> Orquestração Multiagente & Histórico de Alertas
              </h3>
              <span className="panel-sub">Hub-and-Spoke</span>
            </div>

            {ml?.trace && (
              <ol className="agent-trace">
                {ml.trace.map((step, i) => (
                  <li key={i}>
                    <span className="trace-badge">{step.tipo}</span>
                    <strong>{step.de}</strong> → <em>{step.para}</em>: {step.conteudo}
                  </li>
                ))}
              </ol>
            )}

            <h4 className="sub-heading">Últimos alertas registrados</h4>
            {data?.alerts?.length > 0 ? (
              <ul className="alerts-history">
                {data.alerts.slice(0, 6).map((al, i) => (
                  <li key={i} className={`alert-row level-${al.nivel.toLowerCase()}`}>
                    <span>{new Date(al.ts * 1000).toLocaleTimeString()}</span>
                    <strong>{al.nivel}</strong>
                    <span>{al.alertas.join('; ') || al.classificacao_ml}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="empty-state">Sem alertas críticos registrados nesta sessão.</p>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
