import logging
import os
from faster_whisper import WhisperModel
import asyncio
import edge_tts
import pygame
import tempfile
import numpy as np
import sounddevice as sd
import queue

from src.core.config import settings
from src.jarvis.helper import audio_queue, audio_callback


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("tts")


logger.info("Loading Whisper model...")
model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8",
    cpu_threads=4,
)

VOICE = "ru-RU-DmitryNeural"

pygame.mixer.init()

async def speak_async(text: str) -> None:
    filename = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False,
        ) as temp_file:
            filename = temp_file.name
        communicate = edge_tts.Communicate(
            text=text,
            voice=VOICE,
        )
        await communicate.save(filename)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)

        pygame.mixer.music.unload()

    except Exception as e:
        logger.error(f"TTS error: {e}")

    finally:
        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except PermissionError:
                pass

def speak(text: str) -> None:
    try:
        asyncio.run(
            speak_async(text)
        )
    except Exception as e:
        logger.error(f"Speak error: {e}")

def take_command() -> str | None:
    audio_buffer = np.zeros(0, dtype=np.float32)

    try:
        while not audio_queue.empty():
            try:
                audio_queue.get_nowait()
            except queue.Empty:
                break

        with sd.InputStream(
            samplerate=settings.SAMPLE_RATE,
            channels=settings.CHANNELS,
            blocksize=settings.BLOCK_SIZE,
            callback=audio_callback,
            dtype="float32",
        ):
            logger.info("Слушаю команды...")
            while True:
                chunk = audio_queue.get()
                audio_buffer = np.append(audio_buffer, chunk.flatten())

                if len(audio_buffer) < settings.SAMPLE_RATE * 2.5:
                    continue

                segments, info = model.transcribe(
                    audio_buffer,
                    beam_size=1,
                    language='ru',
                    vad_filter=True,
                    vad_parameters={
                        "min_silence_duration_ms": 400,
                    },
                    condition_on_previous_text=False,
                )

                full_text = "".join([segment.text for segment in segments])
                text_clean = full_text.strip()

                audio_buffer = np.zeros(
                    0,
                    dtype=np.float32
                )

                if not text_clean:
                    speak("Можешь повторить")
                    continue

                logger.info(f"Распознано: {text_clean}")

                return text_clean
    
    except KeyboardInterrupt:
        logger.info("Программа успешно остановлена вручную.")

    except Exception as e:
        logger.info(f"Error: {e}")

    return None
