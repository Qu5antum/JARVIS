from abc import ABC, abstractmethod
from sqlalchemy import select
from typing import Dict, Any
from sqlalchemy.orm import Session


class AbstractRepository(ABC):
    @abstractmethod
    async def create(self, data: dict):
        raise NotImplementedError
    
    @abstractmethod
    async def get(self, id: int):
        raise NotImplementedError
    
    @abstractmethod
    async def get_all(self):
        raise NotImplementedError


class BaseRepository(AbstractRepository):
    model = None

    def __init__(self, session: Session):
        self.session = session

    def create(self, **kwargs):
        new_object = self.model(**kwargs)
        self.session.add(new_object)
        self.session.flush()
        self.session.refresh(new_object)

        return new_object

    def get(self, id: int):
        obj = self.session.get(self.model, id)

        return obj
    
    def get_obj(self, id: int):
        obj = self.session.execute(
            select(self.model).where(self.model.id == id)
        )

        return obj.scalar_one_or_none()
     
    def get_all(self):
        result = self.session.execute(select(self.model))

        return result.scalars().all()
    
    def update(self, id: int, data: Dict[str, Any]):
        obj = self.session.get(self.model, id)
  
        try:
            if obj: 
                for key, value in data.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
            
            self.session.commit()
            self.session.refresh(obj)

            return obj

        except:
            self.session.rollback()
            raise

    def delete(self, id: int):
        try:
            obj = self.session.get(self.model, id)

            if not obj:
                return None

            self.session.delete(obj)
            self.session.commit()

            return obj
        
        except:
            raise