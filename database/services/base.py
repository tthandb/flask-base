from typing import Type
from sqlalchemy.orm import load_only
from sqlalchemy.orm import Session
from database.models.base import Base
from sqlalchemy.sql import func
from sqlalchemy import exc, and_, or_


class BaseService(object):
    session: Type[Session] = None
    model: Type[Base] = None

    def find_by_id(self, model_id):
        query = self.session.query(self.model).filter(
            self.model.id == model_id
        )
        return q.first()

    def find(self, select_columns=None, **conditions):
        query = self.select_query(select_columns)

        for key, value in conditions.items():
            if isinstance(value, list):
                query = query.filter(getattr(self.model, key).in_(value))
                continue
            query = query.filter(getattr(self.model, key) == value)

        return query.all()

    def find_paging(
            self, limit=None, offset=None, select_columns=None, **conditions
    ):
        query = self.select_query(select_columns)
        for key, value in conditions.items():
            if isinstance(value, list):
                query = query.filter(getattr(self.model, key).in_(value))
                continue
            query = query.filter(getattr(self.model, key) == value)

        if limit is not None and offset is not None:
            return query.count(), query.limit(limit).offset(offset).all()
        else:
            records = query.all()
            return len(records), records

    def first(self, select_columns=None, **conditions):
        query = self.select_query(select_columns)
        for key, value in conditions.items():
            if isinstance(value, list):
                query = query.filter(getattr(self.model, key).in_(value))
                continue
            query = query.filter(getattr(self.model, key) == value)

        return query.first()

    def select_query(self, select_columns):
        sql_string = self.session.query(self.model)
        if select_columns is not None:
            sql_string = sql_string.options(load_only(*select_columns))
        return sql_string

    def create(self, flush=True, mapping=None, model=None, **data):
        try:
            if model:
                obj = model()
            else:
                obj = self.model()

            for key in data:
                p = key
                if mapping and key in mapping:
                    p = mapping.get(key)

                if hasattr(obj, key):
                    setattr(obj, key, data[p])
            self.session.add(obj)
            if flush:
                self.session.flush()
            return obj
        except exc.IntegrityError as e:
            raise e

    def bulk_create(self, object_infos):
        return self.session.bulk_insert_mappings(
            self.model,
            object_infos,
            return_defaults=True
        )

    def update(self, obj, flush=True, only=None, **data):
        if obj:
            for k in data:
                if hasattr(obj, k) and (only is None or k in only):
                    setattr(obj, k, data.get(k))
        if flush:
            self.session.flush()
        return obj

    def bulk_update(self, records):
        return self.session.bulk_update_mappings(self.model, records)

    def create_or_update(self, filter_info, new_info):
        new_objects = self.find(
            **filter_info
        )
        if not new_objects:
            new_objects = [self.create(**new_info)]
            return new_objects
        for new_object in new_objects:
            self.update(
                new_object,
                **new_info
            )
        return new_objects

    def delete(self, obj, flush=True):
        try:
            self.session.delete(obj)
            if flush:
                self.session.flush()
            return True
        except exc.IntegrityError as e:
            raise e

    def max_updated_at(self):
        query = self.session.query(func.max(self.model.updated_at))
        result = query.scalar()
        return result if result else 0

    def index(self, limit=10, offset=0, order_by=['id', 'asc']):
        query = self.session.query(self.model)
        total = query.count()
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        return total, query.all()

    def index_condition(
            self, limit=10, offset=0, order_by=['id', 'asc'], **conditions
    ):
        query = self.session.query(self.model)

        for key, value in conditions.items():
            if isinstance(value, list):
                query = query.filter(getattr(self.model, key).in_(value))
                continue
            query = query.filter(getattr(self.model, key) == value)

        total = query.count()

        if order_by:
            query = query.order_by(getattr(
                getattr(self.model, order_by[0]),
                order_by[1]
            )())

        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        return total, query.all()
