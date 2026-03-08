# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Nome do projeto

## Nome do grupo

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do integrante 1</a>

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do Tutor</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do Coordenador</a>


## 📜 Descrição

*Descreva seu projeto com base no texto do PBL (até 600 palavras)*

## Documentos usados

### Resumo das Obras Selecionadas
Selecionamos cinco obras fundamentais que cruzam a história da medicina, a saúde pública brasileira e o estado da arte em tecnologia. O objetivo é fornecer uma base textual rica e diversificada para o processamento de linguagem natural.

1. **Plano DANT (Gov. BR 2021-2030):** Documento estratégico que mapeia o enfrentamento de doenças crônicas no Brasil. Fornece o contexto epidemiológico e as metas de saúde pública para a próxima década.
2. **Cases of Organic Diseases of the Heart (John Collins Warren):** Obra histórica que apresenta relatos de casos clínicos reais do século XIX. Essencial para análise de descrição de sintomas em linguagem natural.
3. **Diretrizes Brasileiras de Hipertensão Arterial (2020):** O padrão para o diagnóstico e tratamento no Brasil. Contém terminologia técnica precisa, valores de referência e protocolos clínicos modernos.
4. **Impacto da Inteligência Artificial na Cardiologia:** Artigo científico que discute como algoritmos já estão transformando o setor, servindo como base teórica e técnica para o desenvolvimento do ecossistema CardioIA.
5. **William Harvey and the Discovery of the Circulation of the Blood (Huxley):** Texto biográfico e técnico sobre a descoberta da circulação. Oferece uma perspectiva sobre a fisiologia fundamental do sistema cardiovascular.

#### Referências
1. **Plano DANT (Gov. BR 2021-2030):** [https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/svsa/doencas-cronicas-nao-transmissiveis-dcnt/09-plano-de-dant-2022_2030.pdf/view](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/svsa/doencas-cronicas-nao-transmissiveis-dcnt/09-plano-de-dant-2022_2030.pdf/view)
2. **Cases of Organic Diseases of the Heart (John Collins Warren):** [https://www.gutenberg.org/ebooks/26836](https://www.gutenberg.org/ebooks/26836)
3. **Diretrizes Brasileiras de Hipertensão Arterial (2020):** [https://www.scielo.br/j/abc/a/Z6m5gGNQCvrW3WLV7csqbqh/?lang=pt](https://www.scielo.br/j/abc/a/Z6m5gGNQCvrW3WLV7csqbqh/?lang=pt)
4. **Impacto da Inteligência Artificial na Cardiologia:** [https://www.scielo.br/j/abc/a/VNQtkGdM85HdjCXKJ6ZgXkQ/?lang=pt](https://www.scielo.br/j/abc/a/VNQtkGdM85HdjCXKJ6ZgXkQ/?lang=pt)
5. **William Harvey and the Discovery of the Circulation of the Blood (Huxley):** [https://www.gutenberg.org/ebooks/2939](https://www.gutenberg.org/ebooks/2939)

---

### Justificativa para o Uso de NLP

A integração desses textos no CardioIA não é apenas documental; eles servem como insumos para três frentes principais de Inteligência Artificial:

* **Extração de Entidades Nomeadas (NER):** Através dos textos de Warren e das Diretrizes de 2020, o modelo pode aprender a identificar e extrair termos médicos específicos (como "isquemia", "pressão sistólica", "hipertrofia ventricular") em prontuários não estruturados, automatizando a triagem de dados.
* **Análise de Sentimento e Semântica em Saúde:** O Plano DANT permite analisar o "tom" das políticas públicas e a urgência de certas patologias, enquanto os relatos de casos históricos ajudam a entender a evolução da descrição da dor e do desconforto pelo paciente.
* **Sumarização e Classificação Automática:** Com artigos densos como o de "Impacto da IA", podemos treinar modelos para gerar resumos executivos para médicos ou classificar automaticamente novos artigos científicos que entrem na base de dados do hospital, mantendo o ecossistema sempre atualizado.

--

### Papel no Projeto CardioIA

Estes dados textuais formam o "cérebro interpretativo" da plataforma. Enquanto os dados numéricos dizem *o que* está acontecendo agora, e as imagens mostram *onde* está o problema, o processamento destes textos permite ao CardioIA entender o contexto clínico, histórico e normativo, garantindo que as decisões da IA estejam alinhadas com as diretrizes médicas vigentes e com a compreensão humana da doença.

---



## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- <b>.github</b>: Nesta pasta ficarão os arquivos de configuração específicos do GitHub que ajudam a gerenciar e automatizar processos no repositório.

- <b>assets</b>: aqui estão os arquivos relacionados a elementos não-estruturados deste repositório, como imagens.

- <b>docs</b>: Artigos, citações, documentos e livros relacioados ao projeto que serão usados para treinamento e refinamento de algoritmos de ML e IA.

- <b>README.md</b>: arquivo que serve como guia e explicação geral sobre o projeto (o mesmo que você está lendo agora).


## 🗃 Histórico de lançamentos

* 0.1.0 - 10/03/2026
    * Estruturação do projeto
    * Obtenção dos dados


## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>


