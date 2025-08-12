# moving_dots_overlay.py
# Zweck: Vollbild-Overlay mit bewegten Punkten zur Vorbeugung von Reisekrankheit / Motion Sickness.
#        Die bewegten Punkte simulieren Bewegung auf dem Bildschirm und können helfen, 
#        Übelkeit bei empfindlichen Personen zu reduzieren, wenn sich der eigentliche Bildschirminhalt nicht bewegt.
# Hinweis: Klick-durchlässig auf Windows (kein Einfluss auf darunterliegende Anwendungen).
# Hotkey: Strg+Umschalt+Q zum Beenden (unter Windows oft Adminrechte nötig).

import sys
import random
import math
import ctypes
from PyQt5 import QtCore, QtGui, QtWidgets
import keyboard  # für globalen Hotkey (Auf Windows oft Adminrechte erforderlich)

# Windows constants for extended window styles
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOPMOST = 0x00000008

class Dot:
    def __init__(self, rect: QtCore.QRect):
        self.reset(rect)

    def reset(self, rect: QtCore.QRect):
        self.x = random.uniform(0, rect.width())
        self.y = random.uniform(0, rect.height())
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(10, 120)  # pixels / second
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        self.radius = random.uniform(3, 9)
        self.alpha = random.uniform(0.25, 0.9)

    def step(self, dt, rect: QtCore.QRect):
        self.x += self.vx * dt
        self.y += self.vy * dt
        # bounce on edges
        if self.x < 0:
            self.x = 0
            self.vx *= -1
        if self.x > rect.width():
            self.x = rect.width()
            self.vx *= -1
        if self.y < 0:
            self.y = 0
            self.vy *= -1
        if self.y > rect.height():
            self.y = rect.height()
            self.vy *= -1

class OverlayWindow(QtWidgets.QWidget):
    def __init__(self, dots_count=40, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool
        )
        screens = QtWidgets.QApplication.screens()
        geom = QtCore.QRect()
        for s in screens:
            geom = geom.united(s.geometry())
        self.setGeometry(geom)

        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self.on_timeout)
        self._last_ts = QtCore.QTime.currentTime()

        self.dots = [Dot(self.rect()) for _ in range(dots_count)]
        self._timer.start()
        self.setWindowTitle("MovingDotsOverlay – Anti-Reisekrankheit")

        if sys.platform.startswith("win"):
            self.set_click_through()

    def set_click_through(self):
        hwnd = self.winId().__int__()
        gwl = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        new_style = gwl | WS_EX_LAYERED | WS_EX_TRANSPARENT
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
        ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)

    def on_timeout(self):
        now = QtCore.QTime.currentTime()
        dt_ms = self._last_ts.msecsTo(now)
        dt = dt_ms / 1000.0 if dt_ms > 0 else 0.016
        self._last_ts = now

        r = self.rect()
        for d in self.dots:
            d.step(dt, r)
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        for d in self.dots:
            color = QtGui.QColor(255, 255, 255)
            alpha = int(d.alpha * 255)
            color.setAlpha(alpha)
            painter.setBrush(QtGui.QBrush(color))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawEllipse(QtCore.QPointF(d.x, d.y), d.radius, d.radius)
        painter.end()

def main():
    app = QtWidgets.QApplication(sys.argv)
    overlay = OverlayWindow(dots_count=60)
    overlay.show()

    try:
        keyboard.add_hotkey('ctrl+shift+q', lambda: QtCore.QCoreApplication.quit())
    except Exception as e:
        print("Warnung: Hotkey konnte nicht registriert werden. Eventuell Adminrechte nötig.", e)
        print("Beenden alternativ über Task-Manager oder das Schließen der Python-Prozessinstanz.")

    print("Overlay gestartet – Beenden mit Ctrl+Shift+Q (sofern Hotkey registriert wurde).")
    print("Dieses Overlay dient dazu, Motion Sickness / Reisekrankheit zu verhindern, indem es dem Körper Bewegung simuliert.")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
