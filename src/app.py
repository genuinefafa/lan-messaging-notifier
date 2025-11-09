"""FastAPI application for LAN Messaging Notifier."""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging

from .config import config
from .notifiers import SlackNotifier, TelegramNotifier, WhatsAppNotifier
from .utils.logger import setup_logger, logger


# Pydantic models for request/response validation
class NotifyRequest(BaseModel):
    """Request model for notification endpoint."""
    message: str = Field(..., description="Message to send", min_length=1)
    platforms: Optional[List[str]] = Field(
        None,
        description="List of platforms to send to (defaults to all enabled)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello from LAN!",
                "platforms": ["slack", "telegram"]
            }
        }


class PlatformResult(BaseModel):
    """Result for a single platform."""
    success: bool
    error: Optional[str] = None


class NotifyResponse(BaseModel):
    """Response model for notification endpoint."""
    message: str
    total_platforms: int
    successful: int
    results: Dict[str, PlatformResult]


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    enabled_platforms: List[str]
    version: str


class TestResponse(BaseModel):
    """Response model for connection tests."""
    pass


# Initialize FastAPI app
app = FastAPI(
    title="LAN Messaging Notifier",
    description="Centralized notification service for LAN - send messages to Slack, Telegram, and WhatsApp",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure logging based on debug setting
if config.debug:
    setup_logger(level=logging.DEBUG)

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


@app.on_event("startup")
async def startup_event():
    """Initialize notifiers on application startup."""
    try:
        config.validate()
        initialize_notifiers()
        logger.info(f"Application started with platforms: {list(notifiers.keys())}")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns service status and enabled platforms.
    """
    return HealthResponse(
        status="healthy",
        enabled_platforms=list(notifiers.keys()),
        version="0.2.0"
    )


@app.get("/test", tags=["Health"])
async def test_connections() -> Dict[str, Dict[str, Any]]:
    """
    Test connections to all enabled platforms.

    Returns connection test results for each platform.
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

    return results


@app.post("/notify", response_model=NotifyResponse, tags=["Notifications"])
async def notify(request: NotifyRequest):
    """
    Send notifications to specified platforms.

    - **message**: The message text to send (required)
    - **platforms**: List of platforms to send to (optional, defaults to all enabled)

    Returns results for each platform.
    """
    try:
        # Use all platforms if not specified
        platforms = request.platforms if request.platforms else list(notifiers.keys())

        # Validate platforms
        invalid_platforms = [p for p in platforms if p not in notifiers]
        if invalid_platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    'error': f'Invalid or disabled platforms: {invalid_platforms}',
                    'available_platforms': list(notifiers.keys())
                }
            )

        # Send to each platform
        results = {}
        success_count = 0

        for platform in platforms:
            try:
                notifier = notifiers[platform]
                success = notifier.send_message(request.message)
                results[platform] = PlatformResult(
                    success=success,
                    error=None
                )
                if success:
                    success_count += 1
            except Exception as e:
                results[platform] = PlatformResult(
                    success=False,
                    error=str(e)
                )
                logger.error(f"Failed to send to {platform}: {e}")

        # Return 500 if no messages were sent successfully
        if success_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    'message': 'Failed to send to any platform',
                    'total_platforms': len(platforms),
                    'successful': 0,
                    'results': {k: {'success': v.success, 'error': v.error} for k, v in results.items()}
                }
            )

        return NotifyResponse(
            message="Notifications sent",
            total_platforms=len(platforms),
            successful=success_count,
            results=results
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /notify endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Internal server error: {str(e)}'
        )


def main():
    """Main entry point for the application."""
    import uvicorn

    logger.info(f"Starting LAN Messaging Notifier on {config.host}:{config.port}")
    logger.info(f"Enabled platforms: {list(notifiers.keys())}")
    logger.info("API Documentation available at http://localhost:5000/docs")

    uvicorn.run(
        "src.app:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level="debug" if config.debug else "info"
    )


if __name__ == '__main__':
    main()
