from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import BaseModel


class Contact(BaseModel):
    __tablename__ = "contacts"

    name: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )