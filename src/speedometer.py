from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QFontDatabase, QRadialGradient, QBrush
import math

class SpeedometerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.speed = 0
        self.power = 0
        self.setMinimumSize(300, 300)
        self.setMaximumSize(400, 400)
        self.setFocusPolicy(Qt.StrongFocus)
        # Load Lexend-Thin font if available
        font_path = "Fonts/Lexend-Thin.ttf"
        if QFontDatabase.addApplicationFont(font_path) != -1:
            self.lexend_font = QFont("Lexend Thin", 24, QFont.Normal)
            self.lexend_font_small = QFont("Lexend Thin", 16, QFont.Normal)
        else:
            self.lexend_font = QFont("Arial", 24, QFont.Normal)
            self.lexend_font_small = QFont("Arial", 16, QFont.Normal)

    def set_speed(self, value):
        self.speed = max(0, min(300, value))
        self.power = self.speed * 10  # Example: 10W per mph
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - 10
        arc_width = 16

        # Draw background circle (with cutout at bottom)
        painter.setPen(QPen(QColor('#222'), 8))
        painter.setBrush(QColor('#111'))
        painter.drawArc(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius, 225 * 16, -270 * 16)
        painter.setBrush(Qt.NoBrush)

        # Draw ticks (every 20 units)
        painter.setPen(QPen(QColor('#444'), 2))
        for i in range(0, 301, 20):
            angle = 225 - (i / 300) * 270
            rad = math.radians(angle)
            x1 = center.x() + (radius - 10) * math.cos(rad)
            y1 = center.y() - (radius - 10) * math.sin(rad)
            x2 = center.x() + radius * math.cos(rad)
            y2 = center.y() - radius * math.sin(rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Draw radial gradient progress arc (fill)
        if self.speed > 0:
            # Opacity increases with speed
            opacity = int(50 + (205 * (self.speed / 300)))  # 50-255
            grad = QRadialGradient(center, radius)
            grad.setColorAt(0.0, QColor(0,255,234,0))
            grad.setColorAt(0.7, QColor(0,255,234,opacity//2))
            grad.setColorAt(1.0, QColor(0,255,234,opacity))
            arc_pen = QPen(QBrush(grad), arc_width)
            arc_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(arc_pen)
            span_angle = int((self.speed / 300) * 270 * 16)
            painter.drawArc(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius, 225 * 16, -span_angle)

        # Draw cutout lines from arc endpoints to center
        start_angle = 225
        end_angle = 225 - 270
        for angle in [start_angle, end_angle]:
            rad = math.radians(angle)
            x = center.x() + radius * math.cos(rad)
            y = center.y() - radius * math.sin(rad)
            painter.setPen(QPen(QColor('#444'), 2))
            painter.drawLine(center.x(), center.y(), int(x), int(y))

        # Draw speed text (Lexend Thin, no box), moved up more
        painter.setPen(QColor('#ccc'))
        painter.setFont(self.lexend_font)
        speed_text = f"{self.speed} mph"
        text_rect = rect.adjusted(0, -int(radius/1.5), 0, -int(radius/6))  # Move up even more
        painter.drawText(text_rect, Qt.AlignCenter, speed_text)

        # Draw power draw text below speed
        painter.setFont(self.lexend_font_small)
        power_text = f"{self.power}W"
        power_rect = rect.adjusted(0, -int(radius/6), 0, -int(radius/3))
        painter.drawText(power_rect, Qt.AlignCenter, power_text)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.set_speed(self.speed + 1)
        elif event.key() == Qt.Key_Down:
            self.set_speed(self.speed - 1)
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event):
        self.setStyleSheet("border: 2px solid #007acc;")
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setStyleSheet("")
        super().focusOutEvent(event)
