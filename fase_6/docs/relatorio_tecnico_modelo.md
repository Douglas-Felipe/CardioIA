# Relatório Técnico: Decisões e Avaliação do Modelo Preditivo de Risco Cardíaco

---

## 1. Visão Geral e Contexto Clínico-Operacional

O objetivo deste módulo é a construção, validação e disponibilização de um modelo preditivo supervisionado capaz de antecipar picos de risco cardíaco hospitalar (`pico_risco = 1`) em pacientes admitidos em unidades de pronto atendimento e terapia intensiva.

A base de dados de desenvolvimento compreende **5.000 registros sintéticos** estruturados a partir de distribuições fisiológicas e operacionais realistas, abrangendo 10 variáveis preditoras:
* **Parâmetros Fisiológicos:** `spo2_media` (saturação de oxigênio), `fc_media` (frequência cardíaca), `pa_sistolica` (pressão arterial), `temperatura`, `idade_media`.
* **Parâmetros Operacionais e Sistêmicos:** `carga_sistema` (% de lotação), `tempo_espera` (minutos), `disponibilidade_recursos` (%), `densidade_eventos`, `eventos_24h`.

O particionamento dos dados seguiu amostragem estratificada na proporção **80% treino (4.000 amostras)** e **20% teste independente (1.000 amostras)**, assegurando a preservação da proporção original das classes (~73% classe 0 e ~27% classe 1).

---

## 2. Justificativa do Algoritmo e Benchmark Comparativo

Foram submetidos a benchmark cinco algoritmos supervisionados clássicos, pré-processados com padronização estatística (`StandardScaler`) e submetidos a validação cruzada estratificada em 5 folds:

| Algoritmo | Acurácia (Teste) | F1-Score | ROC-AUC | CV ROC-AUC (5 Folds) | Tempo de Inferência |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (Campeão)** | **99.90%** | **0.9981** | **1.0000** | **1.0000 ± 0.0000** | **< 2.5 ms** |
| Gradient Boosting | 99.80% | 0.9962 | 0.9999 | 0.9999 ± 0.0002 | ~ 3.1 ms |
| Support Vector Machine (RBF Calibrado) | 87.70% | 0.7555 | 0.9488 | 0.9507 ± 0.0043 | ~ 12.8 ms |
| K-Nearest Neighbors ($k=5$) | 83.70% | 0.6091 | 0.8751 | 0.8864 ± 0.0067 | ~ 8.4 ms |
| Regressão Logística | 81.60% | 0.6151 | 0.8715 | 0.8864 ± 0.0106 | **< 1.0 ms** |

### 2.1 Por que o Random Forest foi o Escolhido?

1. **Aderência Geométrica à Função Geradora:**  
   O limiar de pico de risco é determinado pela conjunção de regras clínicas booleanas com pontos de corte retangulares nos eixos coordenados (`carga > 80`, `spo2 < 92`, `fc > 110`, etc.). Modelos baseados em árvores de decisão particionam o espaço ortogonalmente, permitindo ao **Random Forest** reconstruir de forma exata a fronteira lógica.
2. **Superioridade sobre Modelos Lineares e Métricos:**  
   A **Regressão Logística** tenta traçar um hiperplano contínuo suave, falhando nas descontinuidades abruptas em degrau. O **KNN** sofre com a maldição da dimensionalidade no espaço euclidiano 10D, degradado pelas variáveis irrelevantes (`temperatura`, `idade_media`, `pa_sistolica`).
3. **Calibração Probabilística e Estabilidade:**  
   O ensemble de 100 estimadores suaviza as probabilidades preditas por meio da média da fração de votos das árvores, permitindo extrair estimativas contínuas e calibradas de probabilidade de risco essenciais para a triagem médica.

### 2.2 Diagnóstico Crítico: Overfitting ou Aprendizado Causal?

