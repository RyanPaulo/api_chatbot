from typing import List
from fastapi import APIRouter, Query, HTTPException
from schemas.sch_base_consultas import LegislacaoSchema
from supabase_client import supabase

router = APIRouter(
    prefix="/api/legislacao",
    tags=["Legislação Ambiental"]
)

### BUSCAR OS TERMOS DE LEGISLAÇÃO ###
@router.get("/buscar", response_model=List[LegislacaoSchema])
def buscar_legislacao(
    termo: str = Query(..., min_length=3, description="Termo a ser buscado no título ou resumo da legislação")
):
    try:
        # Busca o termo no título OU no resumo
        response = supabase.table('legislacao_ambiental').select("*").or_(
            f"titulo.ilike.%{termo}%,resumo.ilike.%{termo}%"
        ).execute()
        dados = response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {e}")

    if not dados:
        raise HTTPException(
            status_code=404,
            detail=f"Nenhuma legislação encontrada para o termo: '{termo}'"
        )

    return dados
