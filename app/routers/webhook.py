"""
Router do webhook Twilio.

O Twilio chama este endpoint sempre que uma paciente responde
uma mensagem no WhatsApp. A rota processa a resposta e devolve
um TwiML com a mensagem de retorno.

Para receber webhooks localmente, use o ngrok:
    ngrok http 8000
    
Configure a URL no Twilio Console:
    https://seu-id.ngrok.io/twilio/webhook
"""

from fastapi import APIRouter, Form, Response

from app.service import processar_resposta_whatsapp

router = APIRouter(prefix="/twilio", tags=["Webhook"])


@router.post("/webhook")
async def webhook_whatsapp(
    From: str = Form(...),
    Body: str = Form(default=""),
):
    """
    Recebe mensagens de WhatsApp via Twilio e responde automaticamente.

    O Twilio envia os campos 'From' e 'Body' como form-data.
    A resposta deve ser um XML no formato TwiML.

    Parâmetros (enviados pelo Twilio):
        From: número de quem enviou (ex: whatsapp:+5514999999999)
        Body: texto da mensagem
    """
    # Processa a resposta da paciente e gera a mensagem de retorno
    resposta = processar_resposta_whatsapp(From, Body)

    # Constrói o TwiML (formato XML que o Twilio espera como resposta)
    # O Twilio usa essa resposta para enviar a mensagem de volta à paciente
    twiml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Message>{resposta}</Message></Response>"
    )

    return Response(content=twiml, media_type="application/xml")


@router.get("/webhook")
async def webhook_verificacao():
    """
    Endpoint GET para verificação de conectividade.
    Algumas plataformas fazem um GET antes de configurar o webhook.
    """
    return {"status": "ok", "mensagem": "Webhook Hygeia Digital ativo."}