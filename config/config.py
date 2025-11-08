import os

# Configuración de Slack
SLACK_TOKEN = os.getenv('SLACK_TOKEN')

# Configuración de Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')  # ID del chat o canal

# Configuración de Twilio para WhatsApp
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')  # Número de WhatsApp de Twilio
TARGET_WHATSAPP_NUMBER = os.getenv('TARGET_WHATSAPP_NUMBER')  # Número destinatario
