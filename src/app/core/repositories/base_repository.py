from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: dict, commit: bool = True) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        if commit:
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: dict, commit: bool = True) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        if commit:
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> Optional[ModelType]:
        obj = self.db.query(self.model).filter(self.model.id == id).first()
        if obj:
            self.db.delete(obj)
            self.db.commit()
        return obj

    def commit(self) -> None:
        """Faz commit das mudanças pendentes."""
        self.db.commit()

    def rollback(self) -> None:
        """Desfaz as mudanças pendentes."""
        self.db.rollback()
