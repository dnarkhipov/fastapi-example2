from datetime import datetime, timedelta, timezone

from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine

from app.settings import app_settings


def tstz_encoder(tstz):
    return [
        (tstz.astimezone() - datetime(2000, 1, 1, tzinfo=timezone.utc)).total_seconds()
        * 1000000
    ]


def tstz_decoder(tup):
    return (
        datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=tup[0])
    ).astimezone()


if app_settings.TESTING:
    async_engine = create_async_engine(
        app_settings.DB_TEST_DSN,
        echo=app_settings.DB_SQL_ECHO,
        # https://github.com/sqlalchemy/sqlalchemy/issues/7245
        # https://docs.sqlalchemy.org/en/14/dialects/postgresql.html?highlight=server_settings#module-sqlalchemy.dialects.postgresql.asyncpg
        connect_args={"server_settings": {"jit": "off", "timezone": app_settings.TZ}},
    )
else:
    async_engine = create_async_engine(
        app_settings.DB_DSN,
        echo=app_settings.DB_SQL_ECHO,
        # https://github.com/sqlalchemy/sqlalchemy/issues/7245
        # https://docs.sqlalchemy.org/en/14/dialects/postgresql.html?highlight=server_settings#module-sqlalchemy.dialects.postgresql.asyncpg
        connect_args={"server_settings": {"jit": "off", "timezone": app_settings.TZ}},
    )


@event.listens_for(async_engine.sync_engine, "connect")
def register_custom_types(dbapi_connection, *args):
    # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#using-awaitable-only-driver-methods-in-connection-pool-and-other-events

    dbapi_connection.run_async(
        # https://github.com/MagicStack/asyncpg/issues/481
        lambda connection: connection.set_type_codec(
            "timestamptz",
            encoder=tstz_encoder,
            decoder=tstz_decoder,
            format="tuple",
            schema="pg_catalog",
        )
    )

    # https://github.com/MagicStack/asyncpg/issues/140
    # https://github.com/MagicStack/asyncpg/issues/221
    # dbapi_connection.run_async(
    #     lambda connection: connection.set_type_codec(
    #         "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    #     )
    # )
    # dbapi_connection.run_async(
    #     lambda connection: connection.set_type_codec(
    #         "json", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    #     )
    # )
