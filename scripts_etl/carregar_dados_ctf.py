# api_chatbot/scripts_etl/carregar_dados_ctf.py

import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import time
import numpy as np


# --- 1. CONFIGURAÇÃO E CONEXÃO ---

def setup_supabase_client() -> Client:
    """
    Carrega as variáveis de ambiente e inicializa o cliente Supabase.
    """
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')

    print(f"Procurando arquivo .env em: {os.path.abspath(dotenv_path)}")
    load_dotenv(dotenv_path=dotenv_path)

    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise Exception("ERRO: As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não foram definidas.")

    print("Credenciais do Supabase carregadas com sucesso.")
    return create_client(supabase_url, supabase_key)


# --- Variáveis de Configuração ---

# ATENÇÃO: Renomeie seu arquivo local para 'cadastro_ctf.csv' ou ajuste o nome aqui
NOME_ARQUIVO_LOCAL = "pessoasJuridicas.csv"  # Ajustado para o nome que você está usando
CAMINHO_ARQUIVO_LOCAL = os.path.join(os.path.dirname(__file__), '..', 'dados_locais', NOME_ARQUIVO_LOCAL)
NOME_TABELA = "cadastro_tecnico_federal"


def carregar_dados(supabase: Client):
    """
    Função principal que executa o processo de ETL para os dados do CTF/APP a partir de um arquivo local.
    """
    print("\n--- INICIANDO PROCESSO DE ETL (CADASTRO TÉCNICO FEDERAL - LOCAL) ---")

    # --- 2. EXTRAÇÃO (Extraction) ---
    print(f"1. Lendo o arquivo CSV local de: {CAMINHO_ARQUIVO_LOCAL}")
    try:
        # ==================================================================
        # CORREÇÃO PRINCIPAL: Alterando o separador para ponto e vírgula
        # ==================================================================
        df = pd.read_csv(CAMINHO_ARQUIVO_LOCAL, sep=';', encoding='utf-8', on_bad_lines='skip', low_memory=False)
        print("   - Arquivo lido com sucesso.")
    except FileNotFoundError:
        print(f"   - ERRO CRÍTICO: Arquivo '{NOME_ARQUIVO_LOCAL}' não encontrado na pasta 'dados_locais'.")
        return
    except Exception as e:
        print(f"   - ERRO CRÍTICO ao ler o arquivo: {e}")
        return

    # --- 3. TRANSFORMAÇÃO (Transformation) ---
    print("2. Transformando os dados...")

    # Mapeamento das colunas do CSV para as colunas do nosso banco de dados
    # ATENÇÃO: Os nomes das colunas no arquivo são diferentes do Google Sheets
    mapa_colunas = {
        'CNPJ': 'cnpj',
        'Razão Social': 'razao_social',
        'Situação cadastral': 'situacao_cadastro',  # 'c' minúsculo
        'Última Atualização Relatório': 'data_situacao_cadastral',  # Usando a data de atualização
        'Estado': 'uf'  # Usando a coluna 'Estado'
    }

    colunas_no_csv = list(mapa_colunas.keys())

    if not all(col in df.columns for col in colunas_no_csv):
        print("   - ERRO CRÍTICO: Colunas essenciais não foram encontradas no arquivo CSV.")
        print(f"   - Colunas esperadas: {colunas_no_csv}")
        print(f"   - Colunas encontradas: {df.columns.tolist()}")
        return

    print(f"   - Mapeando as colunas...")
    df = df[colunas_no_csv].rename(columns=mapa_colunas)

    df['cnpj'] = df['cnpj'].astype(str).str.replace(r'\D', '', regex=True)
    # A data de atualização já parece estar em um formato bom, vamos apenas converter
    df['data_situacao_cadastral'] = pd.to_datetime(df['data_situacao_cadastral'], errors='coerce').dt.strftime(
        '%Y-%m-%d')

    df.dropna(subset=['cnpj', 'data_situacao_cadastral'], inplace=True)

    df = df.replace({np.nan: None})

    dados_para_inserir = df.to_dict(orient='records')
    print(f"   - {len(dados_para_inserir)} registros válidos prontos para serem inseridos.")

    if not dados_para_inserir:
        print("   - Nenhum dado para inserir. Encerrando o processo.")
        return

    # --- 4. CARGA (Load) ---
    print(f"3. Carregando dados para a tabela '{NOME_TABELA}'...")

    tamanho_lote = 500
    total_inserido = 0
    for i in range(0, len(dados_para_inserir), tamanho_lote):
        lote = dados_para_inserir[i:i + tamanho_lote]
        try:
            supabase.table(NOME_TABELA).insert(lote).execute()
            total_inserido += len(lote)
            print(f"   - Lote {i // tamanho_lote + 1} inserido. Total de registros: {total_inserido}")
        except Exception as e:
            print(f"   - ERRO ao inserir o lote {i // tamanho_lote + 1}: {e}")
            pass

    print("\n--- PROCESSO DE ETL (CTF/APP) CONCLUÍDO ---")


# --- Ponto de Entrada do Script ---
if __name__ == "__main__":
    start_time = time.time()
    try:
        supabase_client = setup_supabase_client()
        carregar_dados(supabase_client)
    except Exception as e:
        print(f"Ocorreu um erro fatal durante a execução: {e}")

    end_time = time.time()
    print(f"Tempo total de execução: {end_time - start_time:.2f} segundos.")
