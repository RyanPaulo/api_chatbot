import os
import pandas as pd
from dotenv import load_dotenv
import time
import numpy as np



try:
    from ..supabase_cliente import supabase
except ImportError:
    # Adiciona o caminho do projeto para permitir a execução direta do script
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from supabase_client import supabase




URL_DADOS_IBAMA = "https://dadosabertos.ibama.gov.br/dados/CTF/APP/AC/pessoasJuridicas.csv"
NOME_TABELA = "cadastro_tecnico_federal"

## FUNÇÃO PRINCIPAL DE ETL PARA CTF
def carregar_dados_ctf( ):

    print("\n--- INICIANDO PROCESSO DE ETL (CADASTRO TÉCNICO FEDERAL - VIA URL) ---")


    print(f"1. Extraindo dados diretamente da URL do IBAMA:\n   {URL_DADOS_IBAMA}")
    try:
        # Usa pandas para ler o CSV diretamente do link, especificando o separador e encoding
        df = pd.read_csv(
            URL_DADOS_IBAMA,
            sep=';',
            encoding='utf-8',
            on_bad_lines='skip',
            low_memory=False
        )
        print("   - Dados extraídos com sucesso.")
    except Exception as e:
        print(f"   - ERRO CRÍTICO ao tentar baixar e ler os dados da URL: {e}")
        return


    print("2. Transformando os dados...")

    # Mapeamento das colunas do CSV para as colunas do nosso banco de dados
    mapa_colunas = {
        'CNPJ': 'cnpj',
        'Razão Social': 'razao_social',
        'Situação cadastral': 'situacao_cadastro',
        'Última Atualização Relatório': 'data_situacao_cadastral',
        'Estado': 'uf'
    }

    colunas_necessarias = list(mapa_colunas.keys())

    # Verifica se todas as colunas esperadas existem no DataFrame
    if not all(col in df.columns for col in colunas_necessarias):
        print("   - ERRO CRÍTICO: Colunas essenciais não foram encontradas no arquivo CSV baixado.")
        print(f"   - Colunas esperadas: {colunas_necessarias}")
        print(f"   - Colunas encontradas no arquivo: {df.columns.tolist()}")
        return

    print("   - Mapeando e renomeando colunas...")
    df = df[colunas_necessarias].rename(columns=mapa_colunas)

    print("   - Limpando e formatando os dados...")
    # Remove caracteres não numéricos do CNPJ
    df['cnpj'] = df['cnpj'].astype(str).str.replace(r'\D', '', regex=True)

    # Converte a data para o formato YYYY-MM-DD, tratando erros
    df['data_situacao_cadastral'] = pd.to_datetime(df['data_situacao_cadastral'], errors='coerce').dt.strftime('%Y-%m-%d')

    # Remove linhas onde o CNPJ ou a data são nulos após a conversão
    df.dropna(subset=['cnpj', 'data_situacao_cadastral'], inplace=True)

    # Substitui valores NaN do Pandas por None, que é compatível com o banco de dados
    df = df.replace({np.nan: None})

    # Converte o DataFrame limpo para uma lista de dicionários, pronta para inserção
    dados_para_inserir = df.to_dict(orient='records')
    print(f"   - {len(dados_para_inserir)} registros válidos prontos para serem inseridos.")

    if not dados_para_inserir:
        print("   - Nenhum dado para inserir. Encerrando o processo.")
        return


    print(f"3. Carregando dados para a tabela '{NOME_TABELA}' no Supabase...")

    tamanho_lote = 500  # Insere os dados em lotes para evitar sobrecarga
    total_inserido = 0
    for i in range(0, len(dados_para_inserir), tamanho_lote):
        lote = dados_para_inserir[i:i + tamanho_lote]
        try:
            # Usa o cliente Supabase importado para inserir o lote
            supabase.table(NOME_TABELA).insert(lote).execute()
            total_inserido += len(lote)
            print(f"   - Lote {i // tamanho_lote + 1} inserido. Total de registros: {total_inserido}")
        except Exception as e:
            print(f"   - ERRO ao inserir o lote {i // tamanho_lote + 1}: {e}")
            # 'pass' continua para o próximo lote mesmo se um falhar
            pass

    print("\n--- PROCESSO DE ETL (CTF/APP) CONCLUÍDO ---")


if __name__ == "__main__":
    start_time = time.time()
    try:
        # A conexão já é feita no `supabase_cliente.py`, então apenas chamamos a função
        carregar_dados_ctf()
    except Exception as e:
        print(f"Ocorreu um erro fatal durante a execução: {e}")

    end_time = time.time()
    print(f"Tempo total de execução: {end_time - start_time:.2f} segundos.")

