"""Configuration management for the notifier service."""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SlackConfig:
    """Slack configuration."""
    token: Optional[str]
    channel: str = "#general"

    def is_enabled(self) -> bool:
        return bool(self.token)


@dataclass
class TelegramConfig:
    """Telegram configuration."""
    token: Optional[str]
    chat_id: Optional[str]

    def is_enabled(self) -> bool:
        return bool(self.token and self.chat_id)


@dataclass
class WhatsAppConfig:
    """WhatsApp (Twilio) configuration."""
    account_sid: Optional[str]
    auth_token: Optional[str]
    from_number: Optional[str]
    to_number: Optional[str]

    def is_enabled(self) -> bool:
        return bool(
            self.account_sid
            and self.auth_token
            and self.from_number
            and self.to_number
        )


class Config:
    """Main configuration class."""

    def __init__(self):
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.host = os.getenv('HOST', '0.0.0.0')
        self.port = int(os.getenv('PORT', '5000'))

        # Slack config
        self.slack = SlackConfig(
            token=os.getenv('SLACK_TOKEN'),
            channel=os.getenv('SLACK_CHANNEL', '#general')
        )

        # Telegram config
        self.telegram = TelegramConfig(
            token=os.getenv('TELEGRAM_TOKEN'),
            chat_id=os.getenv('TELEGRAM_CHAT_ID')
        )

        # WhatsApp config
        self.whatsapp = WhatsAppConfig(
            account_sid=os.getenv('TWILIO_ACCOUNT_SID'),
            auth_token=os.getenv('TWILIO_AUTH_TOKEN'),
            from_number=os.getenv('TWILIO_FROM_NUMBER'),
            to_number=os.getenv('WHATSAPP_TO_NUMBER')
        )

    def get_enabled_platforms(self) -> list[str]:
        """Get list of enabled notification platforms."""
        platforms = []
        if self.slack.is_enabled():
            platforms.append('slack')
        if self.telegram.is_enabled():
            platforms.append('telegram')
        if self.whatsapp.is_enabled():
            platforms.append('whatsapp')
        return platforms

    def validate(self) -> None:
        """
        Validate that at least one platform is configured.

        Raises:
            RuntimeError: If no platforms are configured
        """
        enabled = self.get_enabled_platforms()
        if not enabled:
            raise RuntimeError(
                "No notification platforms configured. "
                "Please set at least one platform's credentials."
            )


# Global config instance
config = Config()
