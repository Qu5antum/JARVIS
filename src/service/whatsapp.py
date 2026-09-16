import pywhatkit


class WhatsAppService:
    @staticmethod
    def send_message(
        phone: str,
        message: str,
        wait_time: int = 60,
        tab_close: bool = True,
    ) -> None:

        if not phone.startswith("+"):
            raise ValueError(
                "Номер должен быть в международном формате. "
                "Например: +7XXXXXXXXX"
            )

        if not message.strip():
            raise ValueError("Сообщение не может быть пустым")

        pywhatkit.sendwhatmsg_instantly(
            phone_no=phone,
            message=message,
            wait_time=wait_time,
            tab_close=tab_close,
            close_time=3,
        )