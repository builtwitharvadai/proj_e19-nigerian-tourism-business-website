"""
Main blueprint routes for Nigerian tourism website.

Implements core routes including health check, home page, and comprehensive
error handlers with production-ready logging and monitoring capabilities.
"""

from flask import Blueprint, jsonify, current_app, request
from werkzeug.exceptions import HTTPException
import time
from typing import Dict, Any, Tuple

# Create main blueprint
main_bp = Blueprint(
    'main',
    __name__,
    template_folder='templates',
    static_folder='static'
)


@main_bp.route('/health', methods=['GET'])
def health_check() -> Tuple[Dict[str, Any], int]:
    """
    Health check endpoint for monitoring and load balancers.

    Provides comprehensive health status including database connectivity,
    application state, and system metrics for observability.

    Returns:
        Tuple of JSON response and HTTP status code

    Response Schema:
        {
            "status": "healthy" | "unhealthy",
            "timestamp": ISO 8601 timestamp,
            "checks": {
                "database": "ok" | "error",
                "application": "ok"
            },
            "version": str
        }
    """
    start_time = time.time()
    
    health_status = {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "checks": {
            "application": "ok"
        }
    }
    
    # Database connectivity check
    try:
        from app.models import db
        db.session.execute(db.text('SELECT 1'))
        health_status["checks"]["database"] = "ok"
        
        current_app.logger.info(
            "Health check passed",
            extra={
                'route': '/health',
                'database_status': 'ok',
                'response_time_ms': round((time.time() - start_time) * 1000, 2)
            }
        )
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = "error"
        
        current_app.logger.error(
            "Health check failed - database error",
            exc_info=True,
            extra={
                'route': '/health',
                'database_status': 'error',
                'error_type': type(e).__name__,
                'error_message': str(e),
                'response_time_ms': round((time.time() - start_time) * 1000, 2)
            }
        )
        
        return jsonify(health_status), 503
    
    # Add version information if available
    try:
        health_status["version"] = current_app.config.get('VERSION', '1.0.0')
    except Exception:
        pass
    
    return jsonify(health_status), 200


