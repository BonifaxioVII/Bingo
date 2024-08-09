from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QLabel, 
                            QPushButton, QGridLayout, QMessageBox,
                            QHBoxLayout, QComboBox, QMainWindow, QGroupBox, QScrollArea) 
from PyQt5.QtGui import QImage, QFont, QPixmap, QPainter, QColor
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

class BingoVisualizer(QWidget):
    def __init__(self, bingo_id, bingo_numbers, yellow_highlights=None, red_highlights=None, parent=None):
        super().__init__(parent)
        self.bingo_id = bingo_id
        self.bingo_numbers = bingo_numbers
        self.yellow_highlights = yellow_highlights if yellow_highlights else []
        self.red_highlights = red_highlights if red_highlights else []

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f'Bingo ID: {self.bingo_id}')
        self.setGeometry(100, 100, 500, 500)

        layout = QGridLayout(self)

        # Crear encabezados de BINGO
        headers = ['B', 'I', 'N', 'G', 'O']
        for col, header in enumerate(headers):
            header_label = QLabel(header, self)
            header_label.setAlignment(Qt.AlignCenter)
            header_label.setFont(QFont("Arial", 14, QFont.Bold))
            layout.addWidget(header_label, 0, col)

        # Crear la cuadrícula de bingo
        for row, row_values in enumerate(self.bingo_numbers):
            for col, number in enumerate(row_values):
                # Manejar el valor central que debe ser "GO"
                if row == 2 and col == 2:
                    label = QLabel("GO", self)
                    label.setAlignment(Qt.AlignCenter)
                    label.setFont(QFont("Arial", 14, QFont.Bold))
                    label.setStyleSheet("background-color: lightgray;")  # Color especial para la casilla central
                    continue

                label = QLabel(str(number), self)
                label.setAlignment(Qt.AlignCenter)
                label.setFont(QFont("Arial", 12))

                # Resaltar la casilla según el tipo de resaltado
                if (row, col) in self.yellow_highlights:
                    label.setStyleSheet("background-color: yellow;")
                elif (row, col) in self.red_highlights:
                    label.setStyleSheet("background-color: red;")

                layout.addWidget(label, row + 1, col)  # +1 para dejar espacio para el encabezado

        self.setLayout(layout)

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

        self.grid_image_path = img_save_path

    def save_round_data(self):
        # Guardar los datos de la ronda en el archivo Juegos.txt
        with open(saved_games_path, 'r') as file:
            games_data = json.load(file)

        game_data = games_data[self.game_name]
        rounds = game_data["rounds"]
        
        # Crear la matriz de la figura con 0s y 1s
        grid_matrix = [[1 if button and button.isChecked() else 0 for button in row] for row in self.bingo_buttons]

        round_data = {
            'creation_time': str(datetime.now()),
            'modification_time': None,
            'grid_image': self.grid_image_path,
            'grid_matrix': grid_matrix,
            'actions':[]}

        rounds[self.round_number] = round_data
        game_data['rounds'] = rounds
        game_data['modification_time'] = str(datetime.now())
        games_data[self.game_name] = game_data

        with open(saved_games_path, 'w') as file:
            json.dump(games_data, file, indent=4)

