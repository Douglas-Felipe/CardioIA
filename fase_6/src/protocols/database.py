from typing import List, Dict, Any

# Lista de protocolos
SIMULATED_PROTOCOLS: List[str] = [
    "Se SPO2 < 88% → iniciar suporte respiratório imediato",
    "Se carga do sistema > 85% → abrir unidades temporárias",
    "Se FC > 120 → iniciar monitoramento intensivo",
    "Se eventos_24h > 5 → ativar equipe de resposta rápida",
    "Se disponibilidade_recursos < 30% → redistribuir insumos",
    "Se tempo_espera > 90 min → priorizar triagem emergencial",
    "Se temperatura > 38°C média → iniciar protocolo infeccioso",
    "Se densidade_eventos > 6 → ativar plano de contingência",
    "Se PA sistólica < 90 → iniciar protocolo de choque",
    "Se risco sistêmico alto → ativar estado de emergência"
]

# Metadados estruturados para cada protocolo para avaliação automatizada e híbrida
PROTOCOL_RULES_METADATA: List[Dict[str, Any]] = [
    {
        "id": "spo2_suporte",
        "regra": "Se SPO2 < 88% → iniciar suporte respiratório imediato",
        "parametro": "spo2_media",
        "operador": "<",
        "limiar": 88.0,
        "acao": "iniciar suporte respiratório imediato"
    },
    {
        "id": "carga_temporaria",
        "regra": "Se carga do sistema > 85% → abrir unidades temporárias",
        "parametro": "carga_sistema",
        "operador": ">",
        "limiar": 85.0,
        "acao": "abrir unidades temporárias"
    },
    {
        "id": "fc_monitoramento",
        "regra": "Se FC > 120 → iniciar monitoramento intensivo",
        "parametro": "fc_media",
        "operador": ">",
        "limiar": 120.0,
        "acao": "iniciar monitoramento intensivo"
    },
    {
        "id": "eventos_equipe_rapida",
        "regra": "Se eventos_24h > 5 → ativar equipe de resposta rápida",
        "parametro": "eventos_24h",
        "operador": ">",
        "limiar": 5.0,
        "acao": "ativar equipe de resposta rápida"
    },
    {
        "id": "recursos_insumos",
        "regra": "Se disponibilidade_recursos < 30% → redistribuir insumos",
        "parametro": "disponibilidade_recursos",
        "operador": "<",
        "limiar": 30.0,
        "acao": "redistribuir insumos"
    },
    {
        "id": "espera_triagem",
        "regra": "Se tempo_espera > 90 min → priorizar triagem emergencial",
        "parametro": "tempo_espera",
        "operador": ">",
        "limiar": 90.0,
        "acao": "priorizar triagem emergencial"
    },
    {
        "id": "temp_infeccioso",
        "regra": "Se temperatura > 38°C média → iniciar protocolo infeccioso",
        "parametro": "temperatura",
        "operador": ">",
        "limiar": 38.0,
        "acao": "iniciar protocolo infeccioso"
    },
    {
        "id": "densidade_contingencia",
        "regra": "Se densidade_eventos > 6 → ativar plano de contingência",
        "parametro": "densidade_eventos",
        "operador": ">",
        "limiar": 6.0,
        "acao": "ativar plano de contingência"
    },
    {
        "id": "pa_choque",
        "regra": "Se PA sistólica < 90 → iniciar protocolo de choque",
        "parametro": "pa_sistolica",
        "operador": "<",
        "limiar": 90.0,
        "acao": "iniciar protocolo de choque"
    },
    {
        "id": "risco_emergencia",
        "regra": "Se risco sistêmico alto → ativar estado de emergência",
        "parametro": "probabilidade_risco",
        "operador": ">=",
        "limiar": 0.80,
        "acao": "ativar estado de emergência"
    }
]
