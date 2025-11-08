# LAN Messaging Notifier

Un sistema centralizado para recibir mensajes de aplicaciones en la red local (LAN) y enviar notificaciones a plataformas externas como Slack, Telegram y WhatsApp.

## Funcionalidades
- Recibe mensajes vía API REST desde apps en LAN.
- Envía notificaciones a Slack, Telegram y WhatsApp.
- Configurable para diferentes plataformas.

## Instalación
1. Clona el repo: `git clone https://github.com/genuinefafa/lan-messaging-notifier.git`
2. Instala dependencias: `pip install -r requirements.txt`
3. Configura las claves API en `config/config.py`.
4. Ejecuta: `python app/main.py`

## Uso
Envía un POST a `http://localhost:5000/notify` con JSON: `{"message": "Hola mundo", "platforms": ["slack", "telegram", "whatsapp"]}`

## Configuración
- **Slack**: Usa `slack-sdk`. Necesitas un token de bot.
- **Telegram**: Usa `python-telegram-bot`. Necesitas un bot token de @BotFather.
- **WhatsApp**: Usa `twilio`. Necesitas SID y auth token de Twilio.

## Contribuir
Crea issues o PRs en este repo.
