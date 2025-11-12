from typing import List
from fastapi import APIRouter, Path, HTTPException
from schemas.sch_base_consultas import TermoEmbargoSchema, RespostaEmbargoSchema
from supabase_client import supabase

router = APIRouter(
    prefix="/api/embargos",
    tags=["Consultas de Termos de Embargo"]
)

### CONSULTA TERMOS DE EMBARGOS ###
@router.get("/documento/{cpf_cnpj}", response_model=RespostaEmbargoSchema)
def consultar_embargo_por_documento(
    cpf_cnpj: str = Path(..., title="CPF ou CNPJ a ser consultado")
):
    documento_limpo = "".join(filter(str.isdigit, cpf_cnpj))

    try:
        # Executa a consulta no Supabase
        response = supabase.table('termos_embargo').select("*").eq('cpf_cnpj', documento_limpo).execute()
        dados = response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {e}")

    return {"documento": documento_limpo, "embargos": dados}


### BUSCANDO OS EMBARGOS PELO O MUNICIPIO###
@router.get("/municipio/{nome_municipio}", response_model=List[TermoEmbargoSchema])
def consultar_embargo_por_municipio(
    nome_municipio: str = Path(..., title="Nome do município a ser consultado")
):
    try:
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


