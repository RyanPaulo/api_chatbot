# api_chatbot/scripts_etl/carregar_dados_legislacao.py

import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import time
import numpy as np
from sentence_transformers import SentenceTransformer


# --- 1. CONFIGURAÇÃO E CONEXÃO ---

def setup_supabase_client() -> Client:
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    print(f"Procurando arquivo .env em: {os.path.abspath(dotenv_path)}")
    load_dotenv(dotenv_path=dotenv_path)
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        raise Exception("ERRO: Variáveis de ambiente do Supabase não definidas.")
    print("Credenciais do Supabase carregadas.")
    return create_client(supabase_url, supabase_key)


# --- Variáveis de Configuração ---

NOME_ARQUIVO_LOCAL = "legislacao_base.csv"
CAMINHO_ARQUIVO_LOCAL = os.path.join(os.path.dirname(__file__), '..', 'dados_locais', NOME_ARQUIVO_LOCAL)
NOME_TABELA = "legislacao_ambiental"
MODELO_EMBEDDING = 'all-MiniLM-L6-v2'


def carregar_dados(supabase: Client):
    print("\n--- INICIANDO ETL DE LEGISLAÇÃO AMBIENTAL ---")

    # --- 2. EXTRAÇÃO (Extraction) ---
    print(f"1. Lendo o arquivo CSV local: {CAMINHO_ARQUIVO_LOCAL}")
    try:
        df = pd.read_csv(CAMINHO_ARQUIVO_LOCAL, sep=';', encoding='utf-8')
        print(f"   - {len(df)} leis encontradas no arquivo.")
    except Exception as e:
        print(f"   - ERRO CRÍTICO ao ler o arquivo: {e}")
        return

    # --- 3. TRANSFORMAÇÃO (Transformation) ---
    print("2. Transformando os dados e gerando embeddings...")

    print(f"   - Carregando o modelo de IA '{MODELO_EMBEDDING}'...")
    model = SentenceTransformer(MODELO_EMBEDDING)

    df['texto_para_embedding'] = df['titulo'] + " " + df['resumo']

    print("   - Gerando embeddings... (Isso pode levar um momento)")
    embeddings = model.encode(df['texto_para_embedding'].tolist(), show_progress_bar=True)

    # ==================================================================
    # CORREÇÃO PRINCIPAL: Convertendo cada embedding para uma lista Python
    # ==================================================================
    df['embedding'] = [embedding.tolist() for embedding in embeddings]

    df['palavras_chave'] = df['palavras_chave'].apply(lambda x: x.split(',') if isinstance(x, str) else [])

    colunas_tabela = ['titulo', 'resumo', 'link_oficial', 'palavras_chave', 'embedding', 'tipo_norma', 'orgao_emissor']
    df_final = df[colunas_tabela]

    df_final = df_final.replace({np.nan: None})
    dados_para_inserir = df_final.to_dict(orient='records')

    print(f"   - {len(dados_para_inserir)} registros prontos para serem inseridos.")

    # --- 4. CARGA (Load) ---
    print(f"3. Carregando dados para a tabela '{NOME_TABELA}'...")

    print("   - Limpando a tabela existente...")
    supabase.table(NOME_TABELA).delete().neq('id', 0).execute()

    try:
        supabase.table(NOME_TABELA).insert(dados_para_inserir).execute()
        print("   - Todos os registros de legislação foram inseridos com sucesso!")
    except Exception as e:
        print(f"   - ERRO ao inserir os dados: {e}")

    print("\n--- PROCESSO DE ETL DE LEGISLAÇÃO CONCLUÍDO ---")


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
