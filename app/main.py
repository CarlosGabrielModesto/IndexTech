"""
Ponto central da aplicação FastAPI.

Responsabilidades:
  - Cria a instância do app com metadados para o Swagger
  - Inicializa o banco de dados na subida
  - Registra os arquivos estáticos e templates
  - Inclui os três routers: dashboard, api e webhook
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from app.db import init_db
from app.routers import dashboard, api, webhook

# Carrega as variáveis do .env antes de qualquer import que dependa delas
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Executado uma vez na inicialização do servidor.
    Garante que todas as tabelas existam antes de receber requisições.
    """
    init_db()
    yield


# --- Criação da aplicação ---
app = FastAPI(
    title="Hygeia Digital",
    description=(
        "Sistema de busca ativa para rastreamento de câncer de colo do útero e mama. "
        "Desenvolvido para o Hackathon Hygeia Digital 2025 — UNESP Botucatu."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Arquivos estáticos (CSS, JS, imagens) ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --- Templates Jinja2 (HTML) ---
# Exportado para ser reutilizado nos routers
templates = Jinja2Templates(directory="app/templates")

# --- Registro dos routers ---
app.include_router(dashboard.router)   # Páginas HTML
app.include_router(api.router)         # Endpoints JSON  (prefixo /api)
app.include_router(webhook.router)     # Webhook Twilio  (prefixo /twilio)