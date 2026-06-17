# 🫀 Processo de Treinamento e Otimização — CardioIA

Este documento sintetiza o pipeline de preparação de dados, estratégias de modelagem, balanceamento de perdas e critérios de seleção implementados no notebook de visão computacional da CardioIA (cardio_ia_visao_computacional.ipynb).

---

## 📌 1. Visão Geral do Dataset e Redução de Dados
O objetivo clínico do projeto é classificar imagens de Raio-X de Tórax em 3 categorias: **Cardiomegaly** (Cardiomegalia), **Effusion** (Derrame Pleural) e **No Finding** (Exame Normal).

* **Origem dos Dados**: Dataset oficial **NIH Chest X-ray** obtido via Kaggle.
* **Otimização de Escopo (Halving)**: Para mitigar restrições de memória física RAM/VRAM e acelerar o ciclo de treinamento, reduzimos a base original de dados de forma homogênea em **50%**.
* **Prevenção de Vazamento (Data Leakage)**: A redução e a posterior divisão de dados foram feitas estritamente no nível de paciente único (`Patient ID`). Isso impede que radiografias do mesmo paciente caiam em partições diferentes.
* **Divisão Estipulada**:
  * **Treino**: 80% dos pacientes (~3.171 imagens)
  * **Validação**: 10% dos pacientes (~3.225 imagens)
  * **Teste**: 10% dos pacientes (~3.227 imagens)

---

## ⚖️ 2. Estratégia de Balanceamento e Ponderação de Perdas

### A. Subamostragem de Treino
Para evitar o viés da classe majoritária (*No Finding*), o conjunto de treinamento foi fisicamente balanceado através de subamostragem na proporção **1:2:4** (Cardiomegaly:Effusion:No Finding).

### B. O Problema: A Armadilha da Loss de Validação (Validation Loss Trap)
O conjunto de validação real possui **92.4%** de imagens *No Finding* (classe majoritária). Sem compensação:
1. Um classificador dummy que chuta *No Finding* para 100% dos dados atinge ~92% de acurácia com uma perda (`val_loss`) muito baixa na Época 1.
2. Quando o modelo começa a aprender patologias reais nas épocas seguintes, ele inevitavelmente comete pequenos erros (falsos positivos) na enorme classe majoritária.
3. Esses pequenos erros acumulam um grande volume de perda, fazendo com que a `val_loss` global dispare de forma fictícia.
4. O `EarlyStopping` identificava o menor ponto de perda na Época 1, interrompia o treino e restaurava os pesos do modelo dummy.

### C. A Solução: Pesos de Amostra Dinâmicos (`Sample_Weight`)
Removemos o parâmetro `class_weight` tradicional do Keras (que causava conflitos na compilação de geradores) e mapeamos pesos de classe diretamente em uma coluna de pesos de amostra (`Sample_Weight`) nos geradores de treino e validação:
* **Pesos Ponderados de Treino**: Cardiomegaly = **2.33** | Effusion = **1.17** | No Finding = **0.58**
* **Pesos Ponderados de Validação (Sem Suavização)**: Cardiomegaly = **17.91** | Effusion = **5.78** | No Finding = **0.36**

*Resultado*: A perda de validação foi perfeitamente equilibrada, de forma que cada classe contribui com exatamente **33.3%** na perda final. O `EarlyStopping` agora só interrompe o treino quando o aprendizado real estabiliza.

---

## 🧠 3. Arquiteturas de Modelagem e Compilação

### A. CNN Simples (Treinada do Zero)
* **Estrutura**: 3 blocos convolucionais com `Conv2D`, `BatchNormalization`, `MaxPooling2D` e `Dropout` de regularização.
* **Otimização GAP2D**: Substituímos a camada `Flatten()` por `GlobalAveragePooling2D()`. Isso reduziu radicalmente os parâmetros densos e evitou o overfitting.
* **Ajustes de Treino**:
  * Otimizador Adam com taxa de aprendizado reduzida para `0.0002` (estabilidade).
  * Compilado com `weighted_metrics=['accuracy']` para rastrear a acurácia balanceada (curva começa em 33.3% e evolui com o aprendizado de patologias).

### B. Transfer Learning com VGG16
* **Estrutura**: Base da VGG16 (ImageNet weights) seguida de GAP2D, Dense(512), BatchNorm, Dropout(0.5), Dense(256), BatchNorm, Dropout(0.3) e Softmax.
* **Fase 1 (Features)**: Base VGG16 congelada; treino da cabeça de classificação por 50 épocas (Adam, `lr=0.0002`).
* **Fase 2 (Fine-tuning)**: Descongelamos as últimas 4 camadas convolucionais da base VGG16. Refinamos os pesos com taxa ultra-baixa de aprendizado (`lr=1e-5`) limitados a **15 épocas** para evitar o esquecimento catastrófico dos filtros originais.

---

## 🏆 4. Critério Clínico de Seleção do Modelo Vencedor

Na avaliação final no conjunto de teste, as métricas globais indicavam a CNN Simples como vencedora por causa de sua alta acurácia global (~92%). No entanto, a análise clínica e a **Matriz de Confusão** revelaram que:
* O modelo **VGG16 Transfer Learning** aprendeu de fato os padrões clínicos, apresentando sensibilidade real e distribuída nas três classes.
* A **CNN Simples** atuou como um classificador dummy: sensibilidade de **0.00%** para *Cardiomegaly* e **0.00%** para *Effusion* (apenas chutando *No Finding*).
* **Restrições de Tempo no Treino**: Devido a bloqueios de tempo e limitações de processamento no ambiente de execução, a rede CNN Simples acabou sendo treinada de forma muito resumida (apenas cerca de 20 épocas ou interrompida precocemente), impedindo que seus pesos convergissem de forma adequada. O ideal para uma rede iniciada do zero seria fornecer mais tempo e épocas de treino para que ela de fato aprendesse a mapear as características espaciais complexas, porém o tempo de treinamento estava se estendendo excessivamente, o que comprometeria a data limite de entrega do projeto.

Por conta disso, o modelo **VGG16 Transfer Learning** foi eleito o campeão absoluto para alimentar o protótipo médico.

---

## 🖥️ 5. Execução Local e Upload Fallback
Configuramos a Célula 36 para agir de forma híbrida:
* **No Colab**: Abre a janela de upload interativa padrão do navegador.
* **Em Execução Local**: Varre automaticamente a pasta física `visao_computacional/image/`, processando e diagnosticando sequencialmente todas as radiografias encontradas.
