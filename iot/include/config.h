// =============================================================
// CardioIA — Módulo IoT | Arquivo de Configuração
// =============================================================
// Centraliza todas as constantes do sistema de monitoramento
// cardíaco: pinos, limites clínicos, MQTT e resiliência.
// =============================================================

#ifndef CONFIG_H
#define CONFIG_H

// --- Pinos dos Sensores ---
#define DHT_PIN       15    // GPIO do sensor DHT22 (temperatura e umidade)
#define DHT_TYPE      DHT22
#define SPO2_PIN      34    // GPIO do potenciômetro (simulação de SpO2, ADC1)
#define LED_PIN       2     // GPIO do LED de alerta

// --- Limites Clínicos para Alertas ---
#define TEMP_MAX      38.0  // Temperatura máxima normal (°C)
#define SPO2_MIN      92    // SpO2 mínimo aceitável (%)

// --- Intervalos de Tempo ---
#define READ_INTERVAL_MS  10000   // Intervalo entre leituras (10 segundos)
#define MQTT_RECONNECT_MS 5000    // Intervalo entre tentativas MQTT (5 segundos)

// --- Wi-Fi (Wokwi Virtual AP) ---
#define WIFI_SSID     "Wokwi-GUEST"
#define WIFI_PASSWORD ""

// --- Configuração MQTT (HiveMQ Cloud) ---
#define MQTT_BROKER   "7a6c9a375f5b4f5c95df80f366f9b118.s1.eu.hivemq.cloud"
#define MQTT_PORT     8883
#define MQTT_USER     "ESPFIAP"
#define MQTT_PASS     "ESPFiap123"
#define MQTT_CLIENT   "cardioia-esp32"

// --- Tópicos MQTT ---
#define TOPIC_TEMP    "cardioia/vitals/temperature"
#define TOPIC_SPO2    "cardioia/vitals/spo2"
#define TOPIC_STATUS  "cardioia/status"
#define TOPIC_SYNC    "cardioia/vitals/sync"

// --- Resiliência Offline (Edge Computing) ---
#define SPIFFS_LOG_PATH       "/data.log"
#define MAX_OFFLINE_SAMPLES   500   // ~50KB, cobre ~8h com leitura a cada minuto

#endif // CONFIG_H
