import os
import pandas as pd
import time
import numpy as np
import requests
import zipfile
import io

try:
    from ..supabase_cliente import supabase
except ImportError:
    # Adiciona o caminho do projeto para permitir a execução direta do script
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from supabase_cliente import supabase

# URL direta para o arquivo .ZIP de autos de infração distribuídos
URL_DADOS_IBAMA_ZIP = "https://dadosabertos.ibama.gov.br/dados/SIFISC/auto_infracao/auto_infracao_distribuidos/ultimos_5_anos_infra_dist_csv.zip"
NOME_TABELA = "autuacoes_ibama"


## FUNÇÃO PARA AUTOS DE INFRAÇÃO
def carregar_dados_infracoes():

    print("\n--- INICIANDO PROCESSO DE ETL (AUTOS DE INFRAÇÃO - VIA URL) ---")

    print(f"1. Extraindo dados do arquivo ZIP da URL:\n   {URL_DADOS_IBAMA_ZIP}")
    try:
        # Faz o download do conteúdo do arquivo .zip em memória
        response = requests.get(URL_DADOS_IBAMA_ZIP)
        response.raise_for_status()  # Lança um erro se o download falhar

        # Abre o arquivo .zip a partir do conteúdo baixado
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Encontra o primeiro arquivo .csv dentro do .zip
            nome_csv = next((f for f in z.namelist() if f.endswith('.csv')), None)
            if not nome_csv:
                raise FileNotFoundError("Nenhum arquivo .csv encontrado dentro do .zip baixado.")

            print(f"   - Arquivo CSV encontrado no ZIP: '{nome_csv}'")
            # Lê o arquivo CSV diretamente do .zip
            with z.open(nome_csv) as f:
                df = pd.read_csv(
                    f,
                    sep=';',
                    encoding='latin-1',
                    on_bad_lines='skip',
                    low_memory=False
                )
        print("   - Dados extraídos com sucesso.")
    except Exception as e:
        print(f"   - ERRO CRÍTICO ao baixar e ler os dados da URL: {e}")
        return

    print("2. Transformando os dados...")

    mapa_colunas = {
        'CPF_CNPJ_INFRATOR': 'cpf_cnpj',
        'NOME_INFRATOR': 'nome_autuado',
        'DAT_HORA_AUTO_INFRACAO': 'data_auto',
        'VAL_AUTO_INFRACAO': 'valor_multa',
        'DES_INFRACAO': 'descricao_infracao',
        'MUNICIPIO': 'municipio',
        'UF': 'uf'
    }
    colunas_necessarias = list(mapa_colunas.keys())

    if not all(col in df.columns for col in colunas_necessarias):
        print("   - ERRO CRÍTICO: Colunas essenciais não foram encontradas no arquivo CSV.")
        return

    print("   - Mapeando, limpando e formatando os dados...")
    df = df[colunas_necessarias].rename(columns=mapa_colunas)

    # Limpeza e conversão de tipos
    df['cpf_cnpj'] = df['cpf_cnpj'].astype(str).str.replace(r'\D', '', regex=True)
    df['valor_multa'] = pd.to_numeric(df['valor_multa'].astype(str).str.replace(',', '.', regex=False), errors='coerce')
    df['data_auto'] = pd.to_datetime(df['data_auto'], errors='coerce').dt.strftime('%Y-%m-%d')

    # Corrige problema de encoding na coluna de descrição
    if 'descricao_infracao' in df.columns:
        df['descricao_infracao'] = df['descricao_infracao'].astype(str).apply(
            lambda x: x.encode('latin-1').decode('utf-8', 'ignore') if pd.notna(x) else x
        )

    df.dropna(subset=['cpf_cnpj', 'data_auto'], inplace=True)
    df = df.replace({np.nan: None})

    dados_para_inserir = df.to_dict(orient='records')
    print(f"   - {len(dados_para_inserir)} registros válidos prontos para serem inseridos.")

    if not dados_para_inserir:
        print("   - Nenhum dado para inserir. Encerrando o processo.")
        return

    print(f"3. Carregando dados para a tabela '{NOME_TABELA}' no Supabase...")

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

    print("\n--- PROCESSO DE ETL (AUTOS DE INFRAÇÃO) CONCLUÍDO ---")



if __name__ == "__main__":
    start_time = time.time()
    try:
        carregar_dados_infracoes()
    except Exception as e:
        print(f"Ocorreu um erro fatal durante a execução: {e}")

    end_time = time.time()
    print(f"Tempo total de execução: {end_time - start_time:.2f} segundos.")
