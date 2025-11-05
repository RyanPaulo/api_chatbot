from fastapi import Path, HTTPException, APIRouter
from schemas.sch_base_consultas import RespostaConsultaSchema
from supabase_client import supabase


router = APIRouter(
    prefix="/api/autuacoes/documento",
    tags=["Consultas de Autuações"]
)

# EXEMPLO = /api/autuacoes/documento/{cpf_cnpj}
@router.get("/{cpf_cnpj}", response_model=RespostaConsultaSchema)

def consultar_por_documento(cpf_cnpj: str = Path(..., title="CPF ou CNPJ a ser consultado")):

    documento_limpo = "".join(filter(str.isdigit, cpf_cnpj))

    try:
        # Executa a consulta no Supabase
        response = supabase.table('autuacoes_ibama').select("*").eq('cpf_cnpj', documento_limpo).execute()

        # A biblioteca do Supabase retorna os dados dentro de um atributo 'data'
        dados = response.data

    except Exception as e:
        # Tratamento de erro genérico para falhas na consulta
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {e}")

    return {"documento": documento_limpo, "autuacoes": dados}