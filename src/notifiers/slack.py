"""Slack notifier implementation."""

from typing import Dict, Any, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .base import BaseNotifier
from ..utils.logger import logger


class SlackNotifier(BaseNotifier):
    """Notificador para Slack usando slack-sdk."""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el notificador de Slack.

        Args:
            config: Diccionario con 'token' y opcionalmente 'channel'
        """
        self.client: Optional[WebClient] = None
        super().__init__(config)

    def validate_config(self) -> None:
        """Valida la configuración de Slack."""
        if 'token' not in self.config or not self.config['token']:
            raise ValueError("Slack token is required")

        if 'channel' not in self.config:
            self.config['channel'] = '#general'

        # Initialize client
        self.client = WebClient(token=self.config['token'])

    def send_message(self, message: str, **kwargs) -> bool:
        """
        Envía un mensaje a Slack.

        Args:
            message: El mensaje a enviar
            **kwargs: Puede incluir 'channel' para override del canal default

        Returns:
            True si el mensaje se envió exitosamente

        Raises:
            SlackApiError: Si hay un error con la API de Slack
        """
        if not self.client:
            raise RuntimeError("Slack client not initialized")

        channel = kwargs.get('channel', self.config['channel'])

        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message
            )
            logger.info(f"Message sent to Slack channel {channel}: {response['ts']}")
            return True

        except SlackApiError as e:
            logger.error(f"Error sending message to Slack: {e.response['error']}")
            raise

    def test_connection(self) -> bool:
        """
        Prueba la conexión con Slack.

        Returns:
            True si la autenticación es válida
        """
        if not self.client:
            return False

        try:
            response = self.client.auth_test()
            logger.info(f"Slack connection OK - Team: {response['team']}, User: {response['user']}")
            return True
        except SlackApiError as e:
            logger.error(f"Slack connection failed: {e.response['error']}")
            return False
