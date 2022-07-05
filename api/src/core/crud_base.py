from typing import Type, TypeVar, Optional, Any, Generic, List, Union, Dict
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from .db import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase():
    def __init__(self, model: Type[ModelType], db: Session):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `db`: sqlachemy db session
        """
        self.model = model
        self.db = db

    def get(self, id: Any) -> Optional[ModelType]:
        db = self.db
        return db.query(self.model).filter(self.model.id == id).first()

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        db = self.db
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_name(self, name: str) -> Optional[ModelType]:
        db = self.db
        return db.query(self.model).filter(self.model.name == name).first()

    def get_multi(self,  skip: int = 0, limit: int = 100) -> List[ModelType]:
        db = self.db
        return db.query(self.model).offset(skip).limit(limit).all()

    def update(
        self, 
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        db = self.db
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        print(db_obj)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, id: Any) -> ModelType:
        db = self.db
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj