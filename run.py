#!/usr/bin/env python3
"""
Application entry point for Flask development server.

Provides the main entry point for running the Flask application in development
mode with proper configuration loading, error handling, and graceful shutdown.
"""

import logging
import os
import sys
from typing import NoReturn

from app import create_app

# Configure basic logging for startup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def validate_environment() -> None:
    """
    Validate required environment setup before application startup.

    Checks for critical environment variables and directory structure
    required for application operation.

    Raises:
        RuntimeError: If critical environment requirements are not met
    """
    # Check Python version
    if sys.version_info < (3, 8):
        raise RuntimeError(
            f"Python 3.8 or higher required. Current version: {sys.version}"
        )

    # Ensure instance directory exists
    instance_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'instance'
    )
    if not os.path.exists(instance_path):
        logger.info(f"Creating instance directory: {instance_path}")
        os.makedirs(instance_path, exist_ok=True)

    # Ensure logs directory exists
    logs_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'logs'
    )
    if not os.path.exists(logs_path):
        logger.info(f"Creating logs directory: {logs_path}")
        os.makedirs(logs_path, exist_ok=True)

    logger.info("Environment validation completed successfully")


def main() -> NoReturn:
    """
    Main entry point for Flask application.

    Creates and runs the Flask application with development server configuration.
    Handles startup errors and provides graceful shutdown on interruption.

    Raises:
        SystemExit: On application startup failure or keyboard interrupt
    """
    try:
        # Validate environment before startup
        validate_environment()

        # Load environment from .env file if present
        env_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '.env'
        )
        if os.path.exists(env_file):
            logger.info(f"Loading environment from: {env_file}")
            from dotenv import load_dotenv
            load_dotenv(env_file)
        else:
            logger.warning(
                "No .env file found. Using default configuration. "
                "Copy .env.example to .env for custom settings."
            )

        # Get configuration environment
        config_env = os.getenv('FLASK_ENV', 'development')
        logger.info(f"Starting application in {config_env} mode")

        # Create Flask application
        app = create_app(config_env)

        # Get server configuration
        host = app.config.get('HOST', '0.0.0.0')
        port = app.config.get('PORT', 5000)
        debug = app.config.get('DEBUG', True)

        logger.info(
            f"Starting Flask development server on http://{host}:{port}"
        )
        logger.info(f"Debug mode: {debug}")
        logger.info("Press CTRL+C to quit")

        # Run development server
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            threaded=True
        )

    except KeyboardInterrupt:
        logger.info("Application shutdown requested by user")
        sys.exit(0)

    except Exception as e:
        logger.error(
            f"Application startup failed: {str(e)}",
            exc_info=True
        )
        sys.exit(1)


if __name__ == '__main__':
    main()