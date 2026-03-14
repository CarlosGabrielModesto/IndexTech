"""
Script de teste de envio via Twilio WhatsApp.

Uso:
    python scripts/send_test.py

Pré-requisitos:
    - Arquivo .env configurado na raiz do projeto
    - Variáveis TWILIO_* preenchidas corretamente
    - Número TWILIO_WHATSAPP_TO deve ter aceitado o Sandbox
      (enviar "join <palavra>" para o número do Sandbox)
"""

import os
import sys
from pathlib import Path

# Garante que o projeto raiz esteja no path, mesmo rodando da pasta scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.notify import send_message_phone

def main():
    destinatario = os.getenv("TWILIO_WHATSAPP_TO", "").replace("whatsapp:", "")

    if not destinatario:
        print("❌ Variável TWILIO_WHATSAPP_TO não encontrada no .env")
        sys.exit(1)

    print(f"📱 Enviando mensagem de teste para: {destinatario}")
    print(f"   Modo: {os.getenv('NOTIFIER', 'console')}\n")

    mensagem = (
        "🧪 *Teste Hygeia Digital*\n\n"
        "Olá! Esta é uma mensagem de teste do sistema Hygeia Digital.\n"
        "Se você recebeu esta mensagem, a integração está funcionando. ✅\n\n"
        "Responda *SIM* para confirmar o recebimento."
    )

    resultado = send_message_phone(destinatario, mensagem)

    if resultado.get("ok"):
        print("✅ Mensagem enviada com sucesso!")
        if "sid" in resultado:
            print(f"   SID Twilio: {resultado['sid']}")
    else:
        print(f"❌ Falha no envio: {resultado.get('err', 'Erro desconhecido')}")
        sys.exit(1)

if __name__ == "__main__":
    main()