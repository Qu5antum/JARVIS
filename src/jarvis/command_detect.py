import logging
import sys
import shutil
import subprocess
from sys import platform
import webbrowser
from datetime import datetime
import locale
import math

from src.service.downloader import download_video, Format
from src.jarvis.media_contoroller import MediaController
from src.tts.tts import speak, take_command
from src.core.config import settings
from .time_manager import TimerManager
from .proccess_manager import get_processes, get_cpu_processes, kill_process
from .weather import weather
from .helper import (
    is_muted, 
    mute, 
    get_volume, 
    set_volume, 
    unmute, 
    validate_time, 
    format_time, 
    translate, 
    check_internet_speed
)
from .key_movement import (
    press_key, 
    move_mouse, 
    mouse_click, 
    double_click, 
    right_click, 
    scroll_up, 
    scroll_down, 
    move_mouse_relative, 
    selection, 
    insert, 
    copy, 
    close, 
    make_screenshot,
    switch_beetween_multiple_windows,
    fast_switch_between_windows
)
from src.service.contact_service import ContactService
from src.database.db import SessionLocal
from src.service.whatsapp import WhatsAppService
from .screen_recorder import ScreenRecorder
from src.detection.camera_pipeline import CameraPipeline
from .computer_controller import ComputerControl

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("jarvis_main")

session = SessionLocal()
timer_manager = TimerManager()
contact_service = ContactService(session=session)
whatsapp_service = WhatsAppService()
recorder = ScreenRecorder()
camera_pipeline = CameraPipeline(source=0, draw=False)
computer_control = ComputerControl()

# TODO: добавить возможность отправления сообщения по почте
class JarvisMain:
    def __init__(self) -> None:
        if platform == "linux" or platform == "linux2":
            self.chrome_path = "/usr/bin/google-chrome"

        elif platform == "darwin":
            self.chrome_path = "open -a /Applications/Google\\ Chrome.app"

        elif platform == "win32":
            self.chrome_path = (
                r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            )

        else:
            logger.info("Unsupported OS")
            sys.exit(1)

        webbrowser.register(
            "chrome", None, webbrowser.BackgroundBrowser(self.chrome_path)
        )

    def execute_command(self, text: str) -> bool:
        command = text.lower().strip()

        logger.info(f"Команда: {command}")

        if any(
            phrase in command
            for phrase in [
                "открой браузер",
                "открыть браузер",
                "запусти браузер",
                "open browser",
            ]
        ):
            speak("Открываю браузер")
            webbrowser.get("chrome").open_new_tab("https://google.com")
            return True

        if "найди в гугле" in command or "найди в google" in command:
            speak("Что найти в гугле?")

            query = take_command()

            if not query:
                speak("Я не расслышал запрос")
                return True

            speak(f"Ищу в гугле {query}")

            url = (
                f"https://www.google.com/search?q={query}"
            )

            webbrowser.get("chrome").open_new_tab(url)

            return True

        if (
            "открой карты" in command
            or "карты" in command
            or "гугл карты" in command
            or "google карты" in command
        ):
            speak("Какое местоположение вы ищите")

            query = take_command()

            if not query:
                speak("Я не расслышал запрос")
                return True

            url = f"https://www.google.com/maps?q={query}"

            webbrowser.get("chrome").open_new_tab(url)

            return True

        if "открой почту" in command or "запусти почту" in command:
            speak("Открываю почту")
            webbrowser.get("chrome").open("https://mail.google.com/mail")
            return True
            
        if any(
            phrase in command
            for phrase in [
                "открой ютуб",
                "открыть ютуб",
                "запусти ютуб",
                "открой youtube",
                "open youtube",
                "запусти youtube",
                "открой youtube",
            ]
        ):
            speak("Открываю YouTube")
            webbrowser.get("chrome").open("https://youtube.com")
            return True

        if "найди в youtube"  in command or "найди в ютубе" in command:
            speak("Что найти в ютубе?")
            
            query = take_command()

            if not query:
                speak("Я не расслышал запрос")
                return True

            speak(f"Ищу в ютубе {query}")

            url = (
                f"https://www.youtube.com/results?search_query={query}"
            )

            webbrowser.get("chrome").open_new_tab(url)

            return True

        if "скачай" in command:
            speak("Вставь ссылку видео")
            
            url = input("Вставь ссылку видео: ")

            speak("Укажи формат (mp3 или mp4)")

            format_input = input(
                "Укажи формат (mp3 или mp4): "
            ).lower().strip()

            try:
                format = Format(format_input)

            except ValueError:
                speak("Неподдерживаемый формат")

                return False
            try:
                file = download_video(url=url, format=format)

                speak(f"Файл успешно скачан в дерикторий: {file}")

                logger.info(f"Файл находится здесь: {file}")

                return True
            except Exception as e:
                logger.error(f"Ошибка скачавания файла: {e}")

                speak("Не удалось скачать файл")

                return False

        if any(
            phrase in command 
            for phrase in [
                "открой блокнот",
                "открыть блокнот",
                "запусти блокнот",
                "open notepad",
            ]
        ):
            speak("Открываю блокнот")
            subprocess.run(["notepad.exe"])
            return True

        if any(
            phrase in command
            for phrase in [
                "открой github",
                "запусти github",
                "открой гитхаб",
                "запусти гитхаб"
            ]
        ):
            speak("Открываю Github")
            webbrowser.get("chrome").open("https://github.com/Qu5antum")
            return True

        if any(
            phrase in command
            for phrase in [
                "открой minecraft",
                "запусти minecraft",
                "открой майнкрафт",
                "запусти майнкрафт"
            ]
        ):
            speak("Открываю Minecraft")
            subprocess.run([settings.MINECRAFT_DIRECTORY])
            return True

        if any(
            phrase in command
            for phrase in [
                "запусти whatsapp",
                "открой whatsapp",
                "открой ватсап",
                "запусти ватсап",
            ]
        ):
            speak("Открываю Whatsapp")
            webbrowser.get("chrome").open("https://web.whatsapp.com/")
            return True

        if any(
            phrase in command
            for phrase in [
                "открой телеграм",
                "запусти телеграм",
                "открой telegram",
                "запусти telegram"
            ]
        ):
            speak("Открываю Telegram")
            webbrowser.get("chrome").open("https://web.telegram.org/")
            return True

        if any(
            phrase in command
            for phrase in [
                "запусти тикток",
                "открой тикток",
                "запусти tiktok",
                "открой tiktok",
            ]
        ):
            speak("Открываю Tiktok")
            webbrowser.get("chrome").open("https://www.tiktok.com/")
            return True

        if any(
            phrase in command
            for phrase in [
                "открой leetcode",
                "запусти leetcode",
                "открой лит-код",
                "запусти лит-код",
            ]
        ):
            speak("Открываю Leetcode")
            webbrowser.get("chrome").open("https://leetcode.com/problemset/")
            return True

        if any(
            phrase in command
            for phrase in [
                "открой чат гпт",
                "запусти чат гпт",
                "открой чат джпт",
                "запусти лит-джпт",
                "открой chat gpt",
                "запусти chat gpt",
                "открой чат gpt",
                "запусти чат gpt"
            ]
        ):
            speak("Открываю chat gpt")
            webbrowser.get("chrome").open("https://chatgpt.com/")
            return True

        if any(
            phrase in command
            for phrase in [
                "открой инстаграм",
                "запусти инстаграм",
                "открой instagram",
                "запусти instagram",
            ]
        ):
            speak("Открываю instagram")
            webbrowser.get("chrome").open("https://www.instagram.com/")
            return True

        if (
            "открой канва" in command
            or "запусти канва" in command
            or "открой canva" in command
            or "запусти canva" in command
        ):
            speak("Открываю Canva")
            webbrowser.get("chrome").open("https://www.canva.com/")
            return True

        if (
            "открой spotify" in command
            or "запусти spotify" in command
            or "открой спотифай" in command
            or "запусти спотифай" in command
        ):
            speak("Открываю spotify")
            webbrowser.get("chrome").open("https://open.spotify.com/")
            return True

        if (
            "открой рэддит" in command
            or "запусти рэддит" in command
            or "открой reddit" in command
            or "запусти reddit" in command
        ):
            speak("Открываю reddit")
            webbrowser.get("chrome").open("https://www.reddit.com/")
            return True

        if (
            "открой икс" in command
            or "запусти икс" in command
            or "открой x" in command
            or "запусти x" in command
        ): 
            speak("Открываю X")
            webbrowser.get("chrome").open("https://x.com/")
            return True

        if (
            "открой фейсбук" in command
            or "запусти фейсбук" in command
            or "открой facebook" in command
            or "запусти facebook" in command
        ):
            speak("Открываю facebook")
            webbrowser.get("chrome").open("https://www.facebook.com/")
            return True

        if (
            "открой линкедин" in command
            or "запусти линкедин" in command
            or "открой linkedln" in command
            or "запусти linkedln" in command
        ):
            speak("Открываю linkedln")
            webbrowser.get("chrome").open("https://www.linkedin.com/feed/")
            return True

        if (
            "открой капкут" in command
            or "запусти капкут" in command
            or "открой capcut" in command
            or "запусти capcut" in command
        ):
            speak("Открываю Capcut")
            subprocess.run([settings.CAPCUT_DIRECTORY])
            return True

        if any(
            phrase in command
            for phrase in [
                "открой дискорд",
                "запусти дискорд",
                "открой discord",
                "запусти discord",
            ]
        ):
            discord_path = shutil.which(settings.DISCORD_DIRECTORY)

            if discord_path:
                speak("Открываю discord")
                subprocess.run([settings.DISCORD_DIRECTORY])
            else:
                speak("Открываю discord в браузере")
                webbrowser.get("chrome").open("https://discord.com/")

            return True

        if any(
            phrase in command
            for phrase in [
                "открой стим",
                "запусти стим",
                "открой steam",
                "запусти steam",
            ]
        ):
            steam_path = shutil.which(settings.STEAM_DIRECTORY)

            if steam_path:
                speak("Открываю steam")
                subprocess.run([settings.STEAM_DIRECTORY])
            else:
                speak("Открываю steam в браузере")
                webbrowser.get("chrome").open("https://store.steampowered.com/")

            return True

        if (
            "открой ворд" in command
            or "запусти ворд" in command
            or "открой word" in command
            or "запусти word" in command
        ):
            speak("Открываю Word")
            webbrowser.get("chrome").open("https://word.cloud.microsoft/")
            return True

        if (
            "открой поверпоинт" in command
            or "запусти поверпоинт" in command
            or "открой powerpoint" in command
            or "запусти powerpoint" in command
        ):
            speak("Открываю Powerpoint")
            webbrowser.get("chrome").open("https://powerpoint.cloud.microsoft/")
            return True

        if (
            "открой экзель" in command
            or "запусти экзель" in command
            or "открой excel" in command
            or "запусти excel" in command
        ): 
            speak("Открываю Excel")
            webbrowser.get("chrome").open("https://excel.cloud.microsoft/")
            return True


        if "открой настройки" in command or "запусти наcтройки" in command:
            speak("Открываю настройки")
            subprocess.run(["cmd", "/c", "start", "ms-settings:display"])
            return True

        if "открой терминал" in command or "запусти терминал" in command:
            speak("Открываю терминал PowerShell")
            subprocess.Popen(['start', 'powershell'], shell=True)
            return True

        if "открой калькулятор" in command or "запусти калькулятор" in command:
            speak("Открываю Калькулятор")
            subprocess.Popen('calc')
            return True

        if any(
            phrase in command
            for phrase in [
                "открой paint",
                "запусти paint",
                "открой пейнт",
                "запусти пейнт"
            ]
        ):
            speak("Открываю Paint")
            subprocess.run("mspaint")
            return True

        if "открой диспетчер устройств" in command or "запусти диспетчер устройств" in command:
            speak("Открываю диспетчер устройств")
            subprocess.Popen("devmgmt.msc", shell=True)
            return True

        if "открой диспетчер задач" in command or "запусти диспетчер задач" in command:
            speak("Открываю диспетчер задач")
            subprocess.Popen("taskmgr")
            return True

        if "открой проводник" in command or "запусти проводник" in command:
            speak("Открываю проводник")
            subprocess.run(['explorer'])
            return True

        if "выключи компьютер" in command:
            speak("Выключаю компьютер")
            subprocess.run(["shutdown", "/s", "/f", "/t", "0"])
            return True

        if "перезапусти компьютер" in command:
            speak("Перезапускаю компьютер")
            subprocess.run(["shutdown", "/r", "/t", "0"])
            return True

        if "перевести компьютер в спящий режим" in command or "компьютер в спящий режим" in command:
            speak("Перевожу компьютер в спящий режим")
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"], check=True)
            return True

        if "выключи звук" in command:
            if not is_muted():
                speak("Выключаю звук")
                mute()
            else:
                speak("Звук уже выключен")

            return True

        if "включи звук" in command:
            if is_muted():
                speak("Включаю звук")
                unmute()
            else:
                speak("Звук уже включен")

            return True

        if "увеличь громкость" in command or "увеличить громкость" in command:
            current = get_volume()
            set_volume(current + 10)
            speak(f"Громкость {get_volume()} процентов")
            return True

        if "уменьши громкость" in command or "уменьшить громкость" in command:
            current = get_volume()
            set_volume(current - 10)
            speak(f"Громкость {get_volume()} процентов")
            return True

        #TODO добавить возможность увеличивания громкости на какой то процент

        if "пауза" in command:
            speak("Пауза")
            MediaController.play_pause()
            return True

        if "продолжи" in command:
            speak("Продолжаю")
            MediaController.play_pause()
            return True

        if "следующий трек" in command:
            speak("Следующий трек")
            MediaController.next()
            return True

        if "предыдущий трек" in command:
            speak("Предыдущий трек")
            MediaController.previous()
            return True

        if "который час" in command:
            now = datetime.now()
            speak(f"Время {now.hour} часов {now.minute} минут")
            return True

        if (
            "какая сегодня дата" in command 
            or "сегодняшняя дата" in command 
            or "какая дата сегодня" in command
        ):
            try:
                locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8') 
            except locale.Error:
                locale.setlocale(locale.LC_TIME, 'rus_rus')    

            now = datetime.now()

            formatted_date = now.strftime('%A, %d %B %Y года')

            speak(formatted_date)
            return True

        if "поставь таймер" in command or "запусти таймер" in command:
            speak("На какое время поставить таймер?")

            query = take_command()

            if not query:
                speak("Я не расслышал время")
                return True

            seconds = validate_time(query)

            if seconds <= 0:
                speak("Не удалось определить время")
                return True

            timer_manager.create("main", seconds)

            speak(f"Таймер установлен на {format_time(seconds)}")

        if "сколько осталось" in command or "сколько времени осталось" in command:
            remaining = timer_manager.remaining("main")

            if remaining is None:
                speak("Активных таймеров нет")
                return True

            speak(f"Осталось {format_time(remaining)}")

            return True

        if (
            "отмени таймер" in command
            or "удали таймер" in command
            or "останови таймер" in command
        ):
            cancelled = timer_manager.cancel("main")

            if cancelled:
                speak("Таймер отменён")
            else:
                speak("Активных таймеров нет")

            return True

        if "умнож" in command:
            numbers = [int(x) for x in command.split() if x.isdigit()]
    
            if len(numbers) >= 2:
                result = numbers[0] * numbers[1]
                speak(f"Результат: {result}")
    
        if "плюс" in command:
            numbers = [int(x) for x in command.split() if x.isdigit()]
    
            if len(numbers) >= 2:
                result = numbers[0] + numbers[1]
                speak(f"Результат: {result}")
    
        if "минус" in command:
            numbers = [int(x) for x in command.split() if x.isdigit()]
    
            if len(numbers) >= 2:
                result = numbers[0] - numbers[1]
                speak(f"Результат: {result}")
    
        if "дели" in command or "раздели" in command:
            numbers = [int(x) for x in command.split() if x.isdigit()]
    
            if len(numbers) >= 2:
                result = numbers[0] // numbers[1]
                speak(f"Результат: {result}")
    
        if "процент" in command:
            numbers = [int(x) for x in command.split() if x.isdigit()]
    
            if len(numbers) >= 2:
                percent = numbers[0]
                number = numbers[1]
    
                result = number * percent / 100
                speak(f"Результат: {result}")
    
        if "степень" in command:
            numbers = [int(x) for x in command.split() if x.isdigit()]
    
            if len(numbers) >= 2:
                result = numbers[0] ** numbers[1]
                speak(f"Результат: {result}")
    
        if "квадратный корень" in command or "корень" in command:
            numbers = [int(x) for x in command.split() if x.isdigit()]
    
            if numbers:
                result = math.sqrt(numbers[0])
                speak(f"Результат: {result}")

        if "погода" in command or "какая погода" in command:
            speak("В каком городе вы хотите узнать погоду")

            city = take_command()

            if not city:
                speak("Я не расслышал город")
                return True

            weather(city=city)

        if "какие процессы запущены" in command or "что сейчас запущено" in command:
            processes = get_processes()

            if not processes:
                speak("Не удалось получить список процессов")
                return True

            speak(f"Сейчас запущено примерно {len(processes)} процессов")

            return True

        if "какой процесс использует cpu" in command:
            speak("Проверяю загрузку процессора")

            processes = get_cpu_processes(limit=5)

            if not processes:
                speak("Не удалось получить данные о процессах")
                return True
            
            top = processes[0]

            speak(
                f"Больше всего процессор использует "
                f"{top['name']}, {top['cpu']:.0f} процентов"
            )

            return True

        if (
            "закрой discord" in command
            or "закрой дискорд" in command
            or "выключи discord" in command
            or "выключи дискорд" in command
        ):
            success = kill_process("discord.exe")

            if success:
                speak("Discord закрыт")
            else:
                speak("Discord не запущен")

            return True

        if (
            "закрой chrome" in command
            or "закрой хром" in command
            or "выключи chrome" in command
            or "выключи хром" in command
        ):
            success = kill_process("chrome.exe")

            if success:
                speak("Chrome закрыт")
            else:
                speak("Chrome не запущен")

        if (
            "закрой steam" in command
            or "закрой стим" in command
            or "выключи steam" in command
            or "выключи стим" in command
        ):
            success = kill_process("steam.exe")

            if success:
                speak("Steam закрыт")
            else:
                speak("Steam не запущен")   

        if (
            "закрой whatsapp" in command
            or "закрой ватсап" in command
            or "выключи whatsapp" in command
            or "выключи ватсап" in command
        ):
            success = kill_process("WhatsApp.exe")

            if success:
                speak("WhatsApp закрыт")
            else:
                speak("WhatsApp не запущен")

        # проблема в этом коде исправить
        if "переведи слово" in command or "переведи" in command:
            speak("Что перевести на английский")

            text = take_command()

            if not text:
                speak("Можешь повторить")
                return True

            speak("На какой язык перевести")

            language = take_command()

            if not language:
                speak("Можешь повторить, на какой язык перевести")
                return True

            languages = {
                "английский": "en",
                "испанский": "es",
                "немецкий": "de",
                "французский": "fr",
                "турецкий": "tr"
            }

            language = language.lower().strip()

            if language not in languages:
                speak("Я не распознал язык. Попробуй ещё раз")
                return True

            try:
                translation = translate(
                    text=text,
                    to_lang=languages[language]
                )

                speak(f"Перевожу {text}")
                speak(f"Перевод: {translation}")

            except Exception as e:
                print(f"Ошибка перевода: {e}")
                speak("Не удалось выполнить перевод")

            return True

        """
        ------РАБОТАЮТ ЭТИ КОМАНДЫ--------
        нажми Enter
        нажми Escape
        нажми пробел
        нажми Tab
        нажми Backspace
        нажми Delete
        нажми вверх
        нажми вниз
        нажми влево
        нажми вправо
        """

        if "нажми" in command:
            key_name = command.replace("нажми", "").strip()

            if press_key(key_name):
                speak(f"Нажимаю {key_name}")
            else:
                speak(f"Я не знаю такую клавишу: {key_name}")

            return True

        if "кликни" in command:
            mouse_click()
            speak("Клик")
            return True

        if "двойной клик" in command:
            double_click()
            speak("Двойной клик")
            return True

        if (
            "правый клик" in command
            or "нажми правую кнопку" in command
            or "правая кнопка" in command
        ):
            right_click()
            speak("Правая кнопка")
            return True

        if "прокрути вверх" in command:
            scroll_up()
            speak("Прокручиваю вверх")
            return True

        if "прокрути вниз" in command:
            scroll_down()
            speak("Прокручиваю вниз")
            return True

        if "перемести мышку" in command:
            parts = command.split()

            numbers = []

            for part in parts:
                if part.isdigit():
                    numbers.append(int(part))

            if len(numbers) >= 2:
                x = numbers[0]
                y = numbers[1]

                move_mouse(x, y)

                speak(f"Перемещаю мышь в точку {x}, {y}")
            else:
                speak("Назови координаты X и Y")

            return True

        if "мышку вправо" in command:
            move_mouse_relative("вправо")
            speak("Перемещаю мышь вправо")
            return True

        if "мышку влево" in command:
            move_mouse_relative("влево")
            speak("Перемещаю мышь влево")
            return True

        if "мышку вверх" in command:
            move_mouse_relative("вверх")
            speak("Перемещаю мышь вверх")
            return True

        if "мышку вниз" in command:
            move_mouse_relative("вниз")
            speak("Перемещаю мышь вниз")
            return True

        if "выделить" in command or "выдели текст" in command:
            selection()
            speak("Выделяю")
            return True

        if "копировать" in command or "копировать тескт" in command:
            copy()
            speak("Копирую")
            return True

        if (
            "вставь" in command 
            or "вставляй" in command
            or "вставь текст" in command
            or "вставляй текст" in command
        ):
            insert()
            speak("Вставляю")
            return True

        if "закрыть" in command:
            close()
            speak("Закрываю")
            return True

        if "быстро смени окно" in command or "быстро смени" in command:
            fast_switch_between_windows()
            speak("Быстро сменяю окна")
            return True

        if "смени окно" in command or "смени" in command:
            switch_beetween_multiple_windows()
            speak("Сменяю окна")
            return True

        if "сделай скриншот" in command or "скриншот" in command:
            try:
                make_screenshot()

                speak("Скриншот сохранен в папке Рисунки")

            except Exception as e:
                speak("Не удалось сделать скриншот")

            return True

        if (
            "запись экрана" in command
            or "начни запись экрана" in command
            or "начни запись" in command
        ):
            recorder.start()

        elif "останови запись" in command:
            recorder.stop()

        if "интернет" in command or "скорость интернета" in command:
            speak("Подключение к серверам Speedtest.net")
            speak(check_internet_speed())
            return True

        if (
            "создай контакт" in command
            or "создай новый контакт" in command
            or "новый контакт" in command
        ):
            speak("Какое имя хотите дать контакту")

            name = take_command()

            if not name:
                speak("Я не расслышал можешь повторить")
                return True

            speak("Так же можете указать номер телефона в терминале с плюс в началe")
            phone = input("Укажите номер телефона в терминале с плюс в начале: ")

            contact_service.create_contact(name=name, phone=phone)   

        if (
            "выведи все контакты" in command
            or "открой все контакты" in command
        ):
            contacts = contact_service.get_all_contacts()
            
            speak("Вывожу все контакты на терминал")

            for contact in contacts:
                print(f"Имя: {contact.name}, Номер Телефона: {contact.phone}")

        if (
            "напиши сообщение" in command
            or "отправь сообщение" in command
            or "новое сообщение" in command
        ):
            speak("Какому контакту вы хотите отправить сообщение")

            name = take_command()

            if not name:
                speak("Я не расслышал можешь повторить")
                return True

            name = name.replace(" ", "").replace(".", "").lower()

            contacts = contact_service.get_all_names()

            phone = None

            if name in contacts:
                phone = contact_service.get_contact_by_name(name=name)

            if not phone:
                speak("Контакт не найден")
                return False

            speak("Какое сообщение хотите отправить")

            message = take_command()

            if not message:
                speak("Я не расслышал можешь повторить")
                return True


            whatsapp_service.send_message(phone=phone, message=message)

        if "сколько человек видишь" in command or "сколько человек" in command:
            count = camera_pipeline.count_people()

            if count == 0:
                speak("Не вижу людей")
            elif count == 1:
                speak("Я вижу одного человека")
            else:
                speak(f"Я вижу {count} человек")

            return True

        if "включи управление рукой" in command or "запусти управление рукой" in command:    
            computer_control.start()
            speak("Управление рукой включено")

        if "выключи управление рукой" in command or "отключи управление рукой" in command:
            computer_control.stop()
            speak("Управление рукой выключено")

        return False 