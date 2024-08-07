from datetime import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QMessageBox
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
import json
import os

# Configuración inicial
def conf_carts():
    # Ruta de los BingosInfo
    saved_carts_path = os.path.join('Data', "Bingos.txt")
    # Ruta de los juegosInfo
    saved_games_path = os.path.join('Data', "Juegos.txt")
    # Crear carpeta data si no existe
    if not os.path.exists('Data'):
        os.makedirs('Data')
    # Crear txt Bingos si no existe
    if not os.path.exists(saved_carts_path):
        with open(saved_carts_path, 'w') as file:
            json.dump({}, file)
    # Crear txt Juegos si no existe
    if not os.path.exists(saved_games_path):
        with open(saved_games_path, 'w') as file:
            json.dump({}, file)
    # Asegurar que la carpeta ImgCard existe
    img_cart_dir = os.path.join('Data', 'ImgCard')
    if not os.path.exists(img_cart_dir):
        os.makedirs(img_cart_dir)

    return saved_carts_path, saved_games_path, img_cart_dir
saved_carts_path, saved_games_path, img_cart_dir = conf_carts()

class GameWindow(QWidget):
    def __init__(self, game_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle('BingoGo')
        self.showMaximized()

        self.game_name = game_name
        
        # Layout principal
        self.layout = QVBoxLayout()
        
        # Leer los datos existentes del juego
        with open(saved_games_path, 'r') as file:
            self.games = json.load(file)
        
        self.current_game = self.games[self.game_name]

        # Crear widgets
        self.create_widgets()

        # Establecer el layout
        self.setLayout(self.layout)

    def create_widgets(self):
        # Título de la aplicación
        title_label = QLabel("BingoGo", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 30))
        self.layout.addWidget(title_label)
        
        # Información del juego
        game_info_label = QLabel(f"Juego: {self.game_name}\nRonda número: {len(self.current_game['rounds']) + 1}", self)
        game_info_label.setAlignment(Qt.AlignCenter)
        game_info_label.setFont(QFont("Arial", 26))
        self.layout.addWidget(game_info_label)
        
        # Instrucciones
        instructions_label = QLabel("Inserte la forma del bingo que se jugará", self)
        instructions_label.setAlignment(Qt.AlignCenter)
        instructions_label.setFont(QFont("Arial", 24))
        self.layout.addWidget(instructions_label)
                
        self.create_grid()

        # Botones de acción
        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)
        
        save_button = QPushButton("Guardar", self)
        save_button.clicked.connect(self.save_round)
        button_layout.addWidget(save_button)
        
        exit_button = QPushButton("Salir", self)
        exit_button.clicked.connect(self.close)
        button_layout.addWidget(exit_button)
        
        self.layout.addWidget(button_frame)

    def create_grid(self):
        # Cartón de bingo en blanco
        self.bingo_grid = QGridLayout()
        self.bingo_buttons = []
        
        # Agregar las letras B, I, N, G, O
        headers = ['B', 'I', 'N', 'G', 'O']
        for i, header in enumerate(headers):
            label = QLabel(header, self)
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont("Arial", 12, QFont.Bold))
            self.bingo_grid.addWidget(label, 0, i)

        # Crear botones de las casillas de bingo
        for i in range(5):
            row = []
            for j in range(5):
                if i == 2 and j == 2:  # Centro del grid
                    button = QLabel("GO", self)
                    button.setFixedSize(60, 60)
                    button.setAlignment(Qt.AlignCenter)
                    button.setStyleSheet("background-color: lightgray; font-size: 20px; font-weight: bold;")
                    self.bingo_grid.addWidget(button, i + 1, j)
                    row.append(None)
                    continue

                button = QPushButton("", self)
                button.setFixedSize(60, 60)
                button.setCheckable(True)
                button.setStyleSheet("background-color: white;")
                button.clicked.connect(self.toggle_button_color)
                self.bingo_grid.addWidget(button, i + 1, j)  # Desplazar una fila hacia abajo
                row.append(button)
            self.bingo_buttons.append(row)
        
        self.layout.addLayout(self.bingo_grid)

    def toggle_button_color(self):
        button = self.sender()
        if button.isChecked():
            button.setStyleSheet("background-color: black;")
        else:
            button.setStyleSheet("background-color: white;")

    def save_round(self):
        round_number = len(self.current_game['rounds']) + 1
        round_data = {
            "pattern": [],
            "creation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modification_time": None
        }
        
        for i in range(5):
            row = []
            for j in range(5):
                if self.bingo_buttons[i][j] is None: # Centro del grid
                    row.append(0)  
                    continue

                if self.bingo_buttons[i][j].isChecked(): row.append(1)
                else: row.append(0)

            round_data["pattern"].append(row)
        
        self.current_game['rounds'][round_number] = round_data
        self.current_game['modification_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Guardar datos en Juegos.txt
        self.save_game_to_file()
        
        QMessageBox.information(self, "Ronda Guardada", f"La ronda {round_number} ha sido guardada exitosamente.")

    def save_game_to_file(self):        
        # Actualizar datos del juego en el archivo
        with open(saved_games_path, 'w') as file:
            json.dump(self.games, file, indent=4)

