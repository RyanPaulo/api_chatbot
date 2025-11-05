from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import endpoint01, consulta_municipio, consulta_recentes, consulta_glossario, consulta_legislacao, consulta_embargos, consulta_ctf

# Cria uma instância da aplicação FastAPI
app = FastAPI(
    title="EcoBot API",
    description="API para fornecer dados ambientais ao chatbot EcoBot.",
    version="1.1.0"
)

# Configuração CORS - ESSENCIAL para integração com Rasa AI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos: ["http://localhost:5005", "https://seu-dominio.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Permite todos os headers
)

# Incluir os routeadores no executor
app.include_router(endpoint01.router)
app.include_router(consulta_municipio.router)
app.include_router(consulta_recentes.router)
app.include_router(consulta_glossario.router)
app.include_router(consulta_legislacao.router)
app.include_router(consulta_embargos.router)
app.include_router(consulta_ctf.router)


# **** ENDPOINT RAIZ PARA VERIFICAR SE A API ESTA ONLINE E DA A MSG DE BOAS-VINDAS ****
@app.get("/", tags=["Status"])
def read_root():
    return {"message": "Bem-vindo à API do EcoBot!"}

