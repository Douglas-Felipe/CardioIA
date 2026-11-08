"""Armazenamento em memória (thread-safe) das leituras, análises e alertas.

Para o MVP no Render free tier o armazenamento é efêmero: mantém um buffer
circular das últimas N leituras e é reiniciado a cada deploy/hibernação.
"""

import threading
import time
from collections import deque
from typing import Any, Deque, Dict, List, Optional

from .config import settings


class TelemetryStore:
    def __init__(self, maxlen: int = settings.history_size) -> None:
        self._lock = threading.Lock()
        self._readings: Deque[Dict[str, Any]] = deque(maxlen=maxlen)
        self._alerts: Deque[Dict[str, Any]] = deque(maxlen=100)
        self._last_level: Optional[str] = None
        self.total_received = 0

    def add(self, reading: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        entry = {"ts": time.time(), **reading, "analysis": analysis}
        with self._lock:
            self._readings.append(entry)
            self.total_received += 1
            level = analysis["nivel"]
            # Registra alerta somente quando o nível muda para ATENCAO/CRITICO
            if level != "NORMAL" and level != self._last_level:
                self._alerts.appendleft(
                    {
                        "ts": entry["ts"],
                        "nivel": level,
                        "alertas": analysis["alertas"],
                        "classificacao_ml": (analysis.get("ml") or {}).get("classificacao"),
                        "source": reading.get("source", "device"),
                    }
                )
            self._last_level = level
        return entry

    def latest(self) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._readings[-1] if self._readings else None

    def history(self, limit: int = 60) -> List[Dict[str, Any]]:
        with self._lock:
            items = list(self._readings)[-limit:]
        # Histórico enxuto (sem a análise completa) para gráficos
        return [
            {
                "ts": r["ts"],
                "bpm": r["bpm"],
                "spo2": r["spo2"],
                "temperature": r["temperature"],
                "systolic": r["systolic"],
                "nivel": r["analysis"]["nivel"],
                "probabilidade": (r["analysis"].get("ml") or {}).get("probabilidade"),
            }
            for r in items
        ]

    def alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._alerts)[:limit]

    def device_online(self) -> bool:
        last = self.latest()
        return bool(last and last.get("source") == "device" and time.time() - last["ts"] <= settings.device_offline_seconds)

    def clear(self) -> None:
        with self._lock:
            self._readings.clear()
            self._alerts.clear()
            self._last_level = None
            self.total_received = 0


store = TelemetryStore()
