from typing import List
from fastapi import APIRouter, Path, HTTPException
from schemas.sch_base_consultas import AutuacaoSchema
from supabase_client import supabase

router = APIRouter(
    prefix="/api/autuacoes/municipio",
    tags=["Consultas de Autuações por Município"]
)

# EXEMPLO = /api/autuacoes/municipio/{nome_municipio}
@router.get("/{nome_municipio}", response_model=List[AutuacaoSchema] )
def consultar_por_municipio(
    nome_municipio: str = Path(..., title="Nome do município a ser consultado")
):
    """
    Busca todas as autuações registradas em um determinado município.
    """
    try:
        # .ilike() faz uma busca "case-insensitive" (ignora maiúsculas/minúsculas)
        response = supabase.table('autuacoes_ibama').select("*").ilike('municipio', f'%{nome_municipio}%').execute()
        dados = response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {e}")

    if not dados:
        raise HTTPException(
            status_code=404,
            detail=f"Nenhuma autuação encontrada para o município: {nome_municipio}"
        )

    return dados