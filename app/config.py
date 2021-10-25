import bugsnag
from aiohttp.client_exceptions import ClientPayloadError
from sanic.exceptions import MethodNotSupported, NotFound
from sanic.handlers import ErrorHandler
from sanic_cors import CORS
from sanic_openapi import swagger_blueprint

from . import settings, utils, views

EXCEPTIONS = (ClientPayloadError, MethodNotSupported, NotFound)


class BugsnagErrorHandler(ErrorHandler):
    def default(self, request, exception):
        if self._should_notify(exception):
            bugsnag.notify(exception, metadata={"request": request.url})
        return super().default(request, exception)

    @staticmethod
    def _should_notify(exception) -> bool:
        if not settings.BUGSNAG_API_KEY:
            return False
        if isinstance(exception, EXCEPTIONS):
            return False
        return True


def init(app):
    app.config.API_HOST = app.config.SERVER_NAME = settings.SERVER_NAME
    app.config.API_BASEPATH = "/"
    app.config.API_SCHEMES = [settings.SCHEME]
    app.config.API_VERSION = utils.meta.version()
    app.config.API_TITLE = "meme.ojanbot.tk"
    app.config.API_CONTACT_EMAIL = "ojancoders@gmail.com"
    app.config.API_LICENSE_NAME = "Github Developer"
    app.config.API_LICENSE_URL = (
        "https://github.com/FznXSec404"
    )
    app.config.API_SECURITY = [{"ApiKeyAuth": []}]
    app.config.API_SECURITY_DEFINITIONS = {
        "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-KEY"}
    }

    swagger_blueprint.url_prefix = "/docs"
    app.blueprint(swagger_blueprint)

    app.blueprint(views.clients.blueprint)
    app.blueprint(views.memes.blueprint)
    app.blueprint(views.templates.blueprint)
    app.blueprint(views.shortcuts.blueprint)  # registered last to avoid collisions

    CORS(app)
    app.error_handler = BugsnagErrorHandler()
    bugsnag.configure(
        api_key=settings.BUGSNAG_API_KEY,
        project_root="/app",
        release_stage=settings.RELEASE_STAGE,
    )
