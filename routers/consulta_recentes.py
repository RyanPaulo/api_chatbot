from typing import List
from fastapi import APIRouter, Query, HTTPException
from schemas.sch_base_consultas import AutuacaoSchema
from supabase_client import supabase

router = APIRouter(
    prefix="/api/autuacoes/recentes",
    tags=["Consultas de Autuações Recentes"]
)

### CONSULTA AUTUAÇÕES MAIS RECENTER, ORDENADAS PELA DATA DE CRIAÇÃO ###
@router.get("/", response_model=List[AutuacaoSchema])
def consultar_recentes(
    limite: int = Query(5, title="Número de resultados a retornar", ge=1, le=50)
):
    try:
        response = supabase.table('autuacoes_ibama').select("*").order('created_at', desc=True).limit(limite).execute()
        dados = response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {e}")

    return dados