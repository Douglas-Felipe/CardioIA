// =============================================================
// CardioIA — Módulo IoT | Firmware Principal
// =============================================================
// Sistema de monitoramento cardíaco com ESP32 (Wokwi)
//
// Sensores:
//   - DHT22: Temperatura e umidade ambiente/corporal
//   - Potenciômetro: Simulação de oximetria (SpO2)
//
// Funcionalidades:
//   - Captura periódica de sinais vitais
//   - Resiliência offline: dados enviados via Serial quando sem conexão
//   - Transmissão para nuvem via MQTT (HiveMQ Cloud)
//   - Alertas visuais (LED) quando limites são ultrapassados
//
// Comandos Serial (para teste de resiliência):
//   '0' → Simula desconexão (modo offline)
//   '1' → Simula reconexão (modo online)
// =============================================================

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include "config.h"

// =============================================================
// Objetos Globais
// =============================================================
DHT dht(DHT_PIN, DHT_TYPE);
WiFiClientSecure wifiSecure;
PubSubClient mqtt(wifiSecure);

// =============================================================
// Variáveis de Estado
// =============================================================
bool simulatedOffline = false;    // Controle de simulação offline via Serial
unsigned long lastReadTime = 0;   // Timestamp da última leitura
unsigned long lastMqttRetry = 0;  // Timestamp da última tentativa MQTT

// =============================================================
// Protótipos de Funções
// =============================================================
void connectWiFi();
void connectMQTT();
void handleSerialCommands();
bool isOnline();
void readAndProcessSensors();
void publishLiveData(float temp, float hum, int spo2, bool alert);
void printBanner();

// =============================================================
// SETUP — Inicialização do sistema
// =============================================================
void setup() {
    Serial.begin(115200);
    delay(1000);
    printBanner();

    // --- Inicializar sensor DHT22 ---
    Serial.print("[DHT22] Inicializando sensor de temperatura... ");
    dht.begin();
    Serial.println("OK");

    // --- Configurar pinos ---
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    Serial.println("[GPIO]  LED de alerta configurado (GPIO 2)");
    Serial.printf("[GPIO]  Potenciômetro SpO2 configurado (GPIO %d)\n", SPO2_PIN);

    // --- Conectar Wi-Fi ---
    connectWiFi();

    // --- Configurar MQTT com TLS ---
    wifiSecure.setInsecure(); // Ignora verificação de certificado (adequado para Wokwi)
    mqtt.setServer(MQTT_BROKER, MQTT_PORT);
    mqtt.setBufferSize(512);
    Serial.printf("[MQTT]  Broker: %s:%d\n", MQTT_BROKER, MQTT_PORT);

    // --- Conectar ao broker MQTT ---
    if (WiFi.status() == WL_CONNECTED) {
        connectMQTT();
    }

    Serial.println("\n============================================");
    Serial.println(" Sistema pronto! Monitoramento iniciado.");
    Serial.println(" Comandos: '0'=offline  '1'=online");
    Serial.println("============================================\n");
}

// =============================================================
// LOOP — Ciclo principal de execução
// =============================================================
void loop() {
    // Processar comandos do Serial Monitor (toggle online/offline)
    handleSerialCommands();

    // Manter conexão MQTT ativa (se online)
    if (isOnline()) {
        if (!mqtt.connected()) {
            // Tentar reconectar com intervalo para não sobrecarregar
            unsigned long now = millis();
            if (now - lastMqttRetry >= MQTT_RECONNECT_MS) {
                lastMqttRetry = now;
                connectMQTT();
            }
        }
        mqtt.loop();
    }

    // Ler sensores no intervalo configurado
    if (millis() - lastReadTime >= READ_INTERVAL_MS) {
        lastReadTime = millis();
        readAndProcessSensors();
    }
}

// =============================================================
// Leitura e processamento dos sensores
// =============================================================
void readAndProcessSensors() {
    // --- Ler DHT22 (temperatura e umidade) ---
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    if (isnan(temperature) || isnan(humidity)) {
        Serial.println("[ERRO]  Falha na leitura do DHT22!");
        return;
    }

    // --- Ler SpO2 (potenciômetro: ADC 0-4095 → SpO2 85-100%) ---
    int rawAdc = analogRead(SPO2_PIN);
    int spo2 = map(rawAdc, 0, 4095, 85, 100);

    // --- Verificar alertas clínicos ---
    bool alertTemp = temperature > TEMP_MAX;
    bool alertSpo2 = spo2 < SPO2_MIN;
    bool alert = alertTemp || alertSpo2;

    // Acionar LED de alerta
    digitalWrite(LED_PIN, alert ? HIGH : LOW);

    // --- Montar JSON com os dados ---
    JsonDocument doc;
    doc["ts"] = millis();
    doc["temp"] = serialized(String(temperature, 1));
    doc["hum"] = serialized(String(humidity, 1));
    doc["spo2"] = spo2;
    doc["alert"] = alert ? 1 : 0;

    String jsonStr;
    serializeJson(doc, jsonStr);

    // --- Decidir: publicar via MQTT ou enviar via Serial ---
    if (isOnline() && mqtt.connected()) {
        // Publicar dados em tempo real via MQTT
        publishLiveData(temperature, humidity, spo2, alert);
        Serial.printf("[ONLINE]  %s\n", jsonStr.c_str());
    } else {
        // Modo offline: enviar dados via Serial (simulação de armazenamento local)
        Serial.printf("[OFFLINE] %s\n", jsonStr.c_str());
    }

    // --- Log de alertas no Serial ---
    if (alertTemp) {
        Serial.printf("[ALERTA] ⚠ FEBRE DETECTADA: %.1f°C (limite: %.1f°C)\n", temperature, TEMP_MAX);
    }
    if (alertSpo2) {
        Serial.printf("[ALERTA] ⚠ SpO2 BAIXO: %d%% (limite: %d%%)\n", spo2, SPO2_MIN);
    }
}

// =============================================================
// Publicar dados em tempo real via MQTT
// =============================================================
void publishLiveData(float temp, float hum, int spo2, bool alert) {
    // Publicar temperatura
    String tempStr = String(temp, 1);
    mqtt.publish(TOPIC_TEMP, tempStr.c_str(), true);

    // Publicar SpO2
    String spo2Str = String(spo2);
    mqtt.publish(TOPIC_SPO2, spo2Str.c_str(), true);

    // Publicar status de alerta
    mqtt.publish(TOPIC_STATUS, alert ? "ALERTA" : "NORMAL", true);
}

// =============================================================
// Conectar ao Wi-Fi (Wokwi Virtual AP)
// =============================================================
void connectWiFi() {
    Serial.printf("[WiFi]  Conectando a '%s'... ", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\n[WiFi]  Conectado! IP: %s\n", WiFi.localIP().toString().c_str());
    } else {
        Serial.println("\n[WiFi]  Falha na conexão. Operando em modo offline.");
    }
}

// =============================================================
// Conectar ao broker MQTT (HiveMQ Cloud com TLS)
// =============================================================
void connectMQTT() {
    if (mqtt.connected()) return;

    Serial.print("[MQTT]  Conectando ao HiveMQ Cloud... ");

    // Configurar Last Will and Testament (LWT)
    // Se o ESP32 desconectar inesperadamente, o broker publica "DESCONECTADO"
    if (mqtt.connect(MQTT_CLIENT, MQTT_USER, MQTT_PASS,
                     TOPIC_STATUS, 1, true, "DESCONECTADO")) {
        Serial.println("OK");
        // Publicar status de conexão
        mqtt.publish(TOPIC_STATUS, "CONECTADO", true);
    } else {
        Serial.printf("FALHA (rc=%d)\n", mqtt.state());
    }
}

// =============================================================
// Processar comandos do Serial Monitor
// =============================================================
void handleSerialCommands() {
    if (!Serial.available()) return;

    char cmd = Serial.read();

    switch (cmd) {
        case '0':
            simulatedOffline = true;
            Serial.println("\n[CMD]   → Modo OFFLINE ativado (simulação de desconexão)");
            Serial.println("[CMD]     Dados serão enviados apenas via Serial.\n");
            break;
        case '1':
            simulatedOffline = false;
            Serial.println("\n[CMD]   → Modo ONLINE ativado (simulação de reconexão)");
            Serial.println("[CMD]     Dados serão publicados via MQTT.\n");
            break;
        default:
            break; // Ignorar outros caracteres
    }
}

// =============================================================
// Verificar se o sistema está online
// =============================================================
bool isOnline() {
    return !simulatedOffline && (WiFi.status() == WL_CONNECTED);
}

// =============================================================
// Banner de inicialização
// =============================================================
void printBanner() {
    Serial.println("\n============================================");
    Serial.println("   CardioIA — Monitoramento IoT Cardíaco");
    Serial.println("   ESP32 + DHT22 + SpO2 (Simulado)");
    Serial.println("   FIAP — Fase IoT / Edge Computing");
    Serial.println("============================================\n");
}
