"""Tests for Flask application."""

import pytest
from unittest.mock import Mock, patch
import json

from src.app import create_app


@pytest.fixture
def app():
    """Create test app."""
    with patch('src.app.config') as mock_config:
        mock_config.debug = False
        mock_config.host = '0.0.0.0'
        mock_config.port = 5000
        mock_config.slack.is_enabled.return_value = True
        mock_config.telegram.is_enabled.return_value = False
        mock_config.whatsapp.is_enabled.return_value = False
        mock_config.slack.token = 'test-token'
        mock_config.slack.channel = '#test'
        mock_config.validate.return_value = None

        with patch('src.app.SlackNotifier') as mock_slack:
            mock_slack_instance = Mock()
            mock_slack_instance.send_message.return_value = True
            mock_slack_instance.test_connection.return_value = True
            mock_slack.return_value = mock_slack_instance

            app = create_app()
            yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'enabled_platforms' in data
        assert 'version' in data


class TestNotifyEndpoint:
    """Tests for /notify endpoint."""

    def test_notify_missing_message(self, client):
        """Test notify with missing message."""
        response = client.post(
            '/notify',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data
        assert 'message' in data['error'].lower()

    def test_notify_invalid_json(self, client):
        """Test notify with invalid JSON."""
        response = client.post(
            '/notify',
            data='not json',
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_notify_success(self, client):
        """Test successful notification."""
        response = client.post(
            '/notify',
            data=json.dumps({
                'message': 'Test message',
                'platforms': ['slack']
            }),
            content_type='application/json'
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['successful'] > 0
        assert 'results' in data

    def test_notify_invalid_platform(self, client):
        """Test notify with invalid platform."""
        response = client.post(
            '/notify',
            data=json.dumps({
                'message': 'Test message',
                'platforms': ['invalid_platform']
            }),
            content_type='application/json'
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid or disabled platforms' in data['error']


class TestConnectionTest:
    """Tests for /test endpoint."""

    def test_connections(self, client):
        """Test connection test endpoint."""
        response = client.get('/test')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, dict)
