import os
from contextlib import contextmanager
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from flask import _app_ctx_stack

db_session = scoped_session(sessionmaker(autocommit=False))
db_flask_session = scoped_session(sessionmaker(autocommit=False),
                                  scopefunc=_app_ctx_stack.__ident_func__)


def db_engine():
    return create_engine(
        os.getenv('CELLAS_DATABASE_URI'), poolclass=NullPool
    )


@contextmanager
def session_scope(scope=None, auto_commit=True, auto_close=True):
    """Provide a transactional scope around a series of operations."""
    session = scope
    try:
        yield session
        if auto_commit:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        if auto_close:
            session.close()
