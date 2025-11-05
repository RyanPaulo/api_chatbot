from typing import List
from fastapi import APIRouter, Query, HTTPException

from schemas.sch_base_consultas import AutuacaoSchema
from supabase_client import supabase

router = APIRouter(
    prefix="/api/autuacoes/recentes",
    tags=["Consultas de Autuações Recentes"]
)

# EXEMPLO = /api/autuacoes/recentes?limite=10
@router.get("/", response_model=List[AutuacaoSchema])
def consultar_recentes(
    limite: int = Query(5, title="Número de resultados a retornar", ge=1, le=50)
):
    """
    Retorna as autuações mais recentes, ordenadas pela data de criação.
    """
    try:
        # .order() para ordenar e .limit() para restringir o número de resultados
        response = supabase.table('autuacoes_ibama').select("*").order('created_at', desc=True).limit(limite).execute()
        dados = response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {e}")

    return dados