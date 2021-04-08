from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Column, TIMESTAMP
from database.session import db_flask_session, db_engine


DeclarativeBase = declarative_base()
engine = db_engine()
DeclarativeBase.metadata.bind = engine
db_flask_session.configure(bind=engine)
DeclarativeBase.query = db_flask_session.query_property()


class Base(object):
    session = None

    def __init__(self, session=None, **data):
        for key, value in data.iteritems():
            setattr(self, key, value)


class DateTimestamp():
    created_at = Column(TIMESTAMP, nullable=True, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=datetime.utcnow,
                        default=datetime.utcnow)
