"""Flask application for LAN Messaging Notifier."""

from flask import Flask, request, jsonify
from typing import Dict, Any, List
import logging

from .config import config
from .notifiers import SlackNotifier, TelegramNotifier, WhatsAppNotifier
from .utils.logger import setup_logger, logger


app = Flask(__name__)

# Configure logging based on debug setting
if config.debug:
    setup_logger(level=logging.DEBUG)
    app.config['DEBUG'] = True

# Initialize notifiers
notifiers = {}


def initialize_notifiers():
    """Initialize all enabled notifiers."""
    global notifiers

    if config.slack.is_enabled():
        try:
            notifiers['slack'] = SlackNotifier({
                'token': config.slack.token,
                'channel': config.slack.channel
            })
            logger.info("Slack notifier initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Slack notifier: {e}")

    if config.telegram.is_enabled():
        try:
            notifiers['telegram'] = TelegramNotifier({
                'token': config.telegram.token,
                'chat_id': config.telegram.chat_id
            })
            logger.info("Telegram notifier initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram notifier: {e}")

    if config.whatsapp.is_enabled():
        try:
            notifiers['whatsapp'] = WhatsAppNotifier({
                'account_sid': config.whatsapp.account_sid,
                'auth_token': config.whatsapp.auth_token,
                'from_number': config.whatsapp.from_number,
                'to_number': config.whatsapp.to_number
            })
            logger.info("WhatsApp notifier initialized")
        except Exception as e:
            logger.error(f"Failed to initialize WhatsApp notifier: {e}")

    if not notifiers:
        logger.warning("No notifiers were initialized!")


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns:
        JSON with service status and enabled platforms
    """
    return jsonify({
        'status': 'healthy',
        'enabled_platforms': list(notifiers.keys()),
        'version': '0.1.0'
    }), 200


@app.route('/test', methods=['GET'])
def test_connections():
    """
    Test connections to all enabled platforms.

    Returns:
        JSON with connection test results for each platform
    """
    results = {}

    for platform, notifier in notifiers.items():
        try:
            results[platform] = {
                'success': notifier.test_connection(),
                'error': None
            }
        except Exception as e:
            results[platform] = {
                'success': False,
                'error': str(e)
            }
            logger.error(f"Connection test failed for {platform}: {e}")

    return jsonify(results), 200


@app.route('/notify', methods=['POST'])
def notify():
    """
    Send notifications to specified platforms.

    Request JSON:
        {
            "message": "Your message here",
            "platforms": ["slack", "telegram", "whatsapp"]  # optional, defaults to all
        }

    Returns:
        JSON with send results for each platform
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400

        message = data.get('message')
        if not message:
            return jsonify({'error': 'Missing required field: message'}), 400

        platforms = data.get('platforms', list(notifiers.keys()))

        # Validate platforms
        invalid_platforms = [p for p in platforms if p not in notifiers]
        if invalid_platforms:
            return jsonify({
                'error': f'Invalid or disabled platforms: {invalid_platforms}',
                'available_platforms': list(notifiers.keys())
            }), 400

        # Send to each platform
        results = {}
        success_count = 0

        for platform in platforms:
            try:
                notifier = notifiers[platform]
                success = notifier.send_message(message)
                results[platform] = {
                    'success': success,
                    'error': None
                }
                if success:
                    success_count += 1
            except Exception as e:
                results[platform] = {
                    'success': False,
                    'error': str(e)
                }
                logger.error(f"Failed to send to {platform}: {e}")

        status_code = 200 if success_count > 0 else 500

        return jsonify({
            'message': 'Notifications sent',
            'total_platforms': len(platforms),
            'successful': success_count,
            'results': results
        }), status_code

    except Exception as e:
        logger.error(f"Error in /notify endpoint: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


def create_app():
    """
    Application factory.

    Returns:
        Configured Flask app
    """
    try:
        config.validate()
        initialize_notifiers()
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

    return app


if __name__ == '__main__':
    app = create_app()
    logger.info(f"Starting LAN Messaging Notifier on {config.host}:{config.port}")
    logger.info(f"Enabled platforms: {list(notifiers.keys())}")
    app.run(host=config.host, port=config.port, debug=config.debug)
