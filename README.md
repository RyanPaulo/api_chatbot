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

Siga estes passos dentro do diretório `api_fastapi/`.

**1. Acesse o diretório da API:**
```shell
cd api_chatbot
'''

**2. Acesse o diretório da API:**
```shell
# No macOS/Linux
python3 -m venv .venv

# No Windows
python -m venv .venv
'''






