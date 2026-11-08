Enunciado da Atividade:

Após percorrer as fronteiras da coleta de dados (Fase 1), diagnóstico automatizado (Fase 2), monitoramento IoT (Fase 3), análise de imagens (Fase 4), assistência conversacional (Fase 5) e, recentemente, a orquestração de sistemas preditivos multiagentes (Fase 6), a Fase 7 marca o ápice da CardioIA como uma Plataforma de Inteligência Cardíaca Total.

Nesta etapa, o foco deixa de ser o desenvolvimento de módulos isolados e passa a ser a integração transdisciplinar e a materialização da solução. O desafio estratégico é converter a inteligência preditiva e analítica construída na fase anterior em um produto digital funcional, seguro e centrado no usuário. Se na Fase 6 o objetivo era o “Cérebro” da CardioIA (previsão de picos de risco), na Fase 7 o objetivo é o “Corpo” da solução: a interface que conecta o médico e o paciente aos insights de IA em tempo real.

A proposta exige que a equipe realize a integração de todos os módulos back-end, front-end, serviços em nuvem, LLMs e sensores em uma única arquitetura funcional. Isso inclui o deploy profissional da aplicação Web, por exemplo, na Vercel ou Render, Netlify, Cloudflare Pages, Firebase Hosting etc. e a distribuição mobile via Expo EAS Build ou outra plataforma de seu interesse, garantindo acessibilidade e usabilidade. Claro que você pode adotar outras formas de deploy. Além disso, avançamos na infraestrutura de hardware, migrando a lógica de microcontroladores para MicroPython, permitindo o uso de dispositivos mais poderosos e flexíveis, como o Raspberry Pi, para processar diagnósticos localmente. É o momento de apresentar a arquitetura final da solução, demonstrando como a IA revoluciona a Cardiologia através de um ecossistema coeso, tecnológico e voltado à salvaguarda de vidas.

Objetivo geral dessa atividade:

Desenvolver o MVP final e funcional da plataforma CardioIA, sendo capaz de:

Realizar o deploy completo da aplicação: Web (em alguma plataforma) com CI/CD ativo e Mobile (arquivo .apk via EAS Build).
Refinar a Experiência do Usuário (UX), focando na usabilidade e no fluxo de informação dos indicadores de risco.
Integrar todos os módulos técnicos desenvolvidos nas fases anteriores em uma única plataforma orquestrada por Python.
Evoluir o hardware, simulando o uso de MicroPython em microcontroladores de alto desempenho.
Trabalho em equipe e colaboração interdisciplinar, recomendamos o desenvolvimento do projeto em grupo de 4 a 5 integrantes, estimulando habilidades de comunicação, cooperação e divisão equilibrada de tarefas. O trabalho em equipe é considerado uma soft skill essencial para o ambiente profissional e acadêmico, e será concedido 1 ponto extra para as equipes que se organizarem dentro dessa estrutura recomendada.
Ao final desta fase, a equipe terá desenvolvido uma solução prática que demonstra como agentes conversacionais podem ser aplicados em contextos de saúde digital, respeitando boas práticas técnicas e conceituais.


Atividade detalhada:

PARTE 1 – Deploy e Distribuição Profissional (Front-End & Mobile)

Utilizando as aplicações desenvolvidas, o grupo deve:

Web: publicar a aplicação na Vercel, configurando o vercel.json para suporte a rotas SPA e garantindo que cada push no GitHub inicie um deploy automático (CI/CD).
Mobile: configurar o app.json e eas.json para realizar o build na nuvem do Expo, gerando um arquivo .apk funcional.
Validação: testar a aplicação Web e instalar o .apk em um dispositivo real, validando o fluxo de login e visualização dos dados cardíacos.
  

Entregáveis:

Repositório GitHub: deve ser privado, porém compartilhado com o tutor e conter o código-fonte completo da aplicação Web (React+Vite) e Mobile (React Native+Expo).
Arquivos obrigatórios: vercel.json configurado para rotas SPA; app.json com android.package em formato de domínio invertido; e eas.json com o perfil preview para geração de APK.
README.md: deve conter a URL pública da Vercel, o link direto para o build do .apk no dashboard do Expo (ou QR Code), prints comprobatórios do deploy concluído e instruções de instalação.
  

PARTE 2 – Integração do Ecossistema e Arquitetura Final

A equipe deverá construir o núcleo integrador da CardioIA utilizando Python, garantindo os seguintes requisitos técnicos:

Back-end Integrador: desenvolver um serviço em Python que conecte as interfaces (Front-end) aos motores de IA (Modelos Preditivos da Fase 6 e LLMs da Fase 5).
Transição para MicroPython: converter a lógica de captura e processamento de sensores (temperatura, batimentos simulados) de C/C++ para MicroPython, simulando a execução em dispositivos como ESP32 ou Raspberry Pi no ambiente Wokwi.
Arquitetura Final: consolidar o fluxo de dados em um ecossistema funcional que suporte o recebimento de sinais e a entrega de recomendações clínicas em tempo real.
  

Entregáveis:

Código-Fonte Integrado (GitHub): deve ser privado, porém compartilhado com o tutor, incluindo a pasta de Backend contendo os scripts Python de integração e a pasta IoT contendo o script .py para MicroPython.
Projeto Wokwi: link público da simulação em MicroPython demonstrando a análise de sinais e feedback visual (LED/OLED).
  

Relatório Técnico (PDF – Máximo de cinco páginas):

Diagrama de Arquitetura Final: desenho técnico detalhando o fluxo: Sensor → MicroPython → Backend Python → APIs de IA → UI.
Vídeo Demonstrativo (até 5 minutos): demonstração do fluxo fim-a-fim, desde o hardware (Wokwi) até a atualização do dado na URL pública da Vercel/APK.