"""Regras clínicas determinísticas sobre os sinais vitais.

Espelham exatamente a lógica de borda (edge) executada no ESP32 em MicroPython
(iot/micropython/main.py), garantindo consistência entre dispositivo e backend.
"""

from typing import Dict, List, Tuple

NORMAL = "NORMAL"
ATENCAO = "ATENCAO"
CRITICO = "CRITICO"

_LEVEL_ORDER = {NORMAL: 0, ATENCAO: 1, CRITICO: 2}


def worst(*levels: str) -> str:
    return max(levels, key=lambda lv: _LEVEL_ORDER.get(lv, 0))


def classify_bpm(bpm: float) -> str:
    if bpm < 50 or bpm > 120:
        return CRITICO
    if bpm < 60 or bpm > 100:
        return ATENCAO
    return NORMAL


def classify_spo2(spo2: float) -> str:
    if spo2 < 90:
        return CRITICO
    if spo2 < 95:
        return ATENCAO
    return NORMAL


def classify_temperature(temp: float) -> str:
    if temp >= 39.0 or temp < 35.0:
        return CRITICO
    if temp >= 37.6:
        return ATENCAO
    return NORMAL


def classify_systolic(sys_bp: float) -> str:
    if sys_bp >= 180 or sys_bp < 90:
        return CRITICO
    if sys_bp >= 140:
        return ATENCAO
    return NORMAL


_MESSAGES = {
    ("bpm", ATENCAO): "Frequência cardíaca fora da faixa ideal (60-100 bpm)",
    ("bpm", CRITICO): "Frequência cardíaca crítica (<50 ou >120 bpm)",
    ("spo2", ATENCAO): "Saturação de O2 levemente reduzida (90-94%)",
    ("spo2", CRITICO): "Hipoxemia: SpO2 abaixo de 90%",
    ("temperature", ATENCAO): "Estado febril (≥37,6 °C)",
    ("temperature", CRITICO): "Temperatura crítica (≥39 °C ou <35 °C)",
    ("systolic", ATENCAO): "Pressão sistólica elevada (≥140 mmHg)",
    ("systolic", CRITICO): "Pressão sistólica crítica (≥180 ou <90 mmHg)",
}


def evaluate_vitals(bpm: float, spo2: float, temperature: float, systolic: float) -> Tuple[str, Dict[str, str], List[str]]:
    """Retorna (status_geral, status_por_sinal, lista_de_alertas)."""
    per_signal = {
        "bpm": classify_bpm(bpm),
        "spo2": classify_spo2(spo2),
        "temperature": classify_temperature(temperature),
        "systolic": classify_systolic(systolic),
    }
    alerts = [_MESSAGES[(k, v)] for k, v in per_signal.items() if v != NORMAL]
    return worst(*per_signal.values()), per_signal, alerts
