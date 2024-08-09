from datetime import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QGridLayout, QMessageBox
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PIL import Image, ImageDraw, ImageFont
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

from PyQt5.QtWidgets import QApplication, QMainWindow

class GameProcess(QMainWindow):
    def __init__(self, game_name):
        super().__init__()
        self.game_name = game_name
        self.round_number = 0
        self.current_window = None

    def start_game(self):
        self.start_new_round()

    def start_new_round(self):
        self.round_number += 1

        # Cerrar la ventana anterior si existe
        if self.current_window is not None:
            self.current_window.close()

        # Crear y mostrar la ventana de la ronda
        self.round_window = RoundWindow(self.game_name, self.round_number)
        self.round_window.figure_make.connect(self.load_game_window)
        
        self.current_window = self.round_window
        self.round_window.show()

    def load_game_window(self):
        # Cerrar la ventana anterior
        self.current_window.close()

        # Crear y mostrar la ventana del juego
        self.game_window = GameWindow(self.game_name)
        self.current_window = self.game_window
        self.game_window.round_completed.connect(self.start_new_round)
        self.game_window.show()

class RoundWindow(QWidget):
    figure_make = pyqtSignal()
    def __init__(self, game_name, round_number, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'Juego: {game_name} - Ronda {round_number}')
        self.showFullScreen()
        self.game_name = game_name
        self.round_number = round_number

        self.layout = QVBoxLayout()
        self.create_widgets()
        self.setLayout(self.layout)

    def create_widgets(self):
        # Nombre de la app
        app_name = QLabel("BingoGO", self)
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setFont(QFont("Arial", 50))
        self.layout.addWidget(app_name)

        # Nombre del juego
        header_label = QLabel(f'Juego: {self.game_name}', self)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 30))
        self.layout.addWidget(header_label)

        # Numero de la ronda
        header_label_number = QLabel(f'Ronda número: {self.round_number}', self)
        header_label_number.setAlignment(Qt.AlignCenter)
        header_label_number.setFont(QFont("Arial", 25))
        self.layout.addWidget(header_label_number)

        # Instrucciones
        instrucciones = QLabel('Presione sobre las casillas que se jugarán en esta ronda:', self)
        instrucciones.setAlignment(Qt.AlignCenter)
        instrucciones.setFont(QFont("Arial", 15))
        self.layout.addWidget(instrucciones)

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

        print(f"... ...\nRonda {self.round_number} en juego.")

        # Mensaje de confirmación
        QMessageBox.information(self, "Guardado", "La ronda ha sido guardada exitosamente.")

        # Iniciar la ventana GameWindow para continuar con el juego
        self.figure_make.emit()  # Emitir la señal cuando se completa la ronda

    def save_bingo_grid_image(self):
        # Crear y guardar la imagen del grid con encabezado BINGO y GO en el centro
        img = Image.new('RGB', (300, 360), color='white')
        draw = ImageDraw.Draw(img)
        cell_size = 60
        font = ImageFont.truetype("arial.ttf", 20)

        # Agregar encabezado "BINGO"
        headers = ['B', 'I', 'N', 'G', 'O']
        for i, header in enumerate(headers):
            x0 = i * cell_size
            y0 = 0
            draw.text((x0 + cell_size // 2 - 10, y0 + 10), header, fill='black', font=font)

        # Dibujar el grid y llenar con colores o texto según corresponda
        for i in range(5):
            for j in range(5):
                x0 = j * cell_size
                y0 = (i + 1) * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size
                color = 'black' if self.bingo_buttons[i][j] and self.bingo_buttons[i][j].isChecked() else 'white'
                draw.rectangle([x0, y0, x1, y1], fill=color, outline='black')

                # Agregar "GO" en el centro
                if i == 2 and j == 2:
                    draw.text((x0 + 15, y0 + 10), "GO", fill='black', font=font)

        img_save_path = os.path.join('Data', 'ImgGames', self.game_name, f'Round_{self.round_number}.png')
        os.makedirs(os.path.dirname(img_save_path), exist_ok=True)
        img.save(img_save_path)

        self.grid_shape = [[button.isChecked() if button else False for button in row] for row in self.bingo_buttons]        
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
    round_completed = pyqtSignal()
    def __init__(self, game_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle('BingoGo')
        self.showFullScreen()
        self.game_name = game_name

        self.load_round_data()
        self.layout = QVBoxLayout()
        
        self.setLayout(self.layout)
        self.create_widgets()
          
    def load_round_data(self):
        # Leer los datos existentes del juego
        with open(saved_games_path, 'r') as file:
            self.games = json.load(file)

        #Actualizar detalles del juego
        current_game = self.games[self.game_name]
        self.bingos = current_game["bingos"]
        self.rounds = current_game["rounds"]
        self.round_number = len(self.rounds) 
        self.creation_time = current_game["creation_time"]
        self.modification_time = current_game["modification_time"]

        # Cargar los datos de la ronda (grid, imagen, etc.)
        self.round_start_time = datetime.now()
        self.grid_image_path = f'Data/ImgGames/{self.game_name}/Round_{self.round_number}.png'

    def create_widgets(self):
        # Nombre de la app
        app_name = QLabel("BingoGO", self)
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setFont(QFont("Arial", 50))
        self.layout.addWidget(app_name)

        # Nombre del juego
        header_label = QLabel(f'Juego: {self.game_name}', self)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 30))
        self.layout.addWidget(header_label)

        # Numero de la ronda
        header_label_number = QLabel(f'Ronda número: {self.round_number}', self)
        header_label_number.setAlignment(Qt.AlignCenter)
        header_label_number.setFont(QFont("Arial", 25))
        self.layout.addWidget(header_label_number)

        # Duración de la ronda
        self.duration_label = QLabel("Duración: 00:00:00", self)
        self.duration_label.setAlignment(Qt.AlignCenter)
        self.duration_label.setFont(QFont("Arial", 10))
        self.layout.addWidget(self.duration_label)
        
        # Configuración del temporizador para actualizar la duración de la ronda
        self.round_duration_timer = QTimer(self)
        self.round_duration_timer.timeout.connect(self.update_round_duration)
        self.round_duration_timer.start(1000)

        # Forma de Bingo que se jugará
        self.instrucciones_image_label = QLabel("La forma del Bingo que se jugará es la siguiente:", self)
        self.instrucciones_image_label.setAlignment(Qt.AlignCenter)
        self.instrucciones_image_label.setFont(QFont("Arial", 15))
        self.layout.addWidget(self.instrucciones_image_label)

        # Imagen de la figura a jugar
        image_label = QLabel(self)
        image_label.setPixmap(QPixmap(self.grid_image_path))
        image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(image_label)

        # Entrada para el número y letra que se está jugando
        self.input_layout = QVBoxLayout()
        
        # Entrada para el número y letra que se está jugando        
        # Agregar acciones del juego

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