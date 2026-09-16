import logging
import queue
from pycaw.pycaw import AudioUtilities
import re
from translate import Translator
import speedtest

device = AudioUtilities.GetSpeakers()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("helper")
audio_queue = queue.Queue()


def audio_callback(indata, frames, time, status) -> None:
    if status:
        logger.warning(f"Audio status: {status}")

    audio_queue.put(indata.copy())

def get_volume_controller():
    device = AudioUtilities.GetSpeakers()
    return device.EndpointVolume


def is_muted():
    volume = get_volume_controller()
    return bool(volume.GetMute())


def mute():
    volume = get_volume_controller()
    volume.SetMute(1, None)


def unmute():
    volume = get_volume_controller()
    volume.SetMute(0, None)


def get_volume():
    volume = get_volume_controller()
    return round(volume.GetMasterVolumeLevelScalar() * 100)


def set_volume(percent: int):
    percent = max(0, min(100, percent))

    volume = get_volume_controller()
    volume.SetMasterVolumeLevelScalar(percent / 100, None)

def format_time(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    result = []

    if hours:
        result.append(f"{hours} ч.")

    if minutes:
        result.append(f"{minutes} мин.")

    if seconds:
        result.append(f"{seconds} сек.")

    return " ".join(result) if result else "0 сек."

def validate_time(query: str) -> int:
    query = query.lower()

    hours = 0
    minutes = 0
    seconds = 0

    hour_match = re.search(r"(\d+)\s*(час|часа|часов)", query)
    minute_match = re.search(r"(\d+)\s*(минут|минуты|мин)", query)
    second_match = re.search(r"(\d+)\s*(секунд|секунды|сек)", query)

    if hour_match:
        hours = int(hour_match.group(1))

    if minute_match:
        minutes = int(minute_match.group(1))

    if second_match:
        seconds = int(second_match.group(1))

    total_seconds = (
        hours * 3600 +
        minutes * 60 +
        seconds
    )

    return total_seconds

def translate(text: str, to_lang: str = "en") -> str:
    translator = Translator(from_lang="ru", to_lang=to_lang)
    return translator.translate(text)

def check_internet_speed() -> str:
    st = speedtest.Speedtest()
    
    st.get_best_server()
    download_speed = st.download()
    upload_speed = st.upload()
    
    ping = st.results.ping
    
    download_mbs = download_speed / 1_000_000
    upload_mbs = upload_speed / 1_000_000
    
    return f"Скорость загрузки: {download_mbs:.2f} Мбит в секунду, Скорость отдачи: {upload_mbs:.2f} Мбит в секунду, Пинг: {ping:.2f} ms"
