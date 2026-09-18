from sqlalchemy import select

from .base_repository import BaseRepository
from src.models.contact_model import Contact


class ContactRepository(BaseRepository):
    model = Contact

    def get_contact_by_name(self, name: str) -> str:
        result = self.session.execute(
            select(self.model.phone)
            .where(self.model.name == name)
        )

        return result.scalar_one_or_none()

    def get_all_names(self) -> list[str | None]:
        result = self.session.execute(
            select(self.model.name)
        )

        return result.scalars().all()