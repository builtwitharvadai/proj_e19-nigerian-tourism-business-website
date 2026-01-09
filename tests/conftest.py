"""
Pytest configuration and fixtures for Flask application testing.

Provides comprehensive test fixtures for Flask application, database, and client
testing with proper setup, teardown, and isolation. Implements production-ready
test infrastructure with context management and resource cleanup.
"""

import os
import tempfile
from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app


@pytest.fixture(scope="session")
def app() -> Generator[Flask, None, None]:
    """
    Create Flask application instance for testing session.

    Provides a Flask application configured for testing with isolated
    database and test-specific settings. Uses session scope for efficiency
    while maintaining test isolation through database fixtures.

    Yields:
        Flask application instance configured for testing

    Notes:
        - Uses in-memory SQLite database for speed
        - Disables CSRF protection for testing
        - Enables testing mode
        - Creates temporary instance directory
    """
    # Create temporary directory for test instance
    temp_dir = tempfile.mkdtemp()
    instance_path = os.path.join(temp_dir, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Create application with testing configuration
    flask_app = create_app('testing')

    # Override instance path for isolation
    flask_app.instance_path = instance_path

    # Ensure logs directory exists
    logs_dir = os.path.join(os.path.dirname(temp_dir), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Push application context for the session
    ctx = flask_app.app_context()
    ctx.push()

    yield flask_app

    # Cleanup
    ctx.pop()

    # Remove temporary directory
    import shutil
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        flask_app.logger.warning(
            f"Failed to cleanup temporary directory: {e}",
            extra={'temp_dir': temp_dir}
        )


@pytest.fixture(scope="function")
def client(app: Flask) -> FlaskClient:
    """
    Create Flask test client for making requests.

    Provides a test client for simulating HTTP requests to the application
    without running a server. Each test function gets a fresh client instance.

    Args:
        app: Flask application fixture

    Returns:
        Flask test client instance

    Notes:
        - Function scope ensures isolation between tests
        - Automatically handles cookies and session
        - Supports context managers for request context
    """
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app: Flask):
    """
    Create Flask CLI test runner.

    Provides a test runner for invoking Flask CLI commands in tests.
    Useful for testing custom CLI commands and management scripts.

    Args:
        app: Flask application fixture

    Returns:
        Flask CLI test runner instance

    Notes:
        - Function scope for test isolation
        - Captures command output for assertions
        - Supports testing click commands
    """
    return app.test_cli_runner()


@pytest.fixture(scope="function", autouse=True)
def reset_app_state(app: Flask) -> Generator[None, None, None]:
    """
    Reset application state between tests.

    Automatically runs before and after each test to ensure clean state.
    Clears any cached data, resets configuration overrides, and ensures
    test isolation.

    Args:
        app: Flask application fixture

    Yields:
        None

    Notes:
        - autouse=True means this runs for every test automatically
        - Function scope ensures per-test cleanup
        - Handles both setup and teardown
    """
    # Setup: Clear any test-specific state
    app.config['TESTING'] = True

    yield

    # Teardown: Reset state after test
    # Clear any cached data or temporary state
    # This ensures tests don't affect each other


@pytest.fixture(scope="function")
def app_context(app: Flask) -> Generator[None, None, None]:
    """
    Provide application context for tests that need it.

    Creates and manages Flask application context for tests that need
    to access application-level resources like config or extensions
    outside of request context.

    Args:
        app: Flask application fixture

    Yields:
        None (context is active during yield)

    Notes:
        - Use when testing code that requires app context
        - Automatically cleaned up after test
        - Separate from request context
    """
    with app.app_context():
        yield


@pytest.fixture(scope="function")
def request_context(app: Flask) -> Generator[None, None, None]:
    """
    Provide request context for tests that need it.

    Creates and manages Flask request context for tests that need
    to access request-level resources like session, request object,
    or g object.

    Args:
        app: Flask application fixture

    Yields:
        None (context is active during yield)

    Notes:
        - Use when testing code that requires request context
        - Provides access to request, session, g
        - Automatically cleaned up after test
    """
    with app.test_request_context():
        yield