from datetime import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QGridLayout, QMessageBox
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PIL import Image, ImageDraw
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
    # Asegurar que la carpeta ImgGames existe
    img_game_dir = os.path.join('Data', 'ImgGames')
    if not os.path.exists(img_game_dir):
        os.makedirs(img_game_dir)

    return saved_carts_path, saved_games_path, img_cart_dir, img_game_dir
saved_carts_path, saved_games_path, img_cart_dir, img_game_dir = conf_carts()

class RoundWindow(QWidget):
    def __init__(self, game_name, round_number, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'Juego: {game_name} - Ronda {round_number}')
        self.showFullScreen()
        self.game_name = game_name
        self.round_number = round_number
        self.parent_window = parent

        self.layout = QVBoxLayout()
        self.create_widgets()
        self.setLayout(self.layout)

    def create_widgets(self):
        # Nombre del juego y número de ronda
        header_label = QLabel(f'Juego: {self.game_name} \nRonda número: {self.round_number}', self)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 16))
        self.layout.addWidget(header_label)

        # Grid para la forma del bingo
        self.create_bingo_grid()

        # Botones de acción
        button_frame = QWidget()
        button_layout = QVBoxLayout(button_frame)
        
        self.save_button = QPushButton("Guardar", self)
        self.save_button.clicked.connect(self.save_round)
        button_layout.addWidget(self.save_button)
        
        cancel_button = QPushButton("Salir", self)
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)
        
        self.layout.addWidget(button_frame)

    def create_bingo_grid(self):
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
        # Guardar la imagen del grid
        self.save_bingo_grid_image()

        # Guardar los datos de la ronda en el archivo Juegos.txt
        self.save_round_data()

        # Mensaje de confirmación
        QMessageBox.information(self, "Guardado", "La ronda ha sido guardada exitosamente.")

        # Iniciar la ventana GameWindow para continuar con el juego
        self.parent_window.load_round_data()

    def save_bingo_grid_image(self):
        # Crear imagen del grid
        img = Image.new('RGB', (300, 300), color='white')
        draw = ImageDraw.Draw(img)
        cell_size = 60
        for i in range(5):
            for j in range(5):
                x0 = j * cell_size
                y0 = i * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size
                color = 'black' if self.bingo_buttons[i][j] and self.bingo_buttons[i][j].isChecked() else 'white'
                draw.rectangle([x0, y0, x1, y1], fill=color, outline='black')
        
        # Guardar imagen del grid 
        img_save_path = os.path.join('Data', 'ImgGames', self.game_name, f'Round_{self.round_number}.png')
        os.makedirs(os.path.dirname(img_save_path), exist_ok=True)
        img.save(img_save_path)
        self.grid_image_path = img_save_path

    def save_round_data(self):
        # Guardar los datos de la ronda en el archivo Juegos.txt
        with open(saved_games_path, 'r') as file:
            games_data = json.load(file)

        game_data = games_data[self.game_name]
        rounds = game_data["rounds"]
        
        round_data = {
            'creation_time': str(datetime.now()),
            'modification_time': None,
            'grid_image': self.grid_image_path}

        rounds[self.round_number] = round_data
        game_data['rounds'] = rounds
        game_data['modification_time'] = str(datetime.now())
        games_data[self.game_name] = game_data

        with open(saved_games_path, 'w') as file:
            json.dump(games_data, file, indent=4)

class GameWindow(QWidget):
    def __init__(self, game_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle('BingoGo')
        self.showFullScreen()
        self.game_name = game_name
        self.round_number = 1

        # Leer los datos existentes del juego
        with open(saved_games_path, 'r') as file:
            self.games = json.load(file)

        #Actualizar detalles del juego
        current_game = self.games[self.game_name]
        self.bingos = current_game["bingos"]
        self.rounds = current_game["rounds"]
        self.creation_time = current_game["creation_time"]
        self.modification_time = current_game["modification_time"]

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.init_ui()

    def init_ui(self):
        # start_new_round
        self.round_window = RoundWindow(self.game_name, self.round_number, self)
        self.round_window.show()

    def load_round_data(self):
        # Cargar los datos de la ronda (grid, imagen, etc.)
        self.round_window.close()
        self.round_start_time = datetime.now()
        self.grid_image_path = f'Data/ImgGames/{self.game_name}/Round_{self.round_number}.png'
        self.init_game_window()

    def init_game_window(self):
        # Nombre de la aplicación 
        self.header_label = QLabel('BingoGo', self)
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setFont(QFont("Arial",30))
        self.layout.addWidget(self.header_label)

        # Numero de la ronda
        self.header_label = QLabel(f'Ronda número: {self.round_number}', self)
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setFont(QFont("Arial",25))
        self.layout.addWidget(self.header_label)

        # Duración de la ronda
        self.duration_label = QLabel("Duración: 00:00:00", self)
        self.duration_label.setAlignment(Qt.AlignCenter)
        self.duration_label.setFont(QFont("Arial", 25))
        self.layout.addWidget(self.duration_label)

        # Configuración del temporizador para actualizar la duración de la ronda
        self.round_duration_timer = QTimer(self)
        self.round_duration_timer.timeout.connect(self.update_round_duration)
        self.round_duration_timer.start(1000)

        # Imagen de la figura a jugar
        image_label = QLabel(self)
        image_label.setPixmap(QPixmap(self.grid_image_path))
        image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(image_label)

        # Entrada para el número y letra que se está jugando
        self.input_layout = QVBoxLayout()
        
        self.number_input = QLineEdit(self)
        self.number_input.setPlaceholderText("Ingrese el número del bingo (1-80)")
        self.input_layout.addWidget(self.number_input)

        self.letter_label = QLabel("Letra: B/I/N/G/O", self)
        self.letter_label.setAlignment(Qt.AlignCenter)
        self.input_layout.addWidget(self.letter_label)

        self.add_number_button = QPushButton("Agregar Número", self)
        self.add_number_button.clicked.connect(self.add_number)
        self.input_layout.addWidget(self.add_number_button)
        
        self.layout.addLayout(self.input_layout)

        # Botones de guardar y salir
        self.save_button = QPushButton("Guardar", self)
        self.save_button.clicked.connect(self.save_game_data)
        self.layout.addWidget(self.save_button)

        self.exit_button = QPushButton("Salir", self)
        self.exit_button.clicked.connect(self.close)
        self.layout.addWidget(self.exit_button)
        
    def update_round_duration(self):
        elapsed_time = datetime.now() - self.round_start_time
        self.duration_label.setText(f"Duración: {str(elapsed_time).split('.')[0]}")

    def add_number(self):
        number = int(self.number_input.text())
        if number < 1 or number > 80:
            QMessageBox.critical(self, "Error", "Por favor, ingrese un número válido entre 1 y 80.")
        self.number_input.clear()

    def save_game_data(self):
        # Guardar los datos de la ronda en el archivo Juegos.txt
        with open(saved_games_path, 'r') as file:
            games_data = json.load(file)
        
        game_data = games_data[self.game_name]
        rounds = game_data["rounds"]
        round_data = {
            'creation_time': str(self.round_start_time),
            'modification_time': None,
            'grid_image': self.grid_image_path}
        
        rounds[self.round_number] = round_data
        game_data['rounds'] = rounds
        game_data['modification_time'] = str(datetime.now())
        games_data[self.game_name] = game_data

        with open(saved_games_path, 'w') as file:
            json.dump(games_data, file, indent=4)

        QMessageBox.information(self, "Guardado", "La ronda ha sido guardada exitosamente.")
        self.close()

    def closeEvent(self, event):
        # Confirmar salida
        reply = QMessageBox.question(self, 'Salir', '¿Estás seguro de que quieres salir?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()