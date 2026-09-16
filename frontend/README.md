# CardioIA - Frontend (React + Vite)

Esta pasta contém a aplicação Web interativa do **Assistente Conversacional CardioIA** desenvolvida em **React** (utilizando Vite e Lucide Icons).

---

## 🎨 Funcionalidades da Interface

- **Chat Conversacional em Tempo Real:** Balões de mensagem para o usuário e o assistente, com suporte a formatação, quebras de linha e destaques em negrito.
- **Chips de Ação Rápida (Quick Replies):** Botões para envio imediato de queixas comuns (*"🚨 Dor no Peito / Urgência"*, *"🩺 Relatar Sintomas"*, *"📊 Informar Pressão"*, *"💡 Prevenção"* e *"ℹ️ Sobre o CardioIA"*).
- **Badge Dinâmico de Risco:** Indicador visual de gravidade baseado na triagem clínica (*Baixo Risco*, *Moderado*, *Alto Risco*, *🚨 Emergência*).
- **Indicador de Digitação:** Animação pulsante indicando que o assistente está processando a resposta.
- **Gerenciamento de Sessão:** Botão para limpar a tela e reiniciar a conversa.
- **Design Responsivo & Acessível:** Interface moderna ajustada para celulares e desktop.

---

## 🚀 Como Executar

### Modo de Desenvolvimento (Vite Dev Server)

Certifique-se de que o backend Flask esteja rodando na porta 5000 (`cd api && python app.py`).

Em seguida, inicie o servidor de desenvolvimento do React:

```bash
cd frontend
npm install
npm run dev
```

Acesse no navegador: **`http://localhost:3000`**

O Vite está configurado com proxy automático para redirecionar as chamadas `/api/*` diretamente para o Flask em `http://localhost:5000`.

---

### Modo de Produção (Build)

Para gerar os arquivos estáticos de produção:

```bash
cd frontend
npm run build
```

Os arquivos compilados serão gerados em `frontend/dist/` e podem ser servidos diretamente pelo backend Flask na rota `http://localhost:5000/react`.
