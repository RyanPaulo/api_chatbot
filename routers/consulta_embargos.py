from typing import List
from fastapi import APIRouter, Path, HTTPException
from schemas.sch_base_consultas import TermoEmbargoSchema, RespostaEmbargoSchema
from supabase_client import supabase

router = APIRouter(
    prefix="/api/embargos",
    tags=["Consultas de Termos de Embargo"]
)

# EXEMPLO = /api/embargos/documento/{cpf_cnpj}
@router.get("/documento/{cpf_cnpj}", response_model=RespostaEmbargoSchema)
def consultar_embargo_por_documento(
    cpf_cnpj: str = Path(..., title="CPF ou CNPJ a ser consultado")
):
    """
    Busca todos os termos de embargo registrados para um CPF ou CNPJ.
    """
    documento_limpo = "".join(filter(str.isdigit, cpf_cnpj))

    try:
        # Executa a consulta no Supabase
        response = supabase.table('termos_embargo').select("*").eq('cpf_cnpj', documento_limpo).execute()
        dados = response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {e}")

    return {"documento": documento_limpo, "embargos": dados}


# EXEMPLO = /api/embargos/municipio/{nome_municipio}
@router.get("/municipio/{nome_municipio}", response_model=List[TermoEmbargoSchema])
def consultar_embargo_por_municipio(
    nome_municipio: str = Path(..., title="Nome do município a ser consultado")
):
    """
    Busca todos os termos de embargo registrados em um determinado município.
    """
    try:
        # .ilike() faz uma busca "case-insensitive" (ignora maiúsculas/minúsculas)
        response = supabase.table('termos_embargo').select("*").ilike('municipio', f'%{nome_municipio}%').execute()
        dados = response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {e}")

    if not dados:
        raise HTTPException(
            status_code=404,
            detail=f"Nenhum embargo encontrado para o município: {nome_municipio}"
        )

    return dados


