"""
Camada de serviços — lógica de negócio da aplicação.
"""

import re
import csv
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone, timedelta

import pandas as pd
from sqlalchemy import select, func

from app.models import Person, Invitation, Appointment
from app.db import get_session
from app.notify import send_message_phone


UTC   = timezone.utc
BR_TZ = timezone(timedelta(hours=-3))

COLUNAS = {
    "phone":         ["telefone_01", "phone", "telefone", "celular", "telefone1", "telefone_1"],
    "primeiro_nome": ["primeiro_nome", "first_name", "nome"],
    "ultimo_nome":   ["ultimo_nome", "last_name", "sobrenome"],
    "name":          ["name", "nome_completo", "paciente", "beneficiaria", "full_name"],
    "neighborhood":  ["neighborhood", "bairro", "localidade"],
    "ubs":           ["ubs", "unidade", "posto", "ubs_nome"],
    "birthdate":     ["data_nascimento", "birthdate", "nascimento", "dob"],
    "email":         ["email", "e-mail", "mail"],
    "cep":           ["cep", "codigo_postal", "zip"],
    "raca_cor":      ["raca_cor", "raca", "cor", "etnia"],
}


def agora_utc() -> datetime:
    return datetime.now(UTC)


def para_br(dt: datetime) -> datetime:
    return dt.astimezone(BR_TZ)


def formatar_br(dt: datetime) -> str:
    return para_br(dt).strftime("%d/%m/%Y %H:%M")


def formatar_when_br(when_str: str) -> str:
    formatos = ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"]
    for fmt in formatos:
        try:
            dt = datetime.strptime(when_str, fmt).replace(tzinfo=UTC)
            return formatar_br(dt)
        except ValueError:
            continue
    return when_str


def normalizar_telefone(phone: str) -> str:
    if not phone:
        return ""
    digitos = re.sub(r"\D", "", str(phone))
    if len(digitos) == 13 and digitos.startswith("55"):
        return f"+{digitos}"
    if len(digitos) == 11:
        return f"+55{digitos}"
    if len(digitos) == 10:
        return f"+55{digitos}"
    if len(digitos) == 12 and digitos.startswith("55"):
        return f"+{digitos}"
    return f"+{digitos}" if digitos and not digitos.startswith("+") else phone


def separar_nome(nome_completo: str) -> tuple:
    partes = (nome_completo or "").strip().split()
    if not partes:
        return "", ""
    if len(partes) == 1:
        return partes[0], ""
    return partes[0], " ".join(partes[1:])


def _pegar_campo(row: dict, chaves: list) -> Optional[str]:
    for chave in chaves:
        valor = row.get(chave)
        if valor not in (None, "", float("nan")):
            texto = str(valor).strip()
            if texto and texto.lower() != "nan":
                return texto
    return None


def importar_pessoas(caminho: str) -> int:
    extensao = Path(caminho).suffix.lower()
    if extensao in {".xlsx", ".xls"}:
        return _importar_excel(caminho)
    return _importar_csv(caminho)


def _importar_excel(caminho: str) -> int:
    try:
        df = pd.read_excel(
            caminho, engine="openpyxl",
            dtype={"telefone_01": str, "telefone_02": str, "phone": str, "celular": str},
        )
    except Exception as erro:
        raise ValueError(f"Erro ao ler o arquivo Excel: {erro}")

    df.columns = [str(c).strip().lower() for c in df.columns]
    count = 0
    with get_session() as s:
        for _, linha in df.iterrows():
            row = {k: (None if pd.isna(v) else v) for k, v in linha.items()}
            count += _processar_linha(s, row)
    return count


def _importar_csv(caminho: str) -> int:
    try:
        with open(caminho, "r", encoding="utf-8", newline="") as f:
            amostra = f.read(4096)
            f.seek(0)
            try:
                dialeto = csv.Sniffer().sniff(amostra, delimiters=",;")
            except csv.Error:
                dialeto = csv.excel
            reader = csv.DictReader(f, dialect=dialeto)
            linhas = [
                {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
                for row in reader
            ]
    except Exception as erro:
        raise ValueError(f"Erro ao ler o arquivo CSV: {erro}")

    count = 0
    with get_session() as s:
        for row in linhas:
            count += _processar_linha(s, row)
    return count


def _processar_linha(session, row: dict) -> int:
    telefone_bruto = _pegar_campo(row, COLUNAS["phone"])
    if not telefone_bruto:
        return 0

    telefone = normalizar_telefone(telefone_bruto)
    existente = session.execute(select(Person).where(Person.phone == telefone)).scalar_one_or_none()
    if existente:
        return 0

    nome_completo = _pegar_campo(row, COLUNAS["name"])
    if not nome_completo:
        primeiro = _pegar_campo(row, COLUNAS["primeiro_nome"]) or ""
        ultimo   = _pegar_campo(row, COLUNAS["ultimo_nome"]) or ""
        nome_completo = f"{primeiro} {ultimo}".strip()

    pessoa = Person(
        name=nome_completo or "Sem nome",
        phone=telefone,
        neighborhood=_pegar_campo(row, COLUNAS["neighborhood"]),
        ubs=_pegar_campo(row, COLUNAS["ubs"]),
        birthdate=_pegar_campo(row, COLUNAS["birthdate"]),
        email=_pegar_campo(row, COLUNAS["email"]),
        cep=_pegar_campo(row, COLUNAS["cep"]),
        raca_cor=_pegar_campo(row, COLUNAS["raca_cor"]),
        created_at=agora_utc(),
    )
    session.add(pessoa)
    session.commit()
    session.refresh(pessoa)

    session.add(Invitation(person_id=pessoa.id, status="pending", updated_at=agora_utc()))
    session.commit()
    return 1


class _SafeDict(dict):
    def __missing__(self, key):
        return f"{{{key}}}"


def enviar_convites_pendentes(template: str, limite: int = 50) -> dict:
    enviados  = 0
    erros     = 0
    ignorados = 0
    telefones_usados = set()

    with get_session() as s:
        convites = s.execute(
            select(Invitation).where(Invitation.status == "pending").limit(limite)
        ).scalars().all()

        for convite in convites:
            pessoa = s.get(Person, convite.person_id)

            if (not pessoa or not pessoa.phone
                    or pessoa.consent_optout
                    or pessoa.phone in telefones_usados):
                convite.status     = "skipped"
                convite.updated_at = agora_utc()
                s.commit()
                ignorados += 1
                continue

            primeiro, ultimo = separar_nome(pessoa.name or "")
            ubs = (pessoa.ubs or "UBS").strip()
            contexto = _SafeDict(primeiro_nome=primeiro, ultimo_nome=ultimo, ubs=ubs, UBS=ubs.upper())
            mensagem = template.format_map(contexto)

            resultado = send_message_phone(pessoa.phone, mensagem)

            if resultado.get("ok"):
                convite.status  = "sent"
                convite.sent_at = agora_utc()
                telefones_usados.add(pessoa.phone)
                enviados += 1
            else:
                convite.status = "error"
                erros += 1

            convite.updated_at = agora_utc()
            s.commit()

    return {"enviados": enviados, "erros": erros, "ignorados": ignorados}


def agendar_consulta(person_id: int, when: str, place: str) -> Appointment:
    with get_session() as s:
        agendamento = Appointment(
            person_id=person_id, when=when, place=place,
            status="scheduled", created_at=agora_utc(),
        )
        s.add(agendamento)
        s.commit()
        s.refresh(agendamento)

        pessoa = s.get(Person, person_id)
        if pessoa and pessoa.phone:
            when_br = formatar_when_br(when)
            send_message_phone(
                pessoa.phone,
                f"✅ Olá, {pessoa.name.split()[0]}! "
                f"Sua coleta preventiva está agendada para *{when_br}* "
                f"na *{place}*. 💚"
            )
        return agendamento


def calcular_metricas() -> dict:
    with get_session() as s:
        total_pessoas      = s.execute(select(func.count(Person.id))).scalar_one()
        total_agendamentos = s.execute(select(func.count(Appointment.id))).scalar_one()

        rows_status = s.execute(
            select(Invitation.status, func.count(Invitation.id)).group_by(Invitation.status)
        ).all()
        convites_por_status = {r[0]: r[1] for r in rows_status}

        enviados  = sum(convites_por_status.get(st, 0) for st in ("sent", "delivered", "read", "responded"))
        pendentes = convites_por_status.get("pending", 0)
        erros     = convites_por_status.get("error", 0)

        ubs_rows = s.execute(
            select(Person.ubs, func.count(Person.id))
            .where(Person.ubs.isnot(None))
            .group_by(Person.ubs)
            .order_by(func.count(Person.id).desc())
            .limit(8)
        ).all()

        faixas = _calcular_faixas_etarias(s)
        cobertura = round((enviados / total_pessoas * 100), 1) if total_pessoas > 0 else 0.0

        agend_rows = s.execute(
            select(Appointment.status, func.count(Appointment.id)).group_by(Appointment.status)
        ).all()
        agend_por_status = {r[0]: r[1] for r in agend_rows}

        return {
            "pessoas":       total_pessoas,
            "inv_enviados":  enviados,
            "inv_pendentes": pendentes,
            "agendamentos":  total_agendamentos,
            "cobertura":     cobertura,
            "inv_erros":     erros,
            "chart_status": {
                "labels": ["Enviados", "Pendentes", "Erros", "Ignorados"],
                "data":   [enviados, pendentes, erros, convites_por_status.get("skipped", 0)],
            },
            "chart_ubs": {
                "labels": [r[0] or "Não informada" for r in ubs_rows],
                "data":   [r[1] for r in ubs_rows],
            },
            "chart_faixas": faixas,
            "agend_scheduled": agend_por_status.get("scheduled", 0),
            "agend_done":      agend_por_status.get("done", 0),
            "agend_cancelled": agend_por_status.get("cancelled", 0),
        }


def _calcular_faixas_etarias(session) -> dict:
    rows      = session.execute(select(Person.birthdate)).scalars().all()
    ano_atual = datetime.now().year
    faixas    = {"25-34": 0, "35-44": 0, "45-54": 0, "55-64": 0, "Outras": 0}

    for birthdate in rows:
        ano = _extrair_ano_nascimento(birthdate)
        if not ano:
            faixas["Outras"] += 1
            continue
        idade = ano_atual - ano
        if   25 <= idade <= 34: faixas["25-34"] += 1
        elif 35 <= idade <= 44: faixas["35-44"] += 1
        elif 45 <= idade <= 54: faixas["45-54"] += 1
        elif 55 <= idade <= 64: faixas["55-64"] += 1
        else:                   faixas["Outras"] += 1

    return {"labels": list(faixas.keys()), "data": list(faixas.values())}


def _extrair_ano_nascimento(birthdate) -> Optional[int]:
    if not birthdate:
        return None
    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"]:
        try:
            return datetime.strptime(str(birthdate).strip(), fmt).year
        except ValueError:
            continue
    match = re.search(r"\b(19|20)\d{2}\b", str(birthdate))
    return int(match.group()) if match else None


def listar_pacientes(pagina=1, por_pagina=20, busca="", ubs_filtro="", status_filtro="") -> dict:
    with get_session() as s:
        query = select(Person)
        if busca:
            termo = f"%{busca}%"
            query = query.where(Person.name.ilike(termo) | Person.phone.ilike(termo))
        if ubs_filtro:
            query = query.where(Person.ubs == ubs_filtro)

        total  = s.execute(select(func.count()).select_from(query.subquery())).scalar_one()
        offset = (pagina - 1) * por_pagina
        pessoas = s.execute(query.offset(offset).limit(por_pagina)).scalars().all()

        resultado = []
        for pessoa in pessoas:
            ult = s.execute(
                select(Invitation)
                .where(Invitation.person_id == pessoa.id)
                .order_by(Invitation.id.desc())
            ).scalars().first()

            status_atual = ult.status if ult else "sem convite"
            if status_filtro and status_atual != status_filtro:
                continue

            resultado.append({
                "id":        pessoa.id,
                "name":      pessoa.name,
                "phone":     pessoa.phone,
                "ubs":       pessoa.ubs or "—",
                "birthdate": pessoa.birthdate or "—",
                "status":    status_atual,
                "optout":    pessoa.consent_optout,
            })

        total_paginas = max(1, -(-total // por_pagina))
        return {"pacientes": resultado, "total": total, "pagina": pagina,
                "por_pagina": por_pagina, "total_paginas": total_paginas}


def listar_ubs() -> list:
    with get_session() as s:
        rows = s.execute(
            select(Person.ubs).where(Person.ubs.isnot(None)).distinct().order_by(Person.ubs)
        ).scalars().all()
        return [u for u in rows if u]


def listar_agendamentos(pagina=1, por_pagina=20) -> dict:
    with get_session() as s:
        total = s.execute(select(func.count(Appointment.id))).scalar_one()
        offset = (pagina - 1) * por_pagina
        ags = s.execute(
            select(Appointment).order_by(Appointment.id.desc()).offset(offset).limit(por_pagina)
        ).scalars().all()

        resultado = []
        for ag in ags:
            pessoa = s.get(Person, ag.person_id)
            resultado.append({
                "id":     ag.id,
                "nome":   pessoa.name if pessoa else "—",
                "phone":  pessoa.phone if pessoa else "—",
                "when":   ag.when or "—",
                "place":  ag.place or "—",
                "status": ag.status,
            })

        total_paginas = max(1, -(-total // por_pagina))
        return {"agendamentos": resultado, "total": total, "pagina": pagina,
                "total_paginas": total_paginas}


def processar_resposta_whatsapp(phone_de: str, corpo: str) -> str:
    texto    = (corpo or "").strip().upper()
    telefone = normalizar_telefone(phone_de)

    with get_session() as s:
        pessoa = s.execute(select(Person).where(Person.phone == telefone)).scalar_one_or_none()

        if not pessoa:
            return "Olá! Não encontrei seu cadastro. Entre em contato com a sua UBS. 🏥"

        primeiro = (pessoa.name or "").split()[0] if pessoa.name else "você"

        if texto in {"PARAR", "STOP", "NAO", "NÃO", "N", "CANCELAR"}:
            pessoa.consent_optout = True
            s.commit()
            return f"Entendido, {primeiro}. Você não receberá mais mensagens. 💚"

        if texto in {"SIM", "OK", "S", "QUERO", "ACEITO", "1"}:
            ult = s.execute(
                select(Invitation).where(Invitation.person_id == pessoa.id)
                .order_by(Invitation.id.desc())
            ).scalars().first()
            if ult:
                ult.status     = "responded"
                ult.response   = "SIM"
                ult.updated_at = agora_utc()

            ubs = pessoa.ubs or "sua UBS"
            s.add(Appointment(person_id=pessoa.id, when=None, place=ubs,
                              status="scheduled", created_at=agora_utc()))
            s.commit()
            return (f"Ótimo, {primeiro}! 🎉 Em breve a equipe da *{ubs}* "
                    f"entrará em contato para confirmar o horário. 💚")

        return (f"Olá, {primeiro}! Não entendi. 😊\n"
                f"Responda *SIM* para agendar ou *PARAR* para cancelar.")