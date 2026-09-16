# CardioIA - Roteiro para Vídeo Demonstrativo (Até 3 Minutos)

Este documento apresenta o roteiro sugerido para a gravação do vídeo de até 3 minutos exigido na entrega da **Fase 5**.

---

## ⏱️ Cronograma de Gravação (3 Minutos)

| Tempo | Seção | O que mostrar na tela | O que falar (Narrativa) |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:30** | **1. Introdução & Contexto** | Interface Web do CardioIA aberta no navegador com o logo e status online. | *"Olá! Neste vídeo apresentamos o Assistente Conversacional Inteligente do CardioIA, correspondente à Fase 5 do projeto. Nosso objetivo foi construir um chatbot capaz de interagir em linguagem natural com o paciente, auxiliando na triagem inicial de queixas cardiológicas e oferecendo orientações preventivas baseadas em diretrizes clínicas."* |
| **0:30 - 1:15** | **2. Arquitetura & Watson Assistant** | Mostrar rapidamente o arquivo JSON `cardioia_watson_assistant.json` e o backend Flask no editor de código. | *"Modelamos o assistente com base no IBM Watson Assistant, definindo intents como saudações, relato de sintomas, dados vitais e emergência médica, além de entidades clínicas como dores, dispneia e fatores de risco. O backend foi desenvolvido em Python com Flask, integrando a API do Watson com um motor local resiliente."* |
| **1:15 - 2:20** | **3. Demonstração Prática da Interação** | Interagir ao vivo na interface do Chatbot: <br>1. Clicar em boas-vindas/chips de atalho.<br>2. Enviar queixa de sinais vitais (*"Minha pressão deu 15 por 9"*).<br>3. Enviar relato de emergência (*"Estou sentindo dor forte no peito irradiando para o braço esquerdo"*). | *"Vamos à demonstração prática: ao iniciar, o assistente traz o disclaimer ético e botões de atalho rápido. Ao enviarmos uma medida de pressão arterial, o assistente analisa e contextualiza segundo as Diretrizes Brasileiras de Hipertensão. Em seguida, ao simularmos um relato de dor torácica irradiada, o assistente dispara imediatamente o alerta de emergência médica, recomendando contato urgente com o SAMU 192 e atualizando o badge de risco para Emergência."* |
| **2:20 - 2:50** | **4. Prevenção e Fallback** | 1. Perguntar sobre prevenção (*"Como prevenir infarto?"*).<br>2. Digitar mensagem fora de contexto (*"Qual a cotação do dólar?"*) para testar o fallback. | *"O assistente também atua como educador em saúde, orientando sobre dieta cardioprotetora e hábitos saudáveis. Caso o paciente envie algo fora do contexto, o assistente ativa o tratamento de exceções (fallback), orientando cordialmente os temas atendidos."* |
| **2:50 - 3:00** | **5. Conclusão & Encerramento** | Mostrar a suite de testes passando no terminal (`pytest tests/ -v`). | *"Todos os testes unitários e de integração foram validados com 100% de sucesso. Muito obrigado!"* |

---

## 💡 Dicas para a Gravação
- **Resolução:** Grave em 1080p com áudio claro.
- **Ambiente:** Deixe o servidor rodando previamente com `python app.py` na pasta `api`.
- **Acesso:** Abra o navegador em `http://localhost:5000` em tela cheia.
