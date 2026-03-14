"""
Router de páginas HTML.

Todas as rotas aqui retornam páginas renderizadas com Jinja2.
São as páginas que o usuário vê no navegador:
  /            → Dashboard principal com métricas e gráficos
  /pacientes   → Listagem paginada de pacientes com filtros
  /agendamentos → Listagem de agendamentos
"""

from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.service import (
    calcular_metricas,
    listar_pacientes,
    listar_agendamentos,
    listar_ubs,
)

router    = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, tags=["Páginas"])
def pagina_dashboard(request: Request):
    """
    Página principal — exibe os cards de métricas e os três gráficos:
    - Rosca: status dos convites
    - Barras horizontais: pacientes por UBS
    - Barras verticais: distribuição por faixa etária
    """
    metricas = calcular_metricas()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "m": metricas},
    )


@router.get("/pacientes", response_class=HTMLResponse, tags=["Páginas"])
def pagina_pacientes(
    request: Request,
    pagina:        int = Query(default=1, ge=1),
    busca:         str = Query(default=""),
    ubs_filtro:    str = Query(default=""),
    status_filtro: str = Query(default=""),
):
    """
    Página de listagem de pacientes.
    Suporta busca por nome/telefone, filtro por UBS e filtro por status do convite.
    """
    dados    = listar_pacientes(pagina, 20, busca, ubs_filtro, status_filtro)
    lista_ubs = listar_ubs()

    return templates.TemplateResponse(
        "patients.html",
        {
            "request":       request,
            "dados":         dados,
            "lista_ubs":     lista_ubs,
            "busca":         busca,
            "ubs_filtro":    ubs_filtro,
            "status_filtro": status_filtro,
        },
    )


@router.get("/agendamentos", response_class=HTMLResponse, tags=["Páginas"])
def pagina_agendamentos(
    request: Request,
    pagina: int = Query(default=1, ge=1),
):
    """
    Página de listagem de agendamentos com paginação.
    """
    dados = listar_agendamentos(pagina, 20)
    return templates.TemplateResponse(
        "appointments.html",
        {"request": request, "dados": dados},
    )