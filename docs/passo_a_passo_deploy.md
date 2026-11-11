# Guia Passo a Passo de Deploy — CardioIA (Fase 7)

Siga exatamente a ordem abaixo (**GitHub → Render → Vercel → Expo EAS Build → Wokwi**), pois a Vercel, o Mobile e o Wokwi precisam da URL pública do Backend gerada pelo Render.

---

## Etapa 0 — Subir o Código para o GitHub (Repositório Privado)

1. No seu terminal local (PowerShell, Git Bash ou WSL), na raiz `D:\FIAP\CardioIA`:
   ```bash
   # Caso apareça erro de "dubious ownership" no Windows:
   git config --global --add safe.directory D:/FIAP/CardioIA

   # Instale o package-lock atualizado do frontend (opcional, mas recomendado):
   cd frontend && npm install && cd ..

   git status
   git add .
   git commit -m "feat(fase7): plataforma integrada backend fastapi, web, mobile expo e micropython"
   git push origin main
   ```
2. No GitHub, vá em **Settings → Collaborators** do repositório, confirme que ele está **Private** e adicione o usuário do tutor conforme solicitado no enunciado.

---

## Etapa 1 — Deploy do Backend Integrador Python no Render

O arquivo [`render.yaml`](../render.yaml) na raiz já automatiza toda a configuração (Blueprint).

### Opção A — Automática via Blueprint (`render.yaml`)
1. Crie uma conta ou faça login em [https://dashboard.render.com/](https://dashboard.render.com/) (conecte sua conta GitHub).
2. No topo, clique em **New +** → **Blueprint**.
3. Selecione o repositório `CardioIA` e clique em **Connect**.
4. Dê um nome ao Blueprint (ex.: `cardioia`) e clique em **Apply**.
5. O Render criará o serviço `cardioia-backend`, instalará `backend/requirements.txt`, executará `python backend/bootstrap_model.py` (que treina e salva o modelo `.joblib` da Fase 6 no container) e subirá o FastAPI.

### Opção B — Manual via Web Service (caso prefira configurar na tela)
1. Clique em **New +** → **Web Service** → selecione o repositório `CardioIA`.
2. Preencha:
   - **Name:** `cardioia-backend`
   - **Region:** Oregon (US West) ou Ohio
   - **Branch:** `main`
   - **Root Directory:** *(deixe em branco! O backend precisa acessar `fase_6/` e `api/`)*
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r backend/requirements.txt && python backend/bootstrap_model.py
     ```
   - **Start Command:**
     ```bash
     uvicorn cardioia.main:app --host 0.0.0.0 --port $PORT --app-dir backend
     ```
   - **Instance Type:** `Free`
3. Em **Environment Variables**, adicione:
   | Key | Value |
   | :--- | :--- |
   | `PYTHON_VERSION` | `3.11.9` |
   | `JWT_SECRET` | `um-segredo-forte-qualquer-123456` |
   | `DEVICE_TOKEN` | `cardioia-device-demo-token` |
   | `MEDICO_PASSWORD` | `cardio123` |
   | `PACIENTE_PASSWORD` | `cardio123` |
   | `CORS_ORIGINS` | `*` |
   | `GEMINI_API_KEY` | *(opcional — sua chave do Google AI Studio, se quiser síntese por LLM)* |
4. Clique em **Create Web Service**.

### Como validar o Backend no Render
- Quando o status ficar **Live**, copie a URL gerada (ex.: `https://cardioia-backend-ewbv.onrender.com`).
- Abra no navegador:
  - `https://SUA-URL.onrender.com/health` → deve retornar `{"status":"ok","ml_fase6":true,...}`
  - `https://SUA-URL.onrender.com/docs` → abre o Swagger interativo da API.

---

## Etapa 2 — Deploy da Aplicação Web (React + Vite) na Vercel com CI/CD

1. Acesse [https://vercel.com/new](https://vercel.com/new) e faça login com o GitHub.
2. Em **Import Git Repository**, clique em **Import** ao lado do repositório `CardioIA`.
3. Na tela **Configure Project**:
   - **Project Name:** `cardioia` (ou similar)
   - **Framework Preset:** `Vite`
   - **Root Directory:** clique em **Edit** e selecione a pasta `frontend` *(o arquivo [`frontend/vercel.json`](../frontend/vercel.json) já está dentro dela configurado com rewrite SPA)*.
4. Abra a seção **Environment Variables** e adicione:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://SUA-URL-DO-RENDER.onrender.com` *(sem barra `/` no final!)*
5. Clique em **Deploy**.

### Como validar a Web + CI/CD na Vercel
1. Ao terminar o build (cerca de 40 segundos), clique na URL pública gerada (ex.: `https://cardioia.vercel.app`).
2. Faça login com `medico` / `cardio123`, clique nos botões **Simular leitura: Normal / Atenção / Crítico** no topo e verifique os cards, o gráfico e os protocolos mudando em tempo real.
3. Acesse diretamente `https://SUA-URL.vercel.app/dashboard` e dê **F5 (refresh)** no navegador — a página deve abrir sem erro 404 (isso comprova que o `vercel.json` está roteando a SPA corretamente).
4. **Tire um print** do painel da Vercel mostrando o deploy **Ready** e o vínculo com o GitHub (CI/CD ativo) para colocar no `README.md`.

---

## Etapa 3 — Build do Aplicativo Mobile (`.apk`) no Expo EAS Build

Os arquivos obrigatórios [`mobile/app.json`](../mobile/app.json) (`android.package = "br.com.fiap.cardioia"`) e [`mobile/eas.json`](../mobile/eas.json) (perfil `preview` gerando `apk`) já estão prontos.

1. Crie uma conta gratuita em [https://expo.dev/signup](https://expo.dev/signup).
2. Se a URL do seu Render for diferente de `https://cardioia-backend-ewbv.onrender.com`, atualize o valor de `EXPO_PUBLIC_API_URL` em [`mobile/eas.json`](../mobile/eas.json) e `extra.apiUrl` em [`mobile/app.json`](../mobile/app.json).
3. No terminal local, entre na pasta `mobile/`:
   ```bash
   cd D:\FIAP\CardioIA\mobile

   # 1. Instalar dependências do projeto mobile
   npm install

   # 2. Instalar o EAS CLI globalmente (ou usar npx eas-cli)
   npm install -g eas-cli

   # 3. Autenticar na sua conta Expo
   eas login

   # 4. Vincular o projeto à sua conta Expo (responda "Y" para criar o projeto @seu-usuario/cardioia)
   # IMPORTANTE: antes de rodar `eas init`, remova ou deixe o eas substituir o placeholder de projectId em app.json:
   eas project:init
   ```
   > **Dica:** Caso o `eas project:init` reclame do valor `"SUBSTITUA_PELO_PROJECT_ID_APOS_EAS_INIT"` no `mobile/app.json`, basta apagar o bloco `"eas": { "projectId": "..." }` dentro de `"extra"` no `mobile/app.json` antes de rodar `eas project:init`, e o comando preencherá o UUID automaticamente.

4. Disparar o build do `.apk` na nuvem do Expo:
   ```bash
   eas build --platform android --profile preview
   ```
   - Quando perguntar *"Generate a new Android Keystore?"*, responda **Yes (`Y`)**.
5. O terminal mostrará um link para acompanhar o build no painel do Expo (`https://expo.dev/accounts/.../projects/cardioia/builds/...`).
6. Quando o build terminar (cerca de 5 a 10 minutos na fila gratuita):
   - O painel do Expo exibirá o botão **Download** (`.apk`) e um **QR Code**.
   - **Tire um print** dessa tela do Expo Dashboard.
   - Escaneie o QR Code com seu celular Android, instale o `.apk`, faça login (`medico` / `cardio123`) e **tire um print** do app rodando no celular.

---

## Etapa 4 — Simulação do Hardware em MicroPython no Wokwi

1. Acesse [https://wokwi.com/projects/new/micropython-esp32](https://wokwi.com/projects/new/micropython-esp32) (faça login para poder salvar link público).
2. Na aba **`main.py`**:
   - Copie todo o conteúdo de [`iot/micropython/main.py`](../iot/micropython/main.py) e cole no editor.
   - Na **linha 36**, confira se `BACKEND_URL` está com a URL exata do seu serviço no Render (sem `/` no final):
     ```python
     BACKEND_URL = "https://SUA-URL-DO-RENDER.onrender.com"
     ```
3. Clique na setinha ao lado das abas do editor → **New File...** → digite **`ssd1306.py`**:
   - Copie todo o conteúdo de [`iot/micropython/ssd1306.py`](../iot/micropython/ssd1306.py) e cole nessa aba.
4. Na aba **`diagram.json`**:
   - Substitua todo o conteúdo pelo de [`iot/micropython/diagram.json`](../iot/micropython/diagram.json).
5. Clique no botão verde **▶ Start the simulation**:
   - No Serial Monitor aparecerá: `[WiFi] Conectado!`, seguido de `[EDGE] FC=... SpO2=...` e `[IA] Backend: ...`.
   - O display OLED mostrará os 4 sinais vitais, o status `Edge` e a probabilidade do modelo `IA`.
   - Clique nos 3 potenciômetros (**FC**, **SpO2**, **PA sist.**) e no sensor **DHT22** durante a simulação para alterar os valores e ver o LED vermelho/buzzer acionando e o site da Vercel / App Mobile atualizando após ~3 segundos.
6. Clique em **Save** (no topo) e depois em **Share** → copie o **link público do projeto Wokwi**.

---

## Etapa 5 — Fechamento dos Entregáveis Finais

1. Coloque os prints salvos na pasta `assets/` e atualize a tabela de links no topo do [`README.md`](../README.md) com:
   - URL pública da Vercel
   - URL pública do Render
   - Link público do build `.apk` no Expo Dashboard
   - Link público da simulação no Wokwi
   - Link do vídeo no YouTube (grave seguindo [`docs/roteiro_video_fase7.md`](roteiro_video_fase7.md))
2. Exporte o relatório [`docs/relatorio_tecnico_fase7.md`](relatorio_tecnico_fase7.md) para PDF (no VS Code: extensão *Markdown PDF* ou abrindo o preview e imprimindo como PDF).
3. Faça o `git commit` e `git push origin main` final (a Vercel fará o deploy automático dessa última atualização via CI/CD).
