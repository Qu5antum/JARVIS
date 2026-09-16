import logging
import numpy as np
import sounddevice as sd

from src.jarvis.command_detect import JarvisMain
from src.jarvis.helper import audio_callback
from src.tts.tts import audio_queue, model
from src.core.config import settings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("download")

jarvis = JarvisMain()
audio_buffer = np.zeros(0, dtype=np.float32)


if __name__ == '__main__':
    try:
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

                if text_clean:
                    logger.info(f"Распознано: {text_clean}")

                    jarvis.execute_command(
                        text_clean
                    )
                    logger.info("---Ожидание новой команды---")

                audio_buffer = np.zeros(
                    0,
                    dtype=np.float32
                )

    except KeyboardInterrupt:
        logger.info("Программа успешно остановлена вручную.")

    except Exception as e:
        logger.info(f"Main Error: {e}")
