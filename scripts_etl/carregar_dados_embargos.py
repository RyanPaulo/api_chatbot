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
    from supabase_client import supabase


# URL direta para o arquivo  no portal de dados abertos do IBAMA
URL_DADOS_IBAMA_ZIP = "https://dadosabertos.ibama.gov.br/dados/SIFISC/termo_embargo/termo_embargo/termo_embargo_csv"
NOME_TABELA = "termos_embargo"

## FUNÇÃO PARA TERMOS DE EMBARGO
def carregar_dados_embargos( ):
    print("\n--- INICIANDO PROCESSO DE ETL (TERMOS DE EMBARGO - VIA URL) ---")

    print(f"1. Extraindo dados do arquivo ZIP da URL:\n   {URL_DADOS_IBAMA_ZIP}")
    try:
        # Faz o download do conteúdo do arquivo .zip em memória
        response = requests.get(URL_DADOS_IBAMA_ZIP)
        response.raise_for_status()  # Lança um erro se o download falhar (ex: 404)

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
                    encoding='latin-1', # Mantido pois é comum em dados governamentais mais antigos
                    on_bad_lines='skip',
                    low_memory=False
                )
        print("   - Dados extraídos com sucesso.")
    except Exception as e:
        print(f"   - ERRO CRÍTICO ao baixar e ler os dados da URL: {e}")
        return

    print("2. Transformando os dados...")

    # Mapeamento das colunas do CSV para as colunas do nosso banco de dados
    mapa_colunas = {
        'CPF_CNPJ_EMBARGADO': 'cpf_cnpj',
        'NOME_EMBARGADO': 'nome_embargado',
        'DAT_EMBARGO': 'data_embargo',
        'DES_TAD': 'justificativa',
        'MUNICIPIO': 'municipio',
        'UF': 'uf'
    }
    colunas_necessarias = list(mapa_colunas.keys())

    if not all(col in df.columns for col in colunas_necessarias):
        print("   - ERRO CRÍTICO: Colunas essenciais não foram encontradas no arquivo CSV.")
        print(f"   - Colunas esperadas: {colunas_necessarias}")
        print(f"   - Colunas encontradas: {df.columns.tolist()}")
        return

    print("   - Mapeando e renomeando colunas...")
    df = df[colunas_necessarias].rename(columns=mapa_colunas)

    print("   - Limpando e formatando os dados...")
    df['cpf_cnpj'] = df['cpf_cnpj'].astype(str).str.replace(r'\D', '', regex=True)
    df['data_embargo'] = pd.to_datetime(df['data_embargo'], errors='coerce').dt.strftime('%Y-%m-%d')

    # Corrige problema de encoding em colunas de texto
    if 'justificativa' in df.columns:
        df['justificativa'] = df['justificativa'].astype(str).apply(
            lambda x: x.encode('latin-1').decode('utf-8', 'ignore') if pd.notna(x) else x
        )

    df.dropna(subset=['cpf_cnpj', 'data_embargo'], inplace=True)
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

    print("\n--- PROCESSO DE ETL (TERMOS DE EMBARGO) CONCLUÍDO ---")



if __name__ == "__main__":
    start_time = time.time()
    try:
        carregar_dados_embargos()
    except Exception as e:
        print(f"Ocorreu um erro fatal durante a execução: {e}")

    end_time = time.time()
    print(f"Tempo total de execução: {end_time - start_time:.2f} segundos.")
