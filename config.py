"""
Flask application configuration module.

Provides environment-specific configuration classes for development, testing,
and production environments with comprehensive settings for database, security,
logging, and application behavior.
"""

import os
from datetime import timedelta
from typing import Final


class Config:
    """Base configuration class with common settings."""

    # Application Settings
    APP_NAME: str = os.getenv('APP_NAME', 'Nigerian Tourism Website')
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    TIMEZONE: str = os.getenv('TIMEZONE', 'Africa/Lagos')

    # Database Configuration
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        'DATABASE_URL',
        'sqlite:///instance/tourism.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = os.getenv(
        'SQLALCHEMY_TRACK_MODIFICATIONS',
        'False'
    ).lower() == 'true'
    SQLALCHEMY_ECHO: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Server Configuration
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', '5000'))

    # Session Configuration
    SESSION_COOKIE_SECURE: bool = os.getenv(
        'SESSION_COOKIE_SECURE',
        'False'
    ).lower() == 'true'
    SESSION_COOKIE_HTTPONLY: bool = os.getenv(
        'SESSION_COOKIE_HTTPONLY',
        'True'
    ).lower() == 'true'
    SESSION_COOKIE_SAMESITE: str = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    PERMANENT_SESSION_LIFETIME: timedelta = timedelta(
        seconds=int(os.getenv('PERMANENT_SESSION_LIFETIME', '3600'))
    )

    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/app.log')
    LOG_FORMAT: str = (
        '%(asctime)s - %(name)s - %(levelname)s - '
        '[%(filename)s:%(lineno)d] - %(message)s'
    )
    LOG_DATE_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    # Testing Configuration
    TESTING: bool = os.getenv('TESTING', 'False').lower() == 'true'

    # Debug Toolbar Configuration
    DEBUG_TB_ENABLED: bool = os.getenv(
        'DEBUG_TB_ENABLED',
        'False'
    ).lower() == 'true'
    DEBUG_TB_INTERCEPT_REDIRECTS: bool = os.getenv(
        'DEBUG_TB_INTERCEPT_REDIRECTS',
        'False'
    ).lower() == 'true'

    # Security Headers
    SECURITY_HEADERS: dict = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
    }

    # File Upload Configuration
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'uploads'
    )
    ALLOWED_EXTENSIONS: set = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

    # Pagination
    ITEMS_PER_PAGE: int = 20

    # Feature Flags
    ENABLE_REGISTRATION: bool = True
    ENABLE_API: bool = True
    ENABLE_ADMIN: bool = True

    @staticmethod
    def init_app(app) -> None:
        """
        Initialize application with configuration-specific setup.

        Args:
            app: Flask application instance
        """
        pass


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG: bool = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SQLALCHEMY_ECHO: bool = True
    DEBUG_TB_ENABLED: bool = True

    # Development-specific database
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        'DATABASE_URL',
        'sqlite:///instance/tourism_dev.db'
    )

    # Relaxed security for development
    SESSION_COOKIE_SECURE: bool = False

    # Enhanced logging for development
    LOG_LEVEL: str = 'DEBUG'

    @staticmethod
    def init_app(app) -> None:
        """
        Initialize development-specific configuration.

        Args:
            app: Flask application instance
        """
        Config.init_app(app)

        # Ensure instance and logs directories exist
        instance_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'instance'
        )
        logs_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'logs'
        )

        os.makedirs(instance_path, exist_ok=True)
        os.makedirs(logs_path, exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING: bool = True
    DEBUG: bool = True
    SQLALCHEMY_ECHO: bool = False

    # In-memory database for testing
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///:memory:'

    # Disable CSRF for testing
    WTF_CSRF_ENABLED: bool = False

    # Fast password hashing for tests
    BCRYPT_LOG_ROUNDS: int = 4

    # Disable rate limiting in tests
    RATELIMIT_ENABLED: bool = False

    # Test-specific secret key
    SECRET_KEY: str = 'test-secret-key'

    # Simplified session for testing
    PERMANENT_SESSION_LIFETIME: timedelta = timedelta(minutes=5)

    @staticmethod
    def init_app(app) -> None:
        """
        Initialize testing-specific configuration.

        Args:
            app: Flask application instance
        """
        Config.init_app(app)

        # Suppress logging during tests unless explicitly enabled
        if not os.getenv('TEST_LOGGING'):
            import logging
            logging.disable(logging.CRITICAL)


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG: bool = False
    TESTING: bool = False

    # Enforce secure session cookies in production
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = 'Strict'

    # Production database from environment
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        'DATABASE_URL',
        'sqlite:///instance/tourism_prod.db'
    )

    # Strict security headers
    SECURITY_HEADERS: dict = {
        **Config.SECURITY_HEADERS,
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'",
    }

    # Production logging
    LOG_LEVEL: str = 'WARNING'

    # Require secret key in production
    @property
    def SECRET_KEY(self) -> str:
        """
        Get secret key with validation for production.

        Returns:
            str: Secret key from environment

        Raises:
            RuntimeError: If SECRET_KEY not set in production
        """
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key or secret_key == 'your-secret-key-here-change-in-production':
            raise RuntimeError(
                'SECRET_KEY must be set in production environment. '
                'Generate a secure key using: python -c "import secrets; '
                'print(secrets.token_hex(32))"'
            )
        return secret_key

    @staticmethod
    def init_app(app) -> None:
        """
        Initialize production-specific configuration.

        Args:
            app: Flask application instance
        """
        Config.init_app(app)

        # Ensure critical directories exist
        instance_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'instance'
        )
        logs_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'logs'
        )

        os.makedirs(instance_path, exist_ok=True)
        os.makedirs(logs_path, exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Configure production logging to file
        import logging
        from logging.handlers import RotatingFileHandler

        if not app.debug and not app.testing:
            file_handler = RotatingFileHandler(
                app.config['LOG_FILE'],
                maxBytes=10485760,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                app.config['LOG_FORMAT'],
                datefmt=app.config['LOG_DATE_FORMAT']
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info(f'{app.config["APP_NAME"]} startup')


# Configuration dictionary for easy access
config: Final[dict[str, type[Config]]] = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env: str | None = None) -> type[Config]:
    """
    Get configuration class for specified environment.

    Args:
        env: Environment name (development, testing, production).
             If None, uses FLASK_ENV environment variable.

    Returns:
        Configuration class for the specified environment

    Raises:
        ValueError: If environment name is invalid
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')

    config_class = config.get(env)
    if config_class is None:
        raise ValueError(
            f'Invalid environment: {env}. '
            f'Valid options: {", ".join(config.keys())}'
        )

    return config_class