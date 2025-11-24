from jinja2 import Template

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from core.config import API_VERSION
from core.utils import get_extensions


router_private = APIRouter(
    prefix=f"{API_VERSION}/private",
    tags=["extensions"]
)


@router_private.get('/extensions', response_class=PlainTextResponse)
async def extensions():
    return ' '.join(get_extensions())


@router_private.get('/nginx_extensions', response_class=PlainTextResponse)
async def nginx_extensions():
    """Get nginx extensions configuration"""
    template = """
        # External Deployments. Auto-generated from manager (nginx_extensions)
        # ====================================================================
    {% for extension in extensions %}
        location ~* /src/?(.*){{extension}}$ {
            alias /var/migasfree/public/$1{{extension}};
            error_page 404 = @backend;
        }
    {% endfor %}
        # ====================================================================
    """

    extensions = get_extensions()
    if len(get_extensions()) > 0:
        return Template(template).render({'extensions': extensions})

    return ''