A proximidade de 100% de acurácia foi minuciosamente investigada para descartar *data leakage* ou memorização rasa:
* **Gap de Generalização:** A acurácia de treino foi de **100.00%** e a de teste de **99.90%** (diferença residual de apenas 0.10%). Na validação cruzada em 5 partições independentes, o desvio padrão foi nulo ($1.0000 \pm 0.0000$).
* **Importância das Variáveis (*Feature Importance*):**  
  As 6 variáveis causais da regra concentram **95.89%** de todo o peso do modelo (`carga_sistema`: 22.85%, `disponibilidade_recursos`: 21.79%, `tempo_espera`: 20.77%, `spo2_media`: 16.85%, `fc_media`: 7.13%, `eventos_24h`: 6.50%). As 4 variáveis clinicamente neutras somaram juntas menos de 4.11%. Isso comprova que o modelo aprendeu as relações causais verdadeiras em vez de decorar ruídos aleatórios.

---

## 3. Interpretação das Métricas e Análise da Matriz de Confusão

O modelo campeão foi avaliado no conjunto de teste independente (1.000 pacientes não observados durante o ajuste dos parâmetros):

```
                  Matriz de Confusão (Teste N = 1000)
                  
                           Predição Negativa    Predição Positiva
      Real Negativo (0)         734 (TN)               0 (FP)
      Real Positivo (1)           1 (FN)             265 (TP)
```

### 3.1 Métricas Detalhadas por Classe

* **Acurácia Global:** **99.90%** (999 acertos em 1.000 predições).
* **Precisão (Classe Positiva):** **100.00%** ($265 / [265 + 0]$).  
  *Impacto Clínico:* Ausência absoluta de falsos positivos (FP = 0). O sistema nunca dispara um alerta indevido de pico de risco, evitando saturação de leitos de UTI, pânico na equipe e desperdício de insumos críticos.
* **Sensibilidade / Recall (Classe Positiva):** **99.62%** ($265 / [265 + 1]$).  
  *Impacto Clínico:* De 266 pacientes reais com pico de risco, o modelo detectou 265. Houve apenas 1 falso negativo em um caso limítrofe no limiar de transição estocástica. Em triagem hospitalar, o recall elevado é o indicador mais crítico para salvar vidas.
* **F1-Score Ponderado:** **0.9981**, atestando equilíbrio quase perfeito entre precisão e sensibilidade.
* **Área sob a Curva ROC (ROC-AUC):** **1.0000**, demonstrando capacidade de ordenação e discriminação ideal em qualquer limiar de decisão operacional.

---

## 4. Limitações Identificadas e Proposta de Melhorias

Apesar da performance na base simulada, o deployment em ambiente de produção hospitalar requer atenção às seguintes limitações:

### 4.1 Limitações Técnicas e Clínicas
1. **Natureza Sintética e Ausência de Ruído Biológico:**  
   Em hospitais reais (bases como MIMIC-IV e eICU), os dados apresentam ruídos de artefatos de eletrodos, comorbidades latentes (diabetes, insuficiência cardíaca crônica), valores faltantes e atrasos de telemetria. Uma acurácia de 99.9% em dados reais seria forte indício de vazamento de rótulo.
2. **Desbalanceamento das Classes:**  
   A base apresenta 73% de casos normais e 27% de picos de risco. Em pronto-socorro geral, a incidência de picos graves pode ser inferior a 5%, exigindo técnicas como *cost-sensitive learning* ou ajuste do threshold de decisão.
3. **Estática Temporal:**  
   O modelo atual avalia uma foto pontual do paciente (*snapshot* tabular), desconsiderando a tendência de evolução contínua das últimas horas.

### 4.2 Recomendações e Melhorias Futuras
* **Monitoramento Contínuo com Séries Temporais:** Substituir inferências isoladas por janelas deslizantes com arquiteturas neurais recorrentes ou temporais (LSTM / Temporal Fusion Transformers) para predição antecipada com horizonte de 4 a 6 horas.
* **Explicabilidade Local Integrada (SHAP / TreeSHAP):** Adicionar valores de SHAP diretamente ao laudo do Agente Analista de Risco, informando à equipe médica a contribuição exata de cada biomarcador no score de risco predito.
* **Validação Prospectiva Multicêntrica:** Conduzir ensaios clínicos simulados em múltiplos centros hospitalares para calibrar a sensibilidade a diferentes perfis demográficos e protocolos locais.
* **Integração MLOps e Monitoramento de Drift:** Implementar monitoramento contínuo de desvio de dados (*data drift*) e degradação de conceito (*concept drift*) para re-treinamento automatizado periódico do pipeline serializado (`cardiac_risk_pipeline.joblib`).
