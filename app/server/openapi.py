"""
OpenAPI/Swagger documentation configuration.
Configures API documentation generation and UI.
"""

from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import RedocRenderPlugin, ScalarRenderPlugin, SwaggerRenderPlugin

from app.config.base_settings import get_settings

settings = get_settings()

# Main OpenAPI configuration
config = OpenAPIConfig(
    title=settings.app.NAME,
    version=settings.app.VERSION,
    use_handler_docstrings=True,
    render_plugins=[ScalarRenderPlugin(), SwaggerRenderPlugin(), RedocRenderPlugin()],  # Scalar documentation UI
    path='/docs'  # Documentation endpoint path
)
