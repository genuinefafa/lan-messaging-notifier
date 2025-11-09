"""WhatsApp notifier implementation using Twilio."""

from typing import Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from .base import BaseNotifier
from ..utils.logger import logger


class WhatsAppNotifier(BaseNotifier):
    """Notificador para WhatsApp usando Twilio."""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el notificador de WhatsApp.

        Args:
            config: Diccionario con 'account_sid', 'auth_token', 'from_number', 'to_number'
        """
        self.client: Client | None = None
        super().__init__(config)

    def validate_config(self) -> None:
        """Valida la configuración de WhatsApp/Twilio."""
        required_fields = ['account_sid', 'auth_token', 'from_number', 'to_number']

        for field in required_fields:
            if field not in self.config or not self.config[field]:
                raise ValueError(f"WhatsApp {field} is required")

        # Ensure numbers have whatsapp: prefix
        if not self.config['from_number'].startswith('whatsapp:'):
            self.config['from_number'] = f"whatsapp:{self.config['from_number']}"

        if not self.config['to_number'].startswith('whatsapp:'):
            self.config['to_number'] = f"whatsapp:{self.config['to_number']}"

        # Initialize Twilio client
        self.client = Client(
            self.config['account_sid'],
            self.config['auth_token']
        )

    def send_message(self, message: str, **kwargs) -> bool:
        """
        Envía un mensaje a WhatsApp vía Twilio.

        Args:
            message: El mensaje a enviar
            **kwargs: Puede incluir 'to_number' para override del número default

        Returns:
            True si el mensaje se envió exitosamente

        Raises:
            TwilioRestException: Si hay un error con la API de Twilio
        """
        if not self.client:
            raise RuntimeError("Twilio client not initialized")

        to_number = kwargs.get('to_number', self.config['to_number'])

        # Ensure to_number has whatsapp: prefix
        if not to_number.startswith('whatsapp:'):
            to_number = f"whatsapp:{to_number}"

        try:
            twilio_message = self.client.messages.create(
                body=message,
                from_=self.config['from_number'],
                to=to_number
            )
            logger.info(
                f"Message sent to WhatsApp {to_number}: SID={twilio_message.sid}, "
                f"Status={twilio_message.status}"
            )
            return True

        except TwilioRestException as e:
            logger.error(f"Error sending message to WhatsApp: {e.msg}")
            raise

    def test_connection(self) -> bool:
        """
        Prueba la conexión con Twilio.

        Returns:
            True si las credenciales son válidas
        """
        if not self.client:
            return False

        try:
            # Try to fetch account info to validate credentials
            account = self.client.api.accounts(self.config['account_sid']).fetch()
            logger.info(
                f"Twilio connection OK - Account: {account.friendly_name}, "
                f"Status: {account.status}"
            )
            return True

        except TwilioRestException as e:
            logger.error(f"Twilio connection failed: {e.msg}")
            return False
