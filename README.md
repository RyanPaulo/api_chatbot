Com certeza! Fiz todos os ajustes que você orientou, corrigi os erros de numeração e estrutura, e melhorei a clareza das explicações. O resultado é um `README.md` muito mais completo e profissional.

Aqui está a versão final e corrigida do arquivo, pronta para ser copiada e colada no seu projeto.

```markdown
# Chatbot de Conformidade Ambiental

## Objetivo do Projeto

Este projeto tem como objetivo principal desenvolver uma solução tecnológica para simplificar e democratizar o acesso a dados públicos sobre fiscalização e regulamentação ambiental no Brasil. Através de um chatbot integrado ao Telegram, chamado "Conformidade Ambiental", buscamos resolver o problema da fragmentação e da complexidade das informações governamentais.

O sistema funciona como uma ponte inteligente entre as bases de dados abertas do IBAMA e o usuário final (cidadãos, empresas, pesquisadores), permitindo a realização de consultas em linguagem natural e recebendo respostas claras, contextualizadas e de fácil compreensão.

A arquitetura é baseada em microsserviços, composta por três componentes principais:

1.  **API (FastAPI):** É o coração do sistema, um serviço de backend que centraliza a lógica de acesso aos dados.
    *   **Endpoints de Consulta:** A API expõe endpoints seguros (rotas) que o chatbot utiliza para solicitar informações específicas, como "consultar CNPJ" ou "buscar infrações por município". Isso desacopla a lógica do chatbot da fonte de dados.
    *   **Processo de ETL:** A API também contém scripts de ETL (Extração, Transformação e Carga) responsáveis por buscar os dados brutos diretamente do Portal de Dados Abertos do IBAMA, limpá-los, padronizá-los e carregá-los em nosso banco de dados.

2.  **Chatbot (Rasa):** É a interface conversacional que interpreta as perguntas do usuário, gerencia o diálogo e consome os dados fornecidos pela API para formular as respostas.

3.  **Supabase (PostgreSQL):** Utilizamos o Supabase como nossa plataforma de banco de dados. Ele armazena de forma segura e persistente todos os dados que foram extraídos do IBAMA pelo processo de ETL. Isso garante que as consultas do chatbot sejam extremamente rápidas e não dependam da disponibilidade do site do IBAMA em tempo real.

## Guia de Instalação e Execução Local

Para executar o projeto, é necessário configurar e rodar os dois serviços (API e Chatbot) de forma independente, em terminais separados.

**Pré-requisitos:**
*   Python 3.10 ou superior.

---

### Parte 1: Configuração e Execução da API (FastAPI)

Siga estes passos dentro do diretório `api_chatbot/`.

**1. Acesse o diretório da API:**
```shell
cd api_chatbot
```

**2. Crie um ambiente virtual:**
```shell
# No macOS/Linux
python3 -m venv .venv_api

# No Windows
python -m venv .venv_api
```

**3. Ative o ambiente virtual:**
```shell
# No macOS/Linux
source .venv_api/bin/activate

# No Windows
.\.venv_api\Scripts\activate
```

**4. Instale as bibliotecas necessárias:**
```shell
pip install -r requirements.txt
```

**5. Execute o servidor da API:**
> **Importante:** Antes de executar, certifique-se de que o arquivo `.env` na raiz do diretório `api_chatbot/` está preenchido com as credenciais do seu banco de dados Supabase.

O servidor da API deve rodar na porta `8000` para que o Rasa possa se conectar localmente.
```shell
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```
> Deixe este terminal aberto. O servidor da API está ativo.

---

### Parte 2: Configuração e Execução do Chatbot (Rasa)

Abra um **novo terminal** e siga estes passos dentro do diretório `chatbot_rasa/`.

**1. Acesse o diretório do Chatbot:**
```shell
cd chatbot_rasa
```

**2. Crie um ambiente virtual:**
```shell
# No macOS/Linux
python3 -m venv .venv_rasa

# No Windows
python -m venv .venv_rasa
```

**3. Ative o ambiente virtual:**
```shell
# No macOS/Linux
source .venv_rasa/bin/activate

# No Windows
.\.venv_rasa\Scripts\activate
```

**4. Instale as bibliotecas necessárias:**
```shell
pip install -r requirements.txt
```
Para verificar se o Rasa foi instalado com sucesso, você pode rodar:
```shell
rasa --version
```

**5. Treine o modelo do Rasa:**
Este comando lê seus arquivos de treinamento (`data/`) e gera um novo modelo em `models/`.
```shell
rasa train
```

**6. Execute o servidor de ações (Actions Server):**
> Abra um **terceiro terminal**, ative o ambiente `.venv_rasa` nele e execute o comando abaixo. Este servidor executa o código Python customizado que se conecta à sua API.
```shell
rasa run actions
```
> Deixe este terminal aberto.

**7. Teste o chatbot no terminal:**
> Voltando ao **segundo terminal** (onde você treinou o modelo), você pode conversar com o bot para testes rápidos.
```shell
rasa shell
```

**8. Execute o servidor principal para conexão externa (Ex: Telegram):**
> Para conectar ao Telegram, use este comando no **segundo terminal** (em vez do `rasa shell`).

**Importante:** Antes de executar, edite o arquivo `credentials.yml` com seu token do Telegram e o `endpoints.yml` com a URL do webhook gerada por uma ferramenta como o `ngrok`.
```shell
rasa run -m models --enable-api --cors "*" --credentials credentials.yml
```
```