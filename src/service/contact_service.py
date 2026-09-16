from sqlalchemy.orm import Session
import logging

from src.repositories.contact_repository import ContactRepository
from src.tts.tts import speak

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("contact_service")


class ContactService:
    def __init__(self, session: Session):
        self.session = session
        self.contact_repo = ContactRepository(session=self.session)

    def create_contact(self, name: str, phone: str) -> None:
        try:
            name = name.replace(" ", "").replace(".", "")

            self.contact_repo.create(
                name=name,
                phone=phone
            )

            self.session.commit()

            speak(f"Контакт создан успешно, Имя: {name}, Телефон: {phone}")

        except Exception as e:
            self.session.rollback()

            logger.error(f"Ошибка в базе, контакт не создался: {e}")

            speak("Ошибка в базе, контакт не создался")
            return None

    def get_contact_by_name(self, name: str) -> str | bool:
        phone = self.contact_repo.get_contact_by_name(name=name)

        if not phone:
            logger.warning(f"Телефон не найден по имени: {name}")
            return False

        return phone

    def get_all_names(self) -> list[str | None]:
        names = self.contact_repo.get_all_names()

        logger.info("Успешный ответ")
        
        return names