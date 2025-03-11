from typing import Any, Iterable, Optional, TypeVar, Generic
from sqlalchemy import Select
from sqlmodel import SQLModel, Session, select
from .errors import MissingEntry

TModel = TypeVar("TModel", bound=SQLModel)
TCreate = TypeVar("TCreate", bound=SQLModel)
TRead = TypeVar("TRead", bound=SQLModel)


class GenericRepository(Generic[TModel, TCreate, TRead]):
    def __init__(self, model: TModel, read: TRead):
        self.model: TModel = model
        self.read: TRead = read

    def _read(self, entry: TModel) -> TRead:
        return self.read(**entry.model_dump())

    def create(self, session: Session, entity: TCreate) -> TRead:
        db_entity = self.model(**entity.model_dump())
        session.add(db_entity)
        session.commit()
        session.refresh(db_entity)

        return self._read(db_entity)

    def create_bulk(self, session: Session, entities: Iterable[dict]) -> None:
        session.bulk_insert_mappings(self.model, entities)

    def get_all(self, session: Session) -> list[TRead]:
        return [self._read(self._read(x)) for x in session.exec(select(self.model)).all()]

    def get_paginated(self, session: Session, offset: int = 0, limit: int = 100) -> list[TRead]:
        return [self._read(x) for x in session.exec(select(self.model).offset(offset).limit(limit)).all()]

    def get_one(self, session: Session, id: int, error: bool = False) -> Optional[TRead]:
        db_entity = session.get(self.model, id)
        if db_entity is None:
            if error:
                raise MissingEntry(self.model.__name__, id)

            return None

        return self._read(db_entity)

    def filter_by(self, session: Session, criteria: dict[str, Any | dict[str, Any]], one: bool = True) -> Optional[TRead] | list[TRead]:
        query: Select = select(self.model)
        ok = True
        for field_name, condition in criteria.items():
            if not hasattr(self.model, field_name):
                ok = False
                break

            field = getattr(self.model, field_name)
            if not isinstance(condition, dict):
                query = query.where(field == condition)
                continue

            query = self.match_condition(query, condition, field)

        if not one:
            return [self._read(x) for x in session.exec(query).all()] if ok else []

        if not ok:
            return None
        
        data = session.exec(query).first()
        if not data:
            return None
                    
        return self._read(data)

    def match_condition(self, query: Any, condition: dict, field: Any):
        value = condition.get("value")
        match condition.get("op", "="):
            case "=":
                return query.where(field == value)
            case "!=":
                return query.where(field != value)
            case "<":
                return query.where(field < value)
            case "<=":
                return query.where(field <= value)
            case ">":
                return query.where(field > value)
            case ">=":
                return query.where(field >= value)
            case "in" if isinstance(value, list):
                return query.where(field.in_(value))
            case "like" if isinstance(value, str):
                return query.where(field.like(value))
            case "in_between" if isinstance(value, (list, tuple)) and len(value) == 2:
                return query.where(field.between(value[0], value[1]))

    def update(self, session: Session, id: int, entity: TCreate) -> TRead:
        return self.update_by_keys_dict(session, id, entity.model_dump(exclude_unset=True))

    def update_by_keys_dict(self, session: Session, id: int, entity: dict[str, Any]) -> TRead:
        db_entity = session.get(self.model, id)
        if db_entity is None:
            raise MissingEntry(self.model.__name__, id)

        db_entity.sqlmodel_update(entity)
        session.add(db_entity)
        session.commit()
        session.refresh(db_entity)

        return self._read(db_entity)

    def update_bulk(self, session: Session, entities: Iterable[dict]) -> None:
        session.bulk_update_mappings(self.model, entities)

    def delete(self, session: Session, id: int) -> bool:
        db_entity = session.get(self.model, id)
        if db_entity is None:
            raise MissingEntry(self.model.__name__, id)

        session.delete(db_entity)
        session.commit()

        return True
