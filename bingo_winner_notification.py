from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import QTimer, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont, QLinearGradient, QPalette
import random

class BingoWinnerWindow(QWidget):
    statistics_command = pyqtSignal()
    def __init__(self, bingo_id):
        super().__init__()
        self.bingo_id = bingo_id
        self.setWindowTitle("¡BINGO!")
        self.setFixedSize(800, 600)
        self.confetti_particles = []
        self.flashing = True

        # Configuración de temporizadores para confeti y fondo parpadeante
        self.confetti_timer = QTimer(self)
        self.confetti_timer.timeout.connect(self.update_confetti)
        self.confetti_timer.start(30)
        
        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self.toggle_flash)
        self.flash_timer.start(500)

        self.initUI()
        self.start_confetti()

    def initUI(self):
        layout = QVBoxLayout()

        # Mensaje de felicitación
        label = QLabel("¡FELICIDADES!", self)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 30, QFont.Bold))
        label.setStyleSheet("color: white;")
        layout.addWidget(label)

        # Mensaje de felicitación
        label = QLabel(f"Has ganado con el cartón: \n{self.bingo_id}\n\n¡Grita BINGO!", self)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 20, QFont.Bold))
        label.setStyleSheet("color: white;")
        layout.addWidget(label)

        # Botón de aceptar
        accept_button = QPushButton("Aceptar", self)
        accept_button.setFont(QFont("Arial", 15, QFont.Bold))
        accept_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px 20px;")
        accept_button.clicked.connect(self.close)
        layout.addWidget(accept_button)

        # Botón de ver estadisticas
        accept_button = QPushButton("Ver estadisticas", self)
        accept_button.setFont(QFont("Arial", 15, QFont.Bold))
        accept_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px 20px;")
        accept_button.clicked.connect(self.statistics)
        layout.addWidget(accept_button)

        self.setLayout(layout)

    def start_confetti(self):
        for _ in range(100):
            x = random.randint(0, self.width())
            y = random.randint(-200, 0)
            color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.confetti_particles.append({"position": QPoint(x, y), "color": color})

    def update_confetti(self):
        for particle in self.confetti_particles:
            particle["position"].setY(particle["position"].y() + random.randint(2, 5))
            if particle["position"].y() > self.height():
                particle["position"].setY(random.randint(-100, 0))
                particle["position"].setX(random.randint(0, self.width()))
        self.update()

    def toggle_flash(self):
        palette = QPalette()
        if self.flashing:
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(255, 0, 0))
            gradient.setColorAt(1, QColor(255, 255, 0))
            palette.setBrush(QPalette.Window, gradient)
        else:
            palette.setColor(QPalette.Window, Qt.black)
        self.setPalette(palette)
        self.flashing = not self.flashing

    def paintEvent(self, event):
        painter = QPainter(self)
        for particle in self.confetti_particles:
            painter.setBrush(particle["color"])
            painter.drawEllipse(particle["position"], 10, 10)

    def statistics(self):
        self.statistics_command.emit()
        self.close()
