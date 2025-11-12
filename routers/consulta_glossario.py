from fastapi import APIRouter, Path, HTTPException
from schemas.sch_base_consultas import GlossarioSchema # Importa do nosso arquivo de schemas
from supabase_client import supabase

router = APIRouter(
    prefix="/api/glossario",
    tags=["Glossário de Termos"]
)


### CONSULTA TERMO GLOSSARIO###
@router.get("/{termo_busca}", response_model=GlossarioSchema)
def buscar_termo_glossario(
    termo_busca: str = Path(..., description="Termo ou sigla a ser buscado no glossário")
):
    try:
        response = supabase.table('termos_glossario').select("*").ilike('termo', termo_busca).limit(1).single().execute()
        dado = response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {e}")

    if not dado:
        raise HTTPException(
            status_code=404,
            detail=f"O termo '{termo_busca}' não foi encontrado no glossário."
        )

    return dado
