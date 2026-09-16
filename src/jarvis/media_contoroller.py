import win32api
import win32con


class MediaController:
    @staticmethod
    def play_pause():
        win32api.keybd_event(
            win32con.VK_MEDIA_PLAY_PAUSE,
            0,
            0,
            0
        )

        win32api.keybd_event(
            win32con.VK_MEDIA_PLAY_PAUSE,
            0,
            2,
            0
        )

    @staticmethod
    def next():
        win32api.keybd_event(
            win32con.VK_MEDIA_NEXT_TRACK,
            0,
            0,
            0
        )

        win32api.keybd_event(
            win32con.VK_MEDIA_NEXT_TRACK,
            0,
            2,
            0
        )

    @staticmethod
    def previous():
        win32api.keybd_event(
            win32con.VK_MEDIA_PREV_TRACK,
            0,
            0,
            0
        )

        win32api.keybd_event(
            win32con.VK_MEDIA_PREV_TRACK,
            0,
            2,
            0
        )
