"""
Flask application factory module.

Provides the create_app factory function for initializing the Flask application
with configuration, database, extensions, and blueprints. Implements production-ready
application initialization with comprehensive error handling and logging.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

from flask import Flask, jsonify
from flask.logging import default_handler
from werkzeug.exceptions import HTTPException

from config import get_config


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Create and configure Flask application instance.

    Implements application factory pattern with environment-specific configuration,
    database initialization, extension registration, and blueprint mounting.

    Args:
        config_name: Configuration environment name (development, testing, production).
                    If None, uses FLASK_ENV environment variable.

    Returns:
        Configured Flask application instance

    Raises:
        ValueError: If configuration environment is invalid
        RuntimeError: If critical initialization fails
    """
    # Initialize Flask application
    app = Flask(
        __name__,
        instance_relative_config=True,
        instance_path=os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'instance'
        )
    )

    # Load configuration
    try:
        config_class = get_config(config_name)
        app.config.from_object(config_class)
        config_class.init_app(app)
    except ValueError as e:
        raise ValueError(f"Configuration loading failed: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Configuration initialization failed: {e}") from e

    # Configure logging
    _configure_logging(app)

    app.logger.info(
        "Application initialization started",
        extra={
            'config': config_name or os.getenv('FLASK_ENV', 'development'),
            'debug': app.debug,
            'testing': app.testing
        }
    )

    # Initialize extensions
    _initialize_extensions(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Register health check endpoint
    _register_health_check(app)

    # Apply security headers
    _apply_security_headers(app)

    app.logger.info(
        "Application initialization completed",
        extra={
            'app_name': app.config['APP_NAME'],
            'host': app.config['HOST'],
            'port': app.config['PORT']
        }
    )

    return app


def _configure_logging(app: Flask) -> None:
    """
    Configure application logging with structured output.

    Sets up console and file handlers with appropriate formatting and log levels
    based on application configuration.

    Args:
        app: Flask application instance
    """
    # Remove default handler
    app.logger.removeHandler(default_handler)

    # Set log level
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
    app.logger.setLevel(log_level)

    # Console handler for all environments
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        app.config['LOG_FORMAT'],
        datefmt=app.config['LOG_DATE_FORMAT']
    )
    console_handler.setFormatter(console_formatter)
    app.logger.addHandler(console_handler)

    # File handler for non-testing environments
    if not app.testing:
        try:
            # Ensure logs directory exists
            log_dir = os.path.dirname(app.config['LOG_FILE'])
            os.makedirs(log_dir, exist_ok=True)

            file_handler = RotatingFileHandler(
                app.config['LOG_FILE'],
                maxBytes=10485760,  # 10MB
                backupCount=10
            )
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                app.config['LOG_FORMAT'],
                datefmt=app.config['LOG_DATE_FORMAT']
            )
            file_handler.setFormatter(file_formatter)
            app.logger.addHandler(file_handler)
        except Exception as e:
            app.logger.warning(
                f"Failed to configure file logging: {e}",
                extra={'log_file': app.config['LOG_FILE']}
            )


def _initialize_extensions(app: Flask) -> None:
    """
    Initialize Flask extensions.

    Currently placeholder for future extension initialization (SQLAlchemy, etc.).
    Extensions will be initialized here as they are added to the project.

    Args:
        app: Flask application instance
    """
    app.logger.debug("Initializing extensions")

    # Future extension initialization will be added here
    # Example:
    # from flask_sqlalchemy import SQLAlchemy
    # db = SQLAlchemy(app)

    app.logger.debug("Extensions initialized successfully")


def _register_blueprints(app: Flask) -> None:
    """
    Register application blueprints.

    Currently placeholder for future blueprint registration.
    Blueprints will be registered here as they are created.

    Args:
        app: Flask application instance
    """
    app.logger.debug("Registering blueprints")

    # Future blueprint registration will be added here
    # Example:
    # from app.routes import main_bp
    # app.register_blueprint(main_bp)

    app.logger.debug("Blueprints registered successfully")


def _register_error_handlers(app: Flask) -> None:
    """
    Register global error handlers for the application.

    Provides consistent error responses with appropriate logging for all
    HTTP exceptions and unexpected errors.

    Args:
        app: Flask application instance
    """
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Handle HTTP exceptions with structured response."""
        app.logger.warning(
            f"HTTP exception: {error.name}",
            extra={
                'status_code': error.code,
                'description': error.description
            }
        )
        response = {
            'error': error.name,
            'message': error.description,
            'status_code': error.code
        }
        return jsonify(response), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error: Exception):
        """Handle unexpected exceptions with error logging."""
        app.logger.error(
            f"Unexpected exception: {str(error)}",
            exc_info=True,
            extra={'error_type': type(error).__name__}
        )
        response = {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }
        return jsonify(response), 500


def _register_health_check(app: Flask) -> None:
    """
    Register health check endpoint.

    Provides a simple endpoint for monitoring application health and readiness.

    Args:
        app: Flask application instance
    """
    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Health check endpoint.

        Returns:
            JSON response with application health status
        """
        return jsonify({
            'status': 'healthy',
            'app_name': app.config['APP_NAME'],
            'environment': os.getenv('FLASK_ENV', 'development')
        }), 200


def _apply_security_headers(app: Flask) -> None:
    """
    Apply security headers to all responses.

    Adds configured security headers to protect against common web vulnerabilities.

    Args:
        app: Flask application instance
    """
    @app.after_request
    def set_security_headers(response):
        """Add security headers to response."""
        for header, value in app.config['SECURITY_HEADERS'].items():
            response.headers[header] = value
        return response
```
```