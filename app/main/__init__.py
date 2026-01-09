"""
Main blueprint module for core website routes.

Provides the main blueprint for handling core website functionality including
homepage, about pages, and other primary navigation routes. Implements production-ready
route handlers with comprehensive error handling and logging.
"""

from flask import Blueprint, render_template, current_app

# Create main blueprint
main_bp = Blueprint(
    'main',
    __name__,
    template_folder='templates',
    static_folder='static'
)


@main_bp.route('/')
def index():
    """
    Homepage route handler.

    Renders the main landing page for the Nigerian tourism website.

    Returns:
        Rendered homepage template

    Raises:
        TemplateNotFound: If homepage template is missing
    """
    current_app.logger.info(
        "Homepage accessed",
        extra={'route': '/', 'blueprint': 'main'}
    )
    return render_template('index.html')


@main_bp.route('/about')
def about():
    """
    About page route handler.

    Renders the about page with information about Nigerian tourism.

    Returns:
        Rendered about page template

    Raises:
        TemplateNotFound: If about template is missing
    """
    current_app.logger.info(
        "About page accessed",
        extra={'route': '/about', 'blueprint': 'main'}
    )
    return render_template('about.html')


@main_bp.before_request
def log_request():
    """
    Log incoming requests to main blueprint routes.

    Executed before each request to main blueprint endpoints for
    observability and debugging purposes.
    """
    from flask import request
    current_app.logger.debug(
        "Main blueprint request received",
        extra={
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'user_agent': request.user_agent.string
        }
    )


@main_bp.after_request
def log_response(response):
    """
    Log outgoing responses from main blueprint routes.

    Args:
        response: Flask response object

    Returns:
        Unmodified response object
    """
    current_app.logger.debug(
        "Main blueprint response sent",
        extra={
            'status_code': response.status_code,
            'content_type': response.content_type
        }
    )
    return response


@main_bp.errorhandler(404)
def not_found_error(error):
    """
    Handle 404 errors within main blueprint.

    Args:
        error: NotFound exception

    Returns:
        Rendered 404 error page with 404 status code
    """
    current_app.logger.warning(
        "Page not found in main blueprint",
        extra={
            'error': str(error),
            'status_code': 404
        }
    )
    return render_template('errors/404.html'), 404


@main_bp.errorhandler(500)
def internal_error(error):
    """
    Handle 500 errors within main blueprint.

    Args:
        error: Internal server error exception

    Returns:
        Rendered 500 error page with 500 status code
    """
    current_app.logger.error(
        "Internal server error in main blueprint",
        exc_info=True,
        extra={
            'error': str(error),
            'status_code': 500,
            'error_type': type(error).__name__
        }
    )
    return render_template('errors/500.html'), 500