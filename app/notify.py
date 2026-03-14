"""
Módulo de notificações — envio de mensagens para as pacientes.

Suporta três modos de operação, controlados pela variável NOTIFIER no .env:

  console  → imprime a mensagem no terminal (ideal para desenvolvimento)
  twilio   → envia via WhatsApp usando a API da Twilio
  whatsapp → envia via Meta Cloud API (WhatsApp Business)

Para trocar de modo, basta alterar NOTIFIER no .env — nenhuma linha de
código precisa ser modificada.
"""

import os
import httpx
from datetime import datetime


def _formatar_whatsapp(numero: str) -> str:
    """
    Garante que o número esteja no formato aceito pelo WhatsApp/Twilio.
    Exemplo: +5514999999999 → whatsapp:+5514999999999
    """
    if str(numero).startswith("whatsapp:"):
        return numero
    return f"whatsapp:{numero}"


def send_message_phone(phone: str, text: str) -> dict:
    """
    Envia uma mensagem de texto para o número informado.

    Parâmetros:
        phone: número da destinatária no formato E.164 (+55DDDNNNNNNNNN)
        text:  conteúdo da mensagem a ser enviada

    Retorna um dicionário com:
        ok   → True se o envio foi bem-sucedido
        mode → qual modo foi utilizado (console, twilio, whatsapp)
        err  → descrição do erro, caso ok seja False
    """
    # Lê o modo de envio a cada chamada para respeitar mudanças no .env em tempo de execução
    modo = os.getenv("NOTIFIER", "console").strip().lower()

    # ------------------------------------------------------------------
    # Modo CONSOLE — apenas imprime no terminal, sem enviar nada de fato
    # ------------------------------------------------------------------
    if modo == "console":
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{timestamp}] 📱 MENSAGEM → {phone}")
        print(f"    {text}")
        print()
        return {"ok": True, "mode": "console"}

    # ------------------------------------------------------------------
    # Modo TWILIO — envia via WhatsApp Sandbox ou número aprovado
    # ------------------------------------------------------------------
    if modo == "twilio":
        try:
            from twilio.rest import Client
        except ImportError:
            return {"ok": False, "err": "Biblioteca twilio não instalada. Execute: pip install twilio"}

        sid       = os.getenv("TWILIO_ACCOUNT_SID")
        token     = os.getenv("TWILIO_AUTH_TOKEN")
        remetente = os.getenv("TWILIO_WHATSAPP_FROM")

        # Valida que todas as variáveis necessárias estão presentes
        if not all([sid, token, remetente]):
            return {
                "ok": False,
                "err": "Variáveis TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN e TWILIO_WHATSAPP_FROM são obrigatórias."
            }

        try:
            client = Client(sid, token)
            mensagem = client.messages.create(
                from_=_formatar_whatsapp(remetente),
                to=_formatar_whatsapp(phone),
                body=text,
            )
            return {"ok": True, "mode": "twilio", "sid": mensagem.sid}
        except Exception as erro:
            return {"ok": False, "err": str(erro)}

    # ------------------------------------------------------------------
    # Modo WHATSAPP — envia via Meta Cloud API
    # ------------------------------------------------------------------
    if modo == "whatsapp":
        token_meta   = os.getenv("WABA_TOKEN")
        phone_id     = os.getenv("WABA_PHONE_ID")

        if not all([token_meta, phone_id]):
            return {"ok": False, "err": "Variáveis WABA_TOKEN e WABA_PHONE_ID são obrigatórias."}

        url     = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
        headers = {"Authorization": f"Bearer {token_meta}"}
        payload = {
            "messaging_product": "whatsapp",
            "to":   phone,
            "type": "text",
            "text": {"body": text},
        }

        try:
            with httpx.Client(timeout=15) as client:
                resposta = client.post(url, headers=headers, json=payload)
                resposta.raise_for_status()
                return {"ok": True, "mode": "whatsapp", "resp": resposta.json()}
        except httpx.HTTPStatusError as erro:
            return {"ok": False, "err": f"HTTP {erro.response.status_code}: {erro.response.text}"}
        except Exception as erro:
            return {"ok": False, "err": str(erro)}

    # Modo desconhecido
    return {"ok": False, "err": f"NOTIFIER inválido: '{modo}'. Use: console, twilio ou whatsapp."}