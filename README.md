# Chatbot de Conformidade Ambiental

## Objetivo do Projeto

Este projeto tem como objetivo principal desenvolver uma solução tecnológica para simplificar e democratizar o acesso a dados públicos sobre fiscalização e regulamentação ambiental no Brasil. Através de um chatbot integrado ao Telegram, chamado "Conformidade Ambiental", buscamos resolver o problema da fragmentação e da complexidade das informações governamentais.

O sistema funciona como uma ponte inteligente entre as bases de dados abertas do IBAMA e o usuário final (cidadãos, empresas, pesquisadores), permitindo a realização de consultas em linguagem natural e recebendo respostas claras, contextualizadas e de fácil compreensão.

A arquitetura é baseada em microsserviços, composta por dois componentes principais:
1.  **API (FastAPI):** Um serviço de backend que centraliza, processa e armazena os dados ambientais, expondo-os de forma segura e otimizada.
        # < AQUI SEPARE EM DOIS TOPICO, UM FALANDO DOS 'ENDPOINTS' PARA CUNSULTAS E O OUTRO FALANDO DOS 'ETL' QUE ESTAMOS USANDO PARA ESTRAIR O DADOS DA API DO IBAMA>
2.  **Chatbot (Rasa):** A interface conversacional que interpreta as perguntas do usuário, gerencia o diálogo e consome os dados fornecidos pela API para formular as respostas.
3.  **Supabase :** <AQUI QUERO QUE EXPLIQUE QUE ESTA SENDO USADO O SUPABASE PARA ARMAZENA COM SEGURANÇA OS DADOS ESTRAIDO DO 'IBAMA'>

## Guia de Instalação e Execução Local

Para executar o projeto, é necessário configurar e rodar os dois serviços (API e Chatbot) de forma independente, em terminais separados.

**Pré-requisitos:**
*   Python 3.10.18.

---

### Parte 1: Configuração do Ambiente da API (FastAPI)

Siga estes passos dentro do diretório `api_chatbot/`.
* ...\Conformidade_Ambiental_Projeto\api_chatbot

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

**4. Instale todas as bibliotecas necessárias:**
```shell
pip install -r requirements.txt
```


**5. Execute o servidor da APi:**
###### Para que o rasa se conecte com a api deve esta na porta 8000, localmente.
###### Antes de execurtar o servidor da API, deve-se editar o arquivo '.env' com os tokens do banco de dasdo

```shell
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```



---

### Parte 2: Configuração do Ambiente da API (FastAPI)

Siga estes passos dentro do diretório `chatbot_rasa/`.
* ...\Conformidade_Ambiental_Projeto\chatbot_rasa

**1. Acesse o diretório da API:**
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

**4. Instale todas as bibliotecas necessárias:**
```shell
pip install -r requirements.txt

# Para testar se a biblioteca rasa  foi instalado com sucesso
rasa --version
```

**5. Treinar o bot rasa:**
```shell
rasa train
```

**7. Executar o servidor principal do rasa:**
```shell
rasa run actions
```

**8. Executar o chatbot no terminal :**

###### *rasa shell* : Nos ajuda a testar as respostas que esta sendo gerada antes de por em produção e de forma rapida.

```shell
rasa shell
```

**8. Executar o servidor de conexao externa (Telegram) :**

###### Deve-se editar as credenciais para conexao com telegram no arquivo *credentials.yml
* access_token: 'TOKEN DO PERFIL TELEGRAM'
* access_token:'NOME DO SEU CHATBOT'
* webhook_url: 'URL WEBHOOK PARA O TUNEL ENTRE O SERVIDOR RASA COM O TELEGRAM'

```shell
rasa run -m models --enable-api --cors "*" --credentials credentials.yml
```