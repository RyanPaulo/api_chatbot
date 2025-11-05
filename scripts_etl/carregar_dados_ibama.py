# api_chatbot/scripts_etl/carregar_dados_ibama.py

import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import time
import numpy as np
import io


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

PASTA_DADOS_LOCAIS = os.path.join(os.path.dirname(__file__), '..', 'dados_locais')
NOME_TABELA = "autuacoes_ibama"


def carregar_dados(supabase: Client):
    """
    Função principal que executa o processo de ETL a partir de arquivos CSV locais.
    """
    print("\n--- INICIANDO PROCESSO DE ETL (LENDO ARQUIVOS LOCAIS) ---")

    # --- 2. EXTRAÇÃO (Extraction) ---
    print(f"1. Lendo todos os arquivos .csv da pasta: {PASTA_DADOS_LOCAIS}")

    lista_de_dataframes = []
    try:
        arquivos_na_pasta = os.listdir(PASTA_DADOS_LOCAIS)
        arquivos_csv = [f for f in arquivos_na_pasta if f.endswith('.csv')]

        if not arquivos_csv:
            print(f"   - ERRO: Nenhum arquivo .csv encontrado na pasta '{PASTA_DADOS_LOCAIS}'.")
            return

        for file_name in arquivos_csv:
            print(f"   - Lendo o arquivo: {file_name}")
            caminho_completo = os.path.join(PASTA_DADOS_LOCAIS, file_name)

            with open(caminho_completo, 'rb') as f:
                content_bytes = f.read()

            content_string = content_bytes.decode('latin-1', errors='ignore')
            csv_file_in_memory = io.StringIO(content_string)

            df_temp = pd.read_csv(csv_file_in_memory, sep=';', on_bad_lines='skip', low_memory=False)
            lista_de_dataframes.append(df_temp)

        df = pd.concat(lista_de_dataframes, ignore_index=True)
        print(f"\n   - Todos os {len(lista_de_dataframes)} arquivos CSV foram lidos e consolidados com sucesso.")

    except Exception as e:
        print(f"   - ERRO CRÍTICO durante a extração dos arquivos locais: {e}")
        return

    # --- 3. TRANSFORMAÇÃO (Transformation) ---
    print("2. Transformando os dados...")

    mapa_colunas = {
        'CPF_CNPJ_INFRATOR': 'cpf_cnpj', 'NOME_INFRATOR': 'nome_autuado',
        'DAT_HORA_AUTO_INFRACAO': 'data_auto', 'VAL_AUTO_INFRACAO': 'valor_multa',
        'DES_INFRACAO': 'descricao_infracao', 'MUNICIPIO': 'municipio', 'UF': 'uf'
    }

    colunas_existentes = {k: v for k, v in mapa_colunas.items() if k in df.columns}
    if not colunas_existentes or 'CPF_CNPJ_INFRATOR' not in colunas_existentes:
        print("   - ERRO CRÍTICO: Colunas essenciais não foram encontradas nos arquivos CSV.")
        return

    print(f"   - Mapeando as colunas encontradas: {list(colunas_existentes.keys())}")
    df = df[list(colunas_existentes.keys())].rename(columns=colunas_existentes)

    # ==================================================================
    # CORREÇÃO DE ENCODING - "LAVAGEM" DO TEXTO
    # ==================================================================
    # Aplicamos a "lavagem" apenas na coluna que tem o problema
    if 'descricao_infracao' in df.columns:
        print("   - Corrigindo codificação da coluna 'descricao_infracao'...")
        df['descricao_infracao'] = df['descricao_infracao'].astype(str).apply(
            lambda x: x.encode('latin-1').decode('utf-8', 'ignore')
        )
    # ==================================================================

    df['cpf_cnpj'] = df['cpf_cnpj'].astype(str).str.replace(r'\D', '', regex=True)
    df['valor_multa'] = pd.to_numeric(df['valor_multa'].astype(str).str.replace(',', '.', regex=False), errors='coerce')
    df['data_auto'] = pd.to_datetime(df['data_auto'], errors='coerce').dt.strftime('%Y-%m-%d')

    df.dropna(subset=['cpf_cnpj', 'data_auto'], inplace=True)

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

    print("\n--- PROCESSO DE ETL CONCLUÍDO ---")


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
