# pylint: disable=all
"""Provide access to the SQL backend."""

from os import getenv
from ssl import SSLContext
from dotenv import dotenv_values
from pg8000.dbapi import Connection
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

CONFIG = dotenv_values()

HOST = CONFIG.get("PG_HOST", getenv("PG_HOST"))
PORT = CONFIG.get("PG_PORT", 5432)
DATABASE = CONFIG.get("DB_NAME", getenv("DB_NAME"))
USER = CONFIG.get("PG_USERNAME", getenv("PG_USERNAME"))
PASSWORD = CONFIG.get("PG_PASSWORD", getenv("PG_PASSWORD"))

# Globals for managing DB connections
engine = None
session_factory = None


def get_ssl_context(
    certfile: str = "keys/client-cert.pem",
    keyfile: str = "keys/client-key.pem",
    cafile: str = "keys/server-ca.pem",
) -> SSLContext:
    """Return the `SSLContext` for DB connections that require encryption."""
    ssl_context = SSLContext()
    ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    ssl_context.load_verify_locations(cafile=cafile)
    return ssl_context


def get_connection() -> Connection:
    """Get a DB API `Connection` using the driver of choice (`pg8000` for now)."""
    return Connection(
        user=USER,
        password=PASSWORD,
        host=HOST,
        database=DATABASE,
        ssl_context=get_ssl_context(),
    )


def get_engine(db_name: str) -> Engine:
    """Get the running instance of a SQLAlchemy `Engine`."""
    global engine
    if engine is None:
        if getenv("OTR_CLOUD"):
            engine = create_engine(
                f"postgresql+pg8000://{USER}:{PASSWORD}@/{db_name}"
                f"?unix_sock=/cloudsql/{getenv('CLOUDSQL_INSTANCE_ID')}/.s.PGSQL.5432",
                echo=False,
            )
        else:
            engine = create_engine(
                f"postgresql+pg8000://{USER}:{PASSWORD}@{HOST}:{PORT}/{db_name}",
                # creator=get_connection,
                echo=False,
            )

    return engine


def get_session(db_name: str = DATABASE) -> Session:
    """Get a `Session` to maintain database transactions."""
    global session_factory
    if session_factory is None:
        session_factory = sessionmaker(get_engine(db_name))

    return session_factory()


async def get_api_db() -> Session:
    """Return a database session suitable for authenticated API requests,
    and close the session after serving the request."""
    db = get_session()
    try:
        yield db
    finally:
        db.close()