class GameWindow(QWidget):
    round_completed = pyqtSignal()
    def __init__(self, game_name, parent=None):
        # Establecer ScrollBar
        super().__init__(parent)
        self.setWindowTitle('BingoGo')
        self.showFullScreen()
        self.game_name = game_name

        self.load_round_data()
        self.load_bingos_data()

        # Crear un layout principal
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # Crear un área de scroll
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        # Crear un widget de contenedor para el scroll area
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)

        # Crear el layout que contendrá todos los widgets de la ventana
        self.layout = QVBoxLayout(self.scroll_widget)
        
        # Agregar el scroll area al layout principal
        self.main_layout.addWidget(self.scroll_area)
        
        self.create_widgets()
          
    def load_round_data(self):
        # Leer los datos existentes del juego
        with open(saved_games_path, 'r') as file:
            self.games = json.load(file)

        #Diccionarios base
        self.current_game = self.games[self.game_name]
        self.round_number = str(len(self.current_game['rounds']))   
        self.current_round = self.current_game['rounds'][self.round_number]
        self.round_start_time = datetime.now()

    def load_bingos_data(self):
        self.bingos_carts = {}

        # Leer los datos existentes de los bingos
        with open(saved_carts_path, 'r') as file:
            bingos = json.load(file)

        for key, values in bingos.items():
            if key in self.current_game["bingos"]:
                self.bingos_carts[key] = values["bingo_numbers"]

    def create_widgets(self):
        # Nombre de la app
        app_name = QLabel("BingoGO", self)
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setFont(QFont("Arial", 50))
        self.layout.addWidget(app_name)

        # Nombre del juego
        header_label = QLabel(f'Juego: {self.game_name}', self)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 20))
        self.layout.addWidget(header_label)

        # Numero de la ronda
        header_label_number = QLabel(f'Ronda número: {self.round_number}', self)
        header_label_number.setAlignment(Qt.AlignCenter)
        header_label_number.setFont(QFont("Arial", 20))
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

        # Instrucciones de accionar
        self.instrucciones_acciones = QLabel("Escriba las letras y numeros que vayan dictando:", self)
        self.instrucciones_acciones.setAlignment(Qt.AlignCenter)
        self.instrucciones_acciones.setFont(QFont("Arial", 15))
        self.layout.addWidget(self.instrucciones_acciones)

        # Agregar acciones del juego
        self.actions_game()

        # Forma de Bingo que se jugará
        self.instrucciones_image_label = QLabel("La forma del Bingo que se jugará es la siguiente:", self)
        self.instrucciones_image_label.setAlignment(Qt.AlignCenter)
        self.instrucciones_image_label.setFont(QFont("Arial", 15))
        self.layout.addWidget(self.instrucciones_image_label)

        # Imagen de la figura a jugar
        image_label = QLabel(self)
        image_label.setPixmap(QPixmap(self.current_round['grid_image']))
        image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(image_label)
   
        # Botones de guardar y salir
        self.save_buttons()

        # Grupo de visualización de cartones de Bingo
        self.create_bingo_visualization()
 
    def actions_game(self):
        # Entrada para el número y letra que se está jugando
        self.input_layout = QHBoxLayout()
        
        # Desplegable de letras B, I, N, G, O
        self.letter_dropdown = QComboBox(self)
        self.letter_dropdown.addItems(['B', 'I', 'N', 'G', 'O'])
        self.letter_dropdown.setFont(QFont("Arial", 20))
        self.letter_dropdown.setMaximumWidth(150)
        self.input_layout.addWidget(self.letter_dropdown)

        # Espacio para ingresar un número
        self.number_input = QLineEdit(self)
        self.number_input.setPlaceholderText("Ingrese el número")
        self.number_input.setFont(QFont("Arial", 20))
        self.number_input.setMaximumWidth(500)
        self.input_layout.addWidget(self.number_input)

        self.input_layout.setAlignment(Qt.AlignCenter)
        self.layout.addLayout(self.input_layout)

    def save_buttons(self):
        # Botón "Jugar"
        self.play_button = QPushButton("Jugar", self)
        self.play_button.clicked.connect(self.check_bingo_card)
        self.layout.addWidget(self.play_button)

        # Botón "Salir"
        self.exit_button = QPushButton("Salir", self)
        self.exit_button.clicked.connect(self.close)
        self.layout.addWidget(self.exit_button)

    def create_bingo_visualization(self):
        self.bingo_group_box = QGroupBox("Visualización de Bingos")
        self.bingo_layout = QVBoxLayout()

        # Crear un widget de visualización por cada cartón de Bingo
        self.bingo_widgets = {}
        for bingo_name in self.bingos_carts.keys():
            label = QLabel(f"Bingo: {bingo_name}")
            label.setFont(QFont("Arial", 15))
            self.bingo_layout.addWidget(label)

            bingo_view = QLabel(self)
            bingo_view.setAlignment(Qt.AlignCenter)
            self.bingo_layout.addWidget(bingo_view)

            self.bingo_widgets[bingo_name] = bingo_view

        self.bingo_group_box.setLayout(self.bingo_layout)
        self.layout.addWidget(self.bingo_group_box)

    def update_round_duration(self):
        elapsed_time = datetime.now() - self.round_start_time
        self.duration_label.setText(f"Duración: {str(elapsed_time).split('.')[0]}")

    def check_bingo_card(self):
        letter = self.letter_dropdown.currentText()
        number_input = self.number_input.text().strip()
        # Validar que el número no esté vacío
        if not number_input:
            QMessageBox.critical(self, "Error", "El campo del número no puede estar vacío.")
            return

        # Validar que el número ingresado sea un número entero
        try: number = int(number_input)
        except ValueError:
            QMessageBox.critical(self, "Error", "Por favor, ingrese un número válido.")
            return

        # Validar que el número esté en el rango permitido (1-80)
        if number < 1 or number > 80:
            QMessageBox.critical(self, "Error", "Por favor, ingrese un número entre 1 y 80.")
            return

        # Formatear la acción actual
        self.current_action = f"{letter}{number_input}"

        # Verificar si la acción ya está en la lista de acciones
        if self.current_action in self.current_round['actions']:
            QMessageBox.critical(self, "Acción repetida", f"La casilla {self.current_action} ya ha sido jugada en esta ronda.")
            return

        # Confirmar la casilla antes de jugar
        confirmation = QMessageBox.question(self, "Confirmar casilla",
                                            f"¿Se juega la casilla {letter}{number}?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirmation == QMessageBox.No:
            return
        
        self.save_game_data()
        self.process_bingo()

    def process_bingo(self):
        for bingo_name, bingo_numbers in self.bingos_carts.items():
            red_highlight, yellow_highlight = self.process_bingo_actions(bingo_numbers, 
                                                                         self.current_round["grid_matrix"], 
                                                                         self.current_round["actions"])
        
            # Actualizar la visualización del cartón de Bingo
            self.update_bingo_visualization(bingo_name, bingo_numbers, red_highlight, yellow_highlight)

    def process_bingo_actions(self, bingo_numbers, grid_matrix, actions):       
        # Diccionario para asociar las letras con los índices de las columnas
        column_mapping = {'B': 0, 'I': 1, 'N': 2, 'G': 3, 'O': 4}

        # Listas para guardar las acciones resaltadas
        red_highlight = []
        yellow_highlight = []

        for action in actions:
            letter = action[0]  # Primera parte de la acción (B, I, N, G, O)
            number = int(action[1:])  # Parte numérica de la acción

            # Determinar el índice de la columna con base en la letra
            column_index = column_mapping[letter]

            # Buscar el número en la columna correspondiente
            for row_index in range(len(bingo_numbers)):
                if bingo_numbers[row_index][column_index] == number:
                    # Verificar si la casilla está marcada en grid_matrix
                    if grid_matrix[row_index][column_index] == 1:
                        red_highlight.append(action)
                    else:
                        yellow_highlight.append(action)
                    break  # Salir del bucle una vez se ha encontrado la acción

        return red_highlight, yellow_highlight

    def update_bingo_visualization(self, bingo_name, bingo_numbers, red_highlight, yellow_highlight):
        # Crear una imagen del cartón de Bingo
        img = QImage(300, 360, QImage.Format_RGB32)
        img.fill(Qt.white)

        painter = QPainter(img)
        cell_size = 60
        font = QFont("Arial", 10)
        painter.setFont(font)

        #Encabezados
        headers = ['B', 'I', 'N', 'G', 'O']
        for i, header in enumerate(headers):
            x0 = i * cell_size
            y0 = 0
            painter.drawText(x0 + cell_size // 2 - 10, y0 + 30, header)

        #Grid
        for i in range(5):
            for j in range(5):
                x0 = j * cell_size
                y0 = (i + 1) * cell_size

                action = f"{headers[j]}{bingo_numbers[i][j]}"
                if action in red_highlight:
                    color = QColor('red')
                elif action in yellow_highlight:
                    color = QColor('yellow')
                else:
                    color = QColor('white')

                painter.fillRect(x0, y0, cell_size, cell_size, color)
                painter.drawRect(x0, y0, cell_size, cell_size)
                painter.drawText(x0 + 20, y0 + 35, str(bingo_numbers[i][j]))

        painter.end()
        
        pixmap = QPixmap.fromImage(img)
        self.bingo_widgets[bingo_name].setPixmap(pixmap)    
    
    def save_game_data(self):
        #Actualizar ronda 
        self.current_round["modification_time"] = str(datetime.now())        
        self.current_round['actions'].append(self.current_action)

        # Actualiza del juego
        self.current_game['rounds'][self.round_number] = self.current_round
        self.current_game['modification_time'] = str(datetime.now())
        
        # Actualización general
        self.games[self.game_name] = self.current_game  

        with open(saved_games_path, 'w') as file:
            json.dump(self.games, file, indent=4)
  
    def closeEvent(self, event):
        # Confirmar salida
        reply = QMessageBox.question(self, 'Salir', '¿Estás seguro de que quieres salir?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()