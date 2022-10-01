import logging
from typing import Callable

from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware

# from fastapi.middleware.gzip import GZipMiddleware
from starlette_exporter import PrometheusMiddleware, handle_metrics

from . import version
from .api.errors import http422_error_handler, http_error_handler
from .api.routes import accounts, health, reports
from .database.session import async_engine
from .settings import app_settings

logger = logging.getLogger("app")


def create_start_app_handler(application: FastAPI) -> Callable:
    async def start_app() -> None:
        logger.info(f"Starting up {version.ABOUT} ...")
        dsn = (
            app_settings.DB_DSN
            if not app_settings.TESTING
            else app_settings.DB_TEST_DSN
        )
        logger.debug(f"Connecting to {dsn}")
        # logger.debug("Connection established.")

    return start_app


def create_stop_app_handler(application: FastAPI) -> Callable:
    async def stop_app() -> None:
        logger.debug("Shutting down...")
        # logger.debug("Closing connections to database")
        # logger.debug("Connection closed")

    return stop_app


def create_application(**kwargs) -> FastAPI:
    application = FastAPI(
        title=kwargs.get("title", "Generic API service"),
        description=kwargs.get("description", ""),
        version=kwargs.get("version", "0.1.0"),
        debug=app_settings.DEBUG,
        root_path=app_settings.PROXY_PREFIX if app_settings.DEBUG else "",
        openapi_tags=kwargs.get("tags_metadata"),
        docs_url="/docs" if app_settings.DEBUG else None,
        redoc_url=None,
    )

    # Set all CORS enabled origins
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in app_settings.BACKEND_CORS_ORIGINS]
        if app_settings.BACKEND_CORS_ORIGINS
        else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # If there is an Accept-Encoding: gzip header in the request, we compress everything that is more than 50KB
    # application.add_middleware(GZipMiddleware, minimum_size=50 * 1024)

    application.add_middleware(
        SQLAlchemyMiddleware,
        custom_engine=async_engine,
    )

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)

    application.add_event_handler("startup", create_start_app_handler(application))
    application.add_event_handler("shutdown", create_stop_app_handler(application))

    # add Prometheus endpoint /metrics
    application.add_middleware(
        PrometheusMiddleware,
        app_name="accounts",
        prefix="http",
        group_paths=True,
        buckets=[0.1, 0.25, 0.5],
        skip_paths=["/health"],
    )
    application.add_route("/metrics", handle_metrics)

    # add Readiness probe /health
    application.include_router(health.router)

    application.include_router(
        accounts.router, prefix=app_settings.API_PREFIX + "/accounts"
    )
    application.include_router(
        reports.router, prefix=app_settings.API_PREFIX + "/reports"
    )

    return application


tags_metadata = [
    {
        "name": "accounts",
        "description": "Accounts management (CRUD)",
    },
    {
        "name": "reports",
        "description": "Various reports",
    },
]


app = create_application(
    title=version.APP_TITLE,
    description=version.APP_DESCRIPTION,
    version=version.__version__,
    about=version.ABOUT,
    copyright=version.__copyright__,
    tags_metadata=tags_metadata,
)
