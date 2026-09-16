import logging
from enum import Enum
from pathlib import Path
import yt_dlp


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("download")

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


class Format(str, Enum):
    MP3 = "mp3"
    MP4 = "mp4"


def download_video(url: str, format: Format) -> Path:
    output_template = DOWNLOAD_DIR / "%(title)s.%(ext)s"

    if format == Format.MP3:
        ydl_opts = {
            "outtmpl": str(output_template),
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                }
            ],
        }

    elif format == Format.MP4:
        ydl_opts = {
            "outtmpl": str(output_template),
            "format": (
                "bestvideo[ext=mp4]"
                "+bestaudio[ext=m4a]"
                "/best[ext=mp4]"
                "/best"
            ),
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = Path(ydl.prepare_filename(info))
            filename = filename.with_suffix(f".{format}")

            logger.info(f"Файл скачан: {filename}")

            return filename

    except Exception as e:
        logger.error(f"Error: {e}") 

        raise 
    