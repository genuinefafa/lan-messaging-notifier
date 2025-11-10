"""Telegram notifier implementation."""

from typing import Dict, Any
from telegram import Bot
from telegram.error import TelegramError

from .base import BaseNotifier
from ..utils.logger import logger


class TelegramNotifier(BaseNotifier):
    """Notificador para Telegram usando python-telegram-bot."""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el notificador de Telegram.

        Args:
            config: Diccionario con 'token' y 'chat_id'
        """
        self.bot: Bot | None = None
        super().__init__(config)

    def validate_config(self) -> None:
        """Valida la configuración de Telegram."""
        if 'token' not in self.config or not self.config['token']:
            raise ValueError("Telegram token is required")

        if 'chat_id' not in self.config or not self.config['chat_id']:
            raise ValueError("Telegram chat_id is required")

        # Initialize bot
        self.bot = Bot(token=self.config['token'])

    def send_message(self, message: str, **kwargs) -> bool:
        """
        Envía un mensaje a Telegram.

        Args:
            message: El mensaje a enviar
            **kwargs: Puede incluir 'chat_id' para override del chat default

        Returns:
            True si el mensaje se envió exitosamente

        Raises:
            TelegramError: Si hay un error con la API de Telegram
        """
        if not self.bot:
            raise RuntimeError("Telegram bot not initialized")

        chat_id = kwargs.get('chat_id', self.config['chat_id'])

        try:
            # Use asyncio.run() to safely handle async call
            import asyncio

            async def send():
                return await self.bot.send_message(
                    chat_id=chat_id,
                    text=message
                )

            result = asyncio.run(send())

            logger.info(f"Message sent to Telegram chat {chat_id}: {result.message_id}")
            return True

        except TelegramError as e:
            logger.error(f"Error sending message to Telegram: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """
        Prueba la conexión con Telegram.

        Returns:
            True si el bot está configurado correctamente
        """
        if not self.bot:
            return False

        try:
            import asyncio

            async def get_me():
                return await self.bot.get_me()

            me = asyncio.run(get_me())

            logger.info(f"Telegram connection OK - Bot: @{me.username}")
            return True

        except TelegramError as e:
            logger.error(f"Telegram connection failed: {str(e)}")
            return False
