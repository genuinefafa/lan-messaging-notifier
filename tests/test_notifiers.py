"""Tests for notifiers."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.notifiers.base import BaseNotifier
from src.notifiers.slack import SlackNotifier
from src.notifiers.telegram import TelegramNotifier
from src.notifiers.whatsapp import WhatsAppNotifier


class TestSlackNotifier:
    """Tests for SlackNotifier."""

    def test_validate_config_missing_token(self):
        """Test that validation fails when token is missing."""
        with pytest.raises(ValueError, match="Slack token is required"):
            SlackNotifier({})

    def test_validate_config_success(self):
        """Test that validation succeeds with valid config."""
        notifier = SlackNotifier({'token': 'xoxb-test-token'})
        assert notifier.config['token'] == 'xoxb-test-token'
        assert notifier.config['channel'] == '#general'

    @patch('src.notifiers.slack.WebClient')
    def test_send_message_success(self, mock_web_client):
        """Test sending a message successfully."""
        mock_client = Mock()
        mock_client.chat_postMessage.return_value = {'ts': '1234567890.123456'}
        mock_web_client.return_value = mock_client

        notifier = SlackNotifier({'token': 'xoxb-test-token'})
        result = notifier.send_message('Test message')

        assert result is True
        mock_client.chat_postMessage.assert_called_once_with(
            channel='#general',
            text='Test message'
        )

    def test_get_name(self):
        """Test get_name returns correct name."""
        notifier = SlackNotifier({'token': 'xoxb-test-token'})
        assert notifier.get_name() == 'slack'


class TestTelegramNotifier:
    """Tests for TelegramNotifier."""

    def test_validate_config_missing_token(self):
        """Test that validation fails when token is missing."""
        with pytest.raises(ValueError, match="Telegram token is required"):
            TelegramNotifier({})

    def test_validate_config_missing_chat_id(self):
        """Test that validation fails when chat_id is missing."""
        with pytest.raises(ValueError, match="Telegram chat_id is required"):
            TelegramNotifier({'token': 'test-token'})

    def test_validate_config_success(self):
        """Test that validation succeeds with valid config."""
        notifier = TelegramNotifier({
            'token': 'test-token',
            'chat_id': '123456789'
        })
        assert notifier.config['token'] == 'test-token'
        assert notifier.config['chat_id'] == '123456789'

    def test_get_name(self):
        """Test get_name returns correct name."""
        notifier = TelegramNotifier({
            'token': 'test-token',
            'chat_id': '123456789'
        })
        assert notifier.get_name() == 'telegram'


class TestWhatsAppNotifier:
    """Tests for WhatsAppNotifier."""

    def test_validate_config_missing_fields(self):
        """Test that validation fails when required fields are missing."""
        with pytest.raises(ValueError, match="WhatsApp account_sid is required"):
            WhatsAppNotifier({})

    def test_validate_config_adds_whatsapp_prefix(self):
        """Test that whatsapp: prefix is added to numbers."""
        with patch('src.notifiers.whatsapp.Client'):
            notifier = WhatsAppNotifier({
                'account_sid': 'test-sid',
                'auth_token': 'test-token',
                'from_number': '+14155238886',
                'to_number': '+1234567890'
            })
            assert notifier.config['from_number'] == 'whatsapp:+14155238886'
            assert notifier.config['to_number'] == 'whatsapp:+1234567890'

    @patch('src.notifiers.whatsapp.Client')
    def test_send_message_success(self, mock_client_class):
        """Test sending a message successfully."""
        mock_client = Mock()
        mock_message = Mock()
        mock_message.sid = 'SM123456789'
        mock_message.status = 'queued'
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client

        notifier = WhatsAppNotifier({
            'account_sid': 'test-sid',
            'auth_token': 'test-token',
            'from_number': 'whatsapp:+14155238886',
            'to_number': 'whatsapp:+1234567890'
        })

        result = notifier.send_message('Test message')

        assert result is True
        mock_client.messages.create.assert_called_once()

    def test_get_name(self):
        """Test get_name returns correct name."""
        with patch('src.notifiers.whatsapp.Client'):
            notifier = WhatsAppNotifier({
                'account_sid': 'test-sid',
                'auth_token': 'test-token',
                'from_number': 'whatsapp:+14155238886',
                'to_number': 'whatsapp:+1234567890'
            })
            assert notifier.get_name() == 'whatsapp'
