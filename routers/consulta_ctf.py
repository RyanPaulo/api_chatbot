from typing import List
from fastapi import APIRouter, Path, HTTPException
from schemas.sch_base_consultas import CadastroTecnicoFederalSchema, RespostaCTFSchema
from supabase_client import supabase

router = APIRouter(
    prefix="/api/ctf",
    tags=["Consultas de Cadastro Técnico Federal"]
)

# EXEMPLO = /api/ctf/cnpj/{cnpj}
@router.get("/cnpj/{cnpj}", response_model=RespostaCTFSchema)
def consultar_ctf_por_cnpj(
    cnpj: str = Path(..., title="CNPJ a ser consultado")
):
    """
    Busca o cadastro técnico federal de uma pessoa jurídica pelo CNPJ.
    """
    cnpj_limpo = "".join(filter(str.isdigit, cnpj))

    try:
        # Executa a consulta no Supabase
        response = supabase.table('cadastro_tecnico_federal').select("*").eq('cnpj', cnpj_limpo).limit(1).single().execute()
        dado = response.data
    except Exception as e:
        # Se não encontrar registro, retorna 404
        if "not found" in str(e).lower() or "single" in str(e).lower():
            raise HTTPException(
                status_code=404,
                detail=f"CNPJ '{cnpj_limpo}' não encontrado no Cadastro Técnico Federal."
            )
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {e}")

    return {"cnpj": cnpj_limpo, "cadastro": dado}


# EXEMPLO = /api/ctf/situacao/{situacao}
@router.get("/situacao/{situacao}", response_model=List[CadastroTecnicoFederalSchema])
def consultar_ctf_por_situacao(
    situacao: str = Path(..., title="Situação cadastral a ser consultada")
):
    """
    Busca todas as pessoas jurídicas com uma determinada situação cadastral no CTF.
    Exemplos de situações: 'Ativo', 'Inativo', 'Suspenso', etc.
    """
    try:
        # .ilike() faz uma busca "case-insensitive" (ignora maiúsculas/minúsculas)
        response = supabase.table('cadastro_tecnico_federal').select("*").ilike('situacao_cadastro', f'%{situacao}%').execute()
        dados = response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {e}")

    if not dados:
        raise HTTPException(
            status_code=404,
            detail=f"Nenhum cadastro encontrado com a situação: '{situacao}'"
        )

    return dados


