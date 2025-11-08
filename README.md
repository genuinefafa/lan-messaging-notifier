# lan-messaging-notifier

Tool to centralize local home or work network to support notifications

A centralized notification service for your LAN that receives messages via REST API and forwards them to multiple platforms: Slack, Telegram, and WhatsApp.

## Features

- **Multi-platform support**: Send notifications to Slack, Telegram, and WhatsApp
- **REST API**: Simple HTTP API for sending messages from any application
- **Flexible configuration**: Enable only the platforms you need
- **Docker support**: Easy deployment with Docker and docker-compose
- **Health checks**: Monitor service status and platform connectivity
- **Comprehensive logging**: Track all notification activity
- **Well-tested**: Unit tests with pytest

## Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/genuinefafa/lan-messaging-notifier.git
cd lan-messaging-notifier
```

2. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and tokens
```

3. Start the service:
```bash
docker-compose up -d
```

The service will be available at `http://localhost:5000`

### Manual Installation

1. Install Python 3.11+

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Run the service:
```bash
python -m src.app
# Or use the helper script:
chmod +x run.sh
./run.sh
```

## Configuration

Configure the service by setting environment variables in `.env` file:

### Flask Configuration
```bash
DEBUG=false          # Enable debug mode
HOST=0.0.0.0        # Listen on all interfaces
PORT=5000           # Service port
```

### Slack Configuration
```bash
SLACK_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL=#general
```

To get a Slack token:
1. Create a Slack App at https://api.slack.com/apps
2. Add `chat:write` bot scope
3. Install app to workspace
4. Copy the Bot User OAuth Token

### Telegram Configuration
```bash
TELEGRAM_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

To get Telegram credentials:
1. Message @BotFather on Telegram
2. Create a new bot with `/newbot`
3. Copy the token
4. Get your chat ID by messaging @userinfobot

### WhatsApp Configuration (via Twilio)
```bash
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_FROM_NUMBER=whatsapp:+14155238886
WHATSAPP_TO_NUMBER=whatsapp:+1234567890
```

To get Twilio credentials:
1. Sign up at https://www.twilio.com
2. Get your Account SID and Auth Token from console
3. Set up WhatsApp sandbox or production number

**Note**: At least one platform must be configured for the service to start.

## API Usage

### Health Check
```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "enabled_platforms": ["slack", "telegram"],
  "version": "0.1.0"
}
```

### Test Connections
```bash
curl http://localhost:5000/test
```

Response:
```json
{
  "slack": {"success": true, "error": null},
  "telegram": {"success": true, "error": null}
}
```

### Send Notification
```bash
curl -X POST http://localhost:5000/notify \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from LAN!",
    "platforms": ["slack", "telegram"]
  }'
```

Response:
```json
{
  "message": "Notifications sent",
  "total_platforms": 2,
  "successful": 2,
  "results": {
    "slack": {"success": true, "error": null},
    "telegram": {"success": true, "error": null}
  }
}
```

**Parameters**:
- `message` (required): The message text to send
- `platforms` (optional): Array of platforms to send to. Defaults to all enabled platforms.

## Project Structure

```
lan-messaging-notifier/
├── src/
│   ├── __init__.py
│   ├── app.py              # Flask application
│   ├── config.py           # Configuration management
│   ├── notifiers/          # Notification platform integrations
│   │   ├── __init__.py
│   │   ├── base.py         # Abstract base class
│   │   ├── slack.py        # Slack integration
│   │   ├── telegram.py     # Telegram integration
│   │   └── whatsapp.py     # WhatsApp/Twilio integration
│   └── utils/
│       ├── __init__.py
│       └── logger.py       # Logging configuration
├── tests/                  # Unit tests
├── .env.example           # Example environment file
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker compose configuration
└── README.md            # This file
```

## Development

### Running Tests
```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Use Cases

- **Home automation**: Send alerts from home automation scripts
- **Server monitoring**: Get notifications when servers have issues
- **Build notifications**: Alert team when builds complete
- **IoT devices**: Send alerts from IoT sensors and devices
- **Log alerts**: Forward important log messages to messaging platforms
- **Backup notifications**: Get notified when backups complete

## Example: Sending from Python

```python
import requests

def send_notification(message, platforms=None):
    response = requests.post(
        'http://localhost:5000/notify',
        json={
            'message': message,
            'platforms': platforms or ['slack', 'telegram', 'whatsapp']
        }
    )
    return response.json()

# Usage
send_notification('Backup completed successfully!')
```

## Example: Sending from Bash

```bash
#!/bin/bash
MESSAGE="Deployment completed at $(date)"

curl -X POST http://localhost:5000/notify \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"$MESSAGE\", \"platforms\": [\"slack\"]}"
```

## Troubleshooting

### Service won't start
- Check that at least one platform is configured in `.env`
- Verify all required environment variables are set
- Check logs for specific error messages

### Messages not sending
- Use `/test` endpoint to verify platform connectivity
- Check that tokens/credentials are correct
- Verify network connectivity to platform APIs

### Docker issues
- Ensure `.env` file exists and is properly formatted
- Check docker logs: `docker-compose logs -f`
- Verify port 5000 is not in use

## Security Considerations

- **API Keys**: Never commit `.env` file or expose API keys
- **Network**: Consider using a reverse proxy with authentication
- **Firewall**: Restrict access to trusted LAN devices only
- **HTTPS**: Use HTTPS in production environments
- **Rate limiting**: Consider implementing rate limiting for production use

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing issues for solutions

## Roadmap

Potential future enhancements:
- [ ] Message templates and formatting
- [ ] Message queuing for reliability
- [ ] Web UI for configuration and testing
- [ ] Support for more platforms (Discord, Matrix, etc.)
- [ ] Message scheduling
- [ ] Authentication/API keys
- [ ] Rate limiting
- [ ] Metrics and analytics

---

Built with Python, Flask, and modern notification APIs.