@main_bp.route('/')
def home() -> str:
    """
    Homepage route handler.

    Renders the main landing page for the Nigerian tourism website with
    featured destinations and services.

    Returns:
        Rendered HTML template

    Raises:
        TemplateNotFound: If homepage template is missing
    """
    start_time = time.time()
    
    current_app.logger.info(
        "Homepage accessed",
        extra={
            'route': '/',
            'method': request.method,
            'remote_addr': request.remote_addr,
            'user_agent': request.user_agent.string
        }
    )
    
    try:
        response = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nigerian Tourism - Discover Nigeria</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                header {
                    background-color: #008751;
                    color: white;
                    padding: 20px 0;
                    text-align: center;
                }
                h1 {
                    margin: 0;
                }
                .content {
                    background-color: white;
                    padding: 40px;
                    margin-top: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .welcome {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .features {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-top: 30px;
                }
                .feature {
                    padding: 20px;
                    background-color: #f9f9f9;
                    border-radius: 4px;
                    border-left: 4px solid #008751;
                }
                .feature h3 {
                    margin-top: 0;
                    color: #008751;
                }
                footer {
                    text-align: center;
                    padding: 20px;
                    margin-top: 40px;
                    color: #666;
                }
            </style>
        </head>
        <body>
            <header>
                <div class="container">
                    <h1>🇳🇬 Nigerian Tourism</h1>
                    <p>Discover the Beauty and Culture of Nigeria</p>
                </div>
            </header>
            
            <div class="container">
                <div class="content">
                    <div class="welcome">
                        <h2>Welcome to Nigerian Tourism</h2>
                        <p>Explore Nigeria's rich cultural heritage, stunning landscapes, and vibrant cities.</p>
                    </div>
                    
                    <div class="features">
                        <div class="feature">
                            <h3>🏞️ Natural Wonders</h3>
                            <p>From the Yankari National Park to the Olumo Rock, discover Nigeria's breathtaking natural attractions.</p>
                        </div>
                        
                        <div class="feature">
                            <h3>🎭 Cultural Heritage</h3>
                            <p>Experience the diverse cultures, festivals, and traditions of Nigeria's many ethnic groups.</p>
                        </div>
                        
                        <div class="feature">
                            <h3>🏙️ Modern Cities</h3>
                            <p>Explore vibrant urban centers like Lagos, Abuja, and Port Harcourt with world-class amenities.</p>
                        </div>
                        
                        <div class="feature">
                            <h3>🍲 Culinary Delights</h3>
                            <p>Savor authentic Nigerian cuisine from jollof rice to suya and pounded yam.</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <footer>
                <p>&copy; 2024 Nigerian Tourism. All rights reserved.</p>
            </footer>
        </body>
        </html>
        """
        
        current_app.logger.info(
            "Homepage rendered successfully",
            extra={
                'route': '/',
                'response_time_ms': round((time.time() - start_time) * 1000, 2)
            }
        )
        
        return response
        
    except Exception as e:
        current_app.logger.error(
            "Error rendering homepage",
            exc_info=True,
            extra={
                'route': '/',
                'error_type': type(e).__name__,
                'error_message': str(e),
                'response_time_ms': round((time.time() - start_time) * 1000, 2)
            }
        )
        raise


@main_bp.before_request
def log_request() -> None:
    """
    Log incoming requests for observability.

    Executed before each request to main blueprint endpoints.
    Captures request metadata for debugging and monitoring.
    """
    current_app.logger.debug(
        "Request received",
        extra={
            'blueprint': 'main',
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'user_agent': request.user_agent.string,
            'referrer': request.referrer
        }
    )


@main_bp.after_request
def log_response(response):
    """
    Log outgoing responses for observability.

    Args:
        response: Flask response object

    Returns:
        Unmodified response object
    """
    current_app.logger.debug(
        "Response sent",
        extra={
            'blueprint': 'main',
            'status_code': response.status_code,
            'content_type': response.content_type,
            'content_length': response.content_length
        }
    )
    return response


@main_bp.errorhandler(404)
def not_found_error(error) -> Tuple[str, int]:
    """
    Handle 404 Not Found errors.

    Args:
        error: NotFound exception

    Returns:
        Tuple of error response and 404 status code
    """
    current_app.logger.warning(
        "Page not found",
        extra={
            'blueprint': 'main',
            'path': request.path,
            'method': request.method,
            'remote_addr': request.remote_addr,
            'status_code': 404,
            'error_message': str(error)
        }
    )
    
    error_response = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>404 - Page Not Found</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f5f5f5;
            }
            .error-container {
                text-align: center;
                padding: 40px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #008751;
                font-size: 72px;
                margin: 0;
            }
            h2 {
                color: #333;
                margin: 10px 0;
            }
            p {
                color: #666;
                margin: 20px 0;
            }
            a {
                color: #008751;
                text-decoration: none;
                font-weight: bold;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="error-container">
            <h1>404</h1>
            <h2>Page Not Found</h2>
            <p>The page you are looking for does not exist.</p>
            <p><a href="/">Return to Homepage</a></p>
        </div>
    </body>
    </html>
    """
    
    return error_response, 404


@main_bp.errorhandler(500)
def internal_error(error) -> Tuple[str, int]:
    """
    Handle 500 Internal Server Error.

    Args:
        error: Internal server error exception

    Returns:
        Tuple of error response and 500 status code
    """
    current_app.logger.error(
        "Internal server error",
        exc_info=True,
        extra={
            'blueprint': 'main',
            'path': request.path,
            'method': request.method,
            'remote_addr': request.remote_addr,
            'status_code': 500,
            'error_type': type(error).__name__,
            'error_message': str(error)
        }
    )
    
    error_response = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>500 - Internal Server Error</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f5f5f5;
            }
            .error-container {
                text-align: center;
                padding: 40px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #d32f2f;
                font-size: 72px;
                margin: 0;
            }
            h2 {
                color: #333;
                margin: 10px 0;
            }
            p {
                color: #666;
                margin: 20px 0;
            }
            a {
                color: #008751;
                text-decoration: none;
                font-weight: bold;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="error-container">
            <h1>500</h1>
            <h2>Internal Server Error</h2>
            <p>Something went wrong on our end. Please try again later.</p>
            <p><a href="/">Return to Homepage</a></p>
        </div>
    </body>
    </html>
    """
    
    return error_response, 500


@main_bp.errorhandler(Exception)
def handle_exception(error) -> Tuple[Any, int]:
    """
    Handle all unhandled exceptions.

    Provides fallback error handling for any exceptions not caught
    by specific error handlers.

    Args:
        error: Exception instance

    Returns:
        Tuple of error response and appropriate status code
    """
    # Handle HTTP exceptions
    if isinstance(error, HTTPException):
        current_app.logger.warning(
            "HTTP exception occurred",
            extra={
                'blueprint': 'main',
                'path': request.path,
                'method': request.method,
                'status_code': error.code,
                'error_message': error.description
            }
        )
        return error.get_response(), error.code
    
    # Handle all other exceptions as 500
    current_app.logger.error(
        "Unhandled exception",
        exc_info=True,
        extra={
            'blueprint': 'main',
            'path': request.path,
            'method': request.method,
            'error_type': type(error).__name__,
            'error_message': str(error)
        }
    )
    
    return internal_error(error)