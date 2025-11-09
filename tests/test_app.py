"""Tests for FastAPI application."""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client with mocked config and notifiers."""
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

            # Import app after patching
            from src.app import app

            # Trigger startup event manually
            with patch('src.app.initialize_notifiers'):
                client = TestClient(app)

                # Manually set notifiers for tests
                import src.app as app_module
                app_module.notifiers = {'slack': mock_slack_instance}

                yield client


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200

        data = response.json()
        assert data['status'] == 'healthy'
        assert 'enabled_platforms' in data
        assert 'version' in data


class TestNotifyEndpoint:
    """Tests for /notify endpoint."""

    def test_notify_missing_message(self, client):
        """Test notify with missing message."""
        response = client.post(
            '/notify',
            json={}
        )
        # FastAPI Pydantic validation returns 422 for missing required fields
        assert response.status_code == 422

        data = response.json()
        assert 'detail' in data

    def test_notify_invalid_json(self, client):
        """Test notify with invalid JSON."""
        response = client.post(
            '/notify',
            data='not json',
            headers={'content-type': 'application/json'}
        )
        assert response.status_code == 422

    def test_notify_success(self, client):
        """Test successful notification."""
        response = client.post(
            '/notify',
            json={
                'message': 'Test message',
                'platforms': ['slack']
            }
        )
        assert response.status_code == 200

        data = response.json()
        assert data['successful'] > 0
        assert 'results' in data

    def test_notify_invalid_platform(self, client):
        """Test notify with invalid platform."""
        response = client.post(
            '/notify',
            json={
                'message': 'Test message',
                'platforms': ['invalid_platform']
            }
        )
        assert response.status_code == 400

        data = response.json()
        assert 'detail' in data
        # FastAPI puts error details in 'detail' field
        detail = data['detail']
        assert 'error' in detail
        assert 'Invalid or disabled platforms' in detail['error']


class TestConnectionTest:
    """Tests for /test endpoint."""

    def test_connections(self, client):
        """Test connection test endpoint."""
        response = client.get('/test')
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)


class TestDocumentation:
    """Tests for auto-generated API documentation."""

    def test_openapi_docs(self, client):
        """Test OpenAPI docs endpoint."""
        response = client.get('/docs')
        assert response.status_code == 200

    def test_openapi_json(self, client):
        """Test OpenAPI JSON schema."""
        response = client.get('/openapi.json')
        assert response.status_code == 200

        data = response.json()
        assert 'openapi' in data
        assert 'paths' in data
        assert '/health' in data['paths']
        assert '/notify' in data['paths']
        assert '/test' in data['paths']
