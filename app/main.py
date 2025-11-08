from flask import Flask, request, jsonify
import slack_sdk
import telegram
from twilio.rest import Client
from config.config import SLACK_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, TARGET_WHATSAPP_NUMBER

app = Flask(__name__)

# Función para enviar a Slack
def send_to_slack(message):
    client = slack_sdk.WebClient(token=SLACK_TOKEN)
    client.chat_postMessage(channel='#general', text=message)  # Cambia el canal

# Función para enviar a Telegram
def send_to_telegram(message):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

# Función para enviar a WhatsApp vía Twilio
def send_to_whatsapp(message):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=f'whatsapp:{TWILIO_WHATSAPP_NUMBER}',
        to=f'whatsapp:{TARGET_WHATSAPP_NUMBER}'
    )

@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()
    message = data.get('message')
    platforms = data.get('platforms', [])
    
    if not message:
        return jsonify({'error': 'Mensaje requerido'}), 400
    
    if 'slack' in platforms:
        send_to_slack(message)
    if 'telegram' in platforms:
        send_to_telegram(message)
    if 'whatsapp' in platforms:
        send_to_whatsapp(message)
    
    return jsonify({'status': 'Enviado'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Escucha en todas las interfaces para LAN
