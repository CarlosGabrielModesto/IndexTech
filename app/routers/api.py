import os
import shutil

from fastapi import APIRouter, Form, HTTPException, Query, UploadFile
from sqlalchemy import select

from app.db import get_session
from app.models import Appointment, Invitation, Person
from app.service import (
    agendar_consulta,
    calcular_metricas,
    enviar_convites_pendentes,
    importar_pessoas,
    listar_pacientes,
    normalizar_telefone,
)

router = APIRouter(prefix="/api", tags=["API"])

TEMPLATE_PADRAO = (
    "Olá, {primeiro_nome}! 👋 Somos da equipe de saúde {ubs}. "
    "Você faz parte do grupo de mulheres que precisam realizar a coleta preventiva "
    "para câncer de colo do útero e mama. "
    "Responda *SIM* para agendar sua consulta gratuitamente. "
    "Responda *PARAR* para não receber mais mensagens. 💚"
)


@router.post("/import")
async def importar_arquivo(file: UploadFile):
    extensoes_permitidas = {".xlsx", ".xls", ".csv"}
    extensao = os.path.splitext(file.filename or "")[1].lower()

    if extensao not in extensoes_permitidas:
        raise HTTPException(
            status_code=400,
            detail=f"Formato não suportado: {extensao}. Use .xlsx, .xls ou .csv.",
        )

    caminho_tmp = f"./tmp_{file.filename}"
    try:
        with open(caminho_tmp, "wb") as f:
            shutil.copyfileobj(file.file, f)
        importados = importar_pessoas(caminho_tmp)
        return {"status": "success", "importados": importados}
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro))
    except Exception as erro:
        raise HTTPException(status_code=500, detail=f"Erro interno: {erro}")
    finally:
        if os.path.exists(caminho_tmp):
            os.remove(caminho_tmp)


@router.post("/invite")
def disparar_convites(
    template: str = Form(default=TEMPLATE_PADRAO),
    limite:   int = Form(default=50, ge=1, le=500),
):
    resultado = enviar_convites_pendentes(template, limite)
    return {
        "status":    "success",
        "enviados":  resultado["enviados"],
        "erros":     resultado["erros"],
        "ignorados": resultado["ignorados"],
    }


@router.post("/schedule")
def agendar_manualmente(
    person_phone: str = Form(...),
    when:         str = Form(...),
    place:        str = Form(default="UBS"),
):
    telefone = normalizar_telefone(person_phone)

    with get_session() as s:
        pessoa = s.execute(
            select(Person).where(Person.phone == telefone)
        ).scalar_one_or_none()

        if not pessoa:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhuma paciente encontrada com o número {person_phone}.",
            )

        agendamento = agendar_consulta(pessoa.id, when, place)
        return {
            "status":         "success",
            "mensagem":       "Agendamento criado e confirmação enviada.",
            "agendamento_id": agendamento.id,
            "paciente":       pessoa.name,
        }


@router.get("/metrics")
def obter_metricas():
    return calcular_metricas()


@router.get("/patients")
def listar(
    pagina:        int = Query(default=1, ge=1),
    busca:         str = Query(default=""),
    ubs_filtro:    str = Query(default=""),
    status_filtro: str = Query(default=""),
):
    return listar_pacientes(pagina, 20, busca, ubs_filtro, status_filtro)


@router.put("/patients/{patient_id}/optout")
def alternar_optout(patient_id: int):
    with get_session() as s:
        pessoa = s.get(Person, patient_id)
        if not pessoa:
            raise HTTPException(status_code=404, detail="Paciente não encontrada.")

        pessoa.consent_optout = not pessoa.consent_optout
        s.commit()

        return {
            "status":   "success",
            "id":       patient_id,
            "optout":   pessoa.consent_optout,
            "mensagem": (
                "Paciente removida da lista de envios."
                if pessoa.consent_optout
                else "Paciente reativada para envios."
            ),
        }


@router.put("/appointments/{appointment_id}/status")
def atualizar_status_agendamento(
    appointment_id: int,
    novo_status: str = Form(...),
):
    status_validos = {"scheduled", "done", "cancelled"}
    if novo_status not in status_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Status inválido. Use: {', '.join(status_validos)}",
        )

    with get_session() as s:
        agendamento = s.get(Appointment, appointment_id)
        if not agendamento:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado.")

        agendamento.status = novo_status
        s.commit()

        return {
            "status":         "success",
            "agendamento_id": appointment_id,
            "novo_status":    novo_status,
        }


@router.post("/seed")
def seed_teste(phone: str = Form(default="+5514999999999")):
    from datetime import datetime, timezone
    telefone = normalizar_telefone(phone)
    with get_session() as s:
        existe = s.execute(select(Person).where(Person.phone == telefone)).scalar_one_or_none()
        if not existe:
            p = Person(
                name="Paciente Teste",
                phone=telefone,
                ubs="UBS Teste",
                birthdate="01/01/1985",
                created_at=datetime.now(timezone.utc),
            )
            s.add(p)
            s.commit()
            s.refresh(p)
            s.add(Invitation(
                person_id=p.id,
                status="pending",
                updated_at=datetime.now(timezone.utc),
            ))
            s.commit()
            return {"status": "success", "mensagem": "Paciente de teste inserida.", "id": p.id}

        return {"status": "info", "mensagem": "Paciente de teste já existe.", "id": existe.id}