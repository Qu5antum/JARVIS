import pyautogui as pg
from pathlib import Path
import time
from datetime import datetime


KEYS = {
    "enter": "enter",
    "энтер": "enter",

    "escape": "esc",
    "эскейп": "esc",

    "пробел": "space",
    "space": "space",

    "tab": "tab",
    "таб": "tab",

    "backspace": "backspace",
    "бекспейс": "backspace",

    "delete": "delete",
    "делит": "delete",

    "home": "home",
    "end": "end",

    "вверх": "up",
    "вниз": "down",
    "влево": "left",
    "вправо": "right",
}

def press_key(key_name: str):
    key = KEYS.get(key_name)

    if key:
        pg.press(key)
        return True

    return False

def move_mouse(x: int, y: int):
    pg.moveTo(x, y, duration=0.3)

def mouse_click():
    pg.click()

def double_click():
    pg.doubleClick()

def right_click():
    pg.rightClick()

def scroll_up():
    pg.scroll(20)

def scroll_down():
    pg.scroll(-20)

def selection():
    pg.hotkey("ctrl", "a")

def copy():
    pg.hotkey("ctrl", "c")

def insert():
    pg.hotkey("ctrl", "v")

def close():
    pg.hotkey("alt", "f4")

def move_mouse_relative(direction: str, amount: int = 100):
    if direction == "вправо":
        pg.moveRel(amount, 0)

    elif direction == "влево":
        pg.moveRel(-amount, 0)

    elif direction == "вверх":
        pg.moveRel(0, -amount)

    elif direction == "вниз":
        pg.moveRel(0, amount)

def make_screenshot():
    pictures_dir = Path.home() / "Pictures" / "JARVIS"

    pictures_dir.mkdir(parents=True, exist_ok=True)

    file_path = pictures_dir / (
        f"screenshot_{datetime.now():%Y-%m-%d_%H-%M-%S}.png"
    )

    screenshot = pg.screenshot()
    screenshot.save(file_path)

    return file_path

def switch_beetween_multiple_windows():
    pg.keyDown('alt')

    pg.press('tab')
    time.sleep(0.1)
    pg.press('tab')

    pg.keyUp('alt')

def fast_switch_between_windows():
    pg.hotkey('alt', 'tab')
