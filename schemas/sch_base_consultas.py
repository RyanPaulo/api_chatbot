from pydantic import BaseModel
from typing import List, Optional

## SCHEMA PARA AUTUAÇÕES ##
class AutuacaoSchema(BaseModel):
    id: int
    data_auto: Optional[str] = None
    valor_multa: Optional[float] = None
    descricao_infracao: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None

class RespostaConsultaSchema(BaseModel):
    documento: str
    autuacoes: List[AutuacaoSchema]


## SCHEMA PARA LEGISLAÇÃO ##
class LegislacaoSchema(BaseModel):
    id: int
    titulo: str
    resumo: Optional[str] = None
    tipo_norma: Optional[str] = None
    link_oficial: Optional[str] = None
    palavras_chave: Optional[List[str]] = None


## SCHEMA PARA GLOSSARIO ##
class GlossarioSchema(BaseModel):
    id: int
    termo: str
    definicao: str
    categoria: Optional[str] = None


## SCHEMA PARA TERMOS DE EMBARGO ##
class TermoEmbargoSchema(BaseModel):
    id: int
    cpf_cnpj: Optional[str] = None
    nome_embargado: Optional[str] = None
    data_embargo: Optional[str] = None
    justificativa: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    wkt_geometria: Optional[str] = None

## SCHEMA PARA CONSULTA DOS ENBARGOS ##
class RespostaEmbargoSchema(BaseModel):
    documento: str
    embargos: List[TermoEmbargoSchema]


## SCHEMA PARA CADASTRO TÉCNICO FEDERAL (CTF) ##
class CadastroTecnicoFederalSchema(BaseModel):
    id: int
    cnpj: str
    razao_social: Optional[str] = None
    situacao_cadastro: Optional[str] = None
    data_situacao_cadastral: Optional[str] = None
    uf: Optional[str] = None


class RespostaCTFSchema(BaseModel):
    cnpj: str
    cadastro: CadastroTecnicoFederalSchema