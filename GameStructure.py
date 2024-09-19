from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QLabel, QTableWidget,
                            QPushButton, QGridLayout, QMessageBox, QTableWidgetItem,
                            QHBoxLayout, QComboBox, QMainWindow, QGroupBox, QScrollArea, QInputDialog, QAbstractItemView) 
from PyQt5.QtGui import QImage, QFont, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PIL import Image, ImageDraw, ImageFont
from bingo_winner_notification import BingoWinnerWindow
import json
import os

# Rellenar la tabla con los números
ranges = [(1, 15),  #B
          (16, 30), #I
          (31, 45), #N
          (46, 60), #G
          (61, 75)] #O

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

class StatisticsWindow(QMainWindow):
    def __init__(self, game_data, bingo_carts, parent=None):
        super().__init__(parent)
        self.game_data = game_data
        self.bingo_carts = bingo_carts
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Estadísticas del Juego')
        self.setGeometry(100, 100, 1000, 800)
        
        # Crear el widget central y el layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Mostrar la forma del Bingo que se jugó
        grid_image_label = QLabel(f"Forma del Bingo que se jugó: {self.game_data['rounds'][str(len(self.game_data['rounds']))]['grid_image']}")
        layout.addWidget(grid_image_label)

        # Mostrar la cantidad de rondas jugadas y la tabla de jugadas
        total_rounds = len(self.game_data['rounds'])
        rounds_label = QLabel(f"\nCantidad de rondas jugadas: {total_rounds}")
        layout.addWidget(rounds_label)

        rounds_table = QTableWidget()
        rounds_table.setRowCount(total_rounds)
        rounds_table.setColumnCount(2)
        rounds_table.setHorizontalHeaderLabels(['Ronda', 'Acciones'])
        
        for i, (round_num, round_data) in enumerate(self.game_data['rounds'].items()):
            actions = ', '.join(round_data['actions'])
            rounds_table.setItem(i, 0, QTableWidgetItem(f"Ronda {round_num}"))
            rounds_table.setItem(i, 1, QTableWidgetItem(actions))
        
        layout.addWidget(rounds_table)

        # Mostrar el estado final de todos los Bingos con el grid
        bingos_label = QLabel("\nEstado final de los Bingos:")
        layout.addWidget(bingos_label)

        scroll_area = QScrollArea()
        layout.addWidget(scroll_area)
        scroll_widget = QWidget()
        scrolright_layout = QVBoxLayout(scroll_widget)

        for bingo_name, data in self.bingo_carts.items():
            # Verificar y resaltar las acciones del Bingo
            grid_matrix = self.game_data['rounds'][str(total_rounds)]['grid_matrix']
            red_highlight, yellow_highlight = self.process_bingo_actions(bingo_name, data['numbers'], grid_matrix)

            # Mostrar el grid del Bingo
            grid_label = QLabel(f"{bingo_name} - Casillas restantes: {data['boxes_to_fill']}")
            scrolright_layout.addWidget(grid_label)

            bingo_pixmap = self.create_bingo_pixmap(bingo_name, data['numbers'], red_highlight, yellow_highlight)
            bingo_label = QLabel()
            bingo_label.setPixmap(bingo_pixmap)
            scrolright_layout.addWidget(bingo_label)
        
        scroll_area.setWidget(scroll_widget)
    
    def process_bingo_actions(self, bingo_name, bingo_numbers, grid_matrix):
        red_highlight, yellow_highlight = [], []

        for action in self.game_data['rounds'][str(len(self.game_data['rounds']))]['actions']:
            r_high, y_high = self.check_bingo_actions(bingo_name, bingo_numbers, grid_matrix, action)
            red_highlight.extend(r_high)
            yellow_highlight.extend(y_high)

        return red_highlight, yellow_highlight

    def check_bingo_actions(self, bingo_name, bingo_numbers, grid_matrix, action):       
        column_mapping = {'B': 0, 'I': 1, 'N': 2, 'G': 3, 'O': 4}

        red_highlight, yellow_highlight = []

        letter = action[0]  # Primera parte de la acción (B, I, N, G, O)
        number = int(action[1:])  # Parte numérica de la acción
        column_index = column_mapping[letter]

        for row_index in range(len(bingo_numbers)):
            if bingo_numbers[row_index][column_index] == number:
                if grid_matrix[row_index][column_index] == 1:
                    red_highlight.append(action)
                else:
                    yellow_highlight.append(action)
                break

        return red_highlight, yellow_highlight

    def create_bingo_pixmap(self, bingo_name, bingo_numbers, red_highlight, yellow_highlight):
        img = QImage(300, 360, QImage.Format_RGB32)
        img.fill(Qt.white)

        painter = QPainter(img)
        cell_size = 60
        font = QFont("Arial", 10)
        painter.setFont(font)

        headers = ['B', 'I', 'N', 'G', 'O']
        for i, header in enumerate(headers):
            x0 = i * cell_size
            y0 = 0
            painter.drawText(x0 + cell_size // 2 - 10, y0 + 30, header)

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
        
        return QPixmap.fromImage(img)
    
class GameProcess(QMainWindow):
    def __init__(self, game_name):
        super().__init__()
        self.game_name = game_name
        self.round_number = 0
        self.current_window = None

    def start_game(self):
        self.start_new_round()

    def ask_for_new_round(self):
        self.game_window.save_game_data()

        # Cerrar la ventana actual de manera adecuada según el tipo de ventana
        if isinstance(self.current_window, GameWindow):
            self.current_window.exit_without_confirmation()
        else: self.current_window.close()

        # Mostrar un cuadro de diálogo preguntando si desea iniciar una nueva ronda
        reply = QMessageBox.question(self, 'Nueva Ronda', '¿Desea iniciar una nueva ronda?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.start_new_round()
        else:
            self.close()

    def show_statistics(self):
        self.statistics_window = QWidget()
        self.statistics_window.setWindowTitle('Resumen del juego')
        self.statistics_window.showFullScreen()
        
        # Crear el widget central y el layout
        central_widget = QWidget()
        self.statistics_window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 1. Nombre de la app
        app_name = QLabel("BingoGO", self)
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setFont(QFont("Arial", 50))
        layout.addWidget(app_name)

        # 2. Resumen del juego
        header_label = QLabel(f'Resumen del juego: {self.game_name} \nRonda: {self.round_number}', self)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 20))
        layout.addWidget(header_label)

        # 3. Mostrar la forma del Bingo que se jugó
        instrucciones_image_label = QLabel("La forma del Bingo que se jugó es la siguiente:", self)
        instrucciones_image_label.setFont(QFont("Arial", 10))
        layout.addWidget(instrucciones_image_label)
        # Imagen de la figura a jugar
        image_label = QLabel(self)
        image_label.setPixmap(QPixmap(self.current_round['grid_image']))
        layout.addWidget(image_label)

        # 4. Mostrar los bingos jugados
        bingos_label = QLabel("\nEstado final de los Bingos:")
        layout.addWidget(bingos_label)
        bingos_table = QTableWidget()
        bingos_table.setRowCount(len(self.bingo_carts))
        bingos_table.setColumnCount(2)
        bingos_table.setHorizontalHeaderLabels(['Bingo', 'Estado'])
        for i, (bingo_name, bingo_data) in enumerate(self.bingo_carts.items()):
            boxes_to_fill = bingo_data['boxes_to_fill']
            status = "Completado" if boxes_to_fill == 0 else f"Incompleto, {boxes_to_fill} casillas faltantes"
            bingos_table.setItem(i, 0, QTableWidgetItem(bingo_name))
            bingos_table.setItem(i, 1, QTableWidgetItem(status))
        
        layout.addWidget(bingos_table)


        # 5. Mostrar la cantidad de rondas jugadas
        total_rounds = len(self.current_game['rounds'])
        rounds_label = QLabel(f"\nCantidad de rondas jugadas: {total_rounds}")
        rounds_label.setFont(QFont("Arial", 10))
        layout.addWidget(rounds_label)

        # 6. Mostrar el estado final de todos los Bingos
        


        # 7. Mostrar otra cosa
        rounds_table = QTableWidget()
        rounds_table.setRowCount(total_rounds)
        rounds_table.setColumnCount(2)
        rounds_table.setHorizontalHeaderLabels(['Ronda', 'Acciones'])
        
        for i, (round_num, round_data) in enumerate(self.game_data['rounds'].items()):
            actions = ', '.join(round_data['actions'])
            rounds_table.setItem(i, 0, QTableWidgetItem(f"Ronda {round_num}"))
            rounds_table.setItem(i, 1, QTableWidgetItem(actions))
        
        layout.addWidget(rounds_table)

    def start_new_round(self):
        self.round_number += 1

        # Crear y mostrar la ventana de la ronda
        self.round_window = RoundWindow(self.game_name, self.round_number)
        self.round_window.figure_make.connect(self.load_game_window)
        
        self.current_window = self.round_window
        self.round_window.show()

    def load_game_window(self):
        # Cerrar la ventana anterior de manera adecuada
        self.current_window.close()

        # Crear y mostrar la ventana del juego
        self.game_window = GameWindow(self.game_name)
        self.current_window = self.game_window

        #Cargar información valiosa
        self.current_game = self.current_window.current_game
        self.current_round = self.current_window.current_round
        self.bingo_carts = self.current_window.bingos_carts
        
        self.game_window.round_completed.connect(self.ask_for_new_round)
        self.game_window.round_win.connect(self.show_bingo_winner)
        self.game_window.show()

    def show_bingo_winner(self):
        id_bingo = self.current_window.round_win_details
        self.game_window.save_game_data()
        self.current_window.exit_without_confirmation()

        self.confetti_window = BingoWinnerWindow(id_bingo)
        self.current_window = self.confetti_window

        self.confetti_window.accept_command.connect(self.ask_for_new_round)
        self.confetti_window.statistics_command.connect(self.show_statistics)
        self.confetti_window.show()

#Completado
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
    round_win = pyqtSignal()
    def __init__(self, game_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle('BingoGo')
        self.showFullScreen()
        self.game_name = game_name

        self.load_round_data()
        self.load_bingos_data()

        # Crear un layout principal horizontal (dividir en dos columnas)
        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)

        # Crear layout de la derecha (información principal)
        self.left_layout = QVBoxLayout()
        self.main_layout.addLayout(self.left_layout)

        # Crear layout de la izquierda (estadísticas y bingos)
        self.right_layout = QVBoxLayout()
        self.main_layout.addLayout(self.right_layout)

        self.create_widgets()

    def load_round_data(self):
        # Leer los datos existentes del juego
        with open(saved_games_path, 'r') as file:
            self.games = json.load(file)

        #Data base
        self.show_exit_confirmation = True
        self.current_game = self.games[self.game_name]
        self.round_number = str(len(self.current_game['rounds']))   
        self.current_round = self.current_game['rounds'][self.round_number]
        self.round_start_time = datetime.now()
        self.round_win_details = None
        # Lista que guarda los números jugados
        self.played_numbers = []
        self.current_action = None

        #Casillas totales por llenar
        self.boxes_to_fill_total = 0
        for row in self.current_round['grid_matrix']:
            for number in row:
                if int(number) == 1: self.boxes_to_fill_total += 1

    def load_bingos_data(self):
        self.bingos_carts = {}

        # Leer los datos existentes de los bingos
        with open(saved_carts_path, 'r') as file:
            bingos = json.load(file)

        for key, values in bingos.items():
            if key in self.current_game["bingos"]:
                self.bingos_carts[key] = {'numbers': values["bingo_numbers"],
                                          'boxes_to_fill': self.boxes_to_fill_total}

    def create_widgets(self):
        # Widgets de la izquierda
        self.create_left_widgets()

        # Widgets de la derecha
        self.create_right_widgets()

    def create_left_widgets(self):
        # Nombre de la app
        app_name = QLabel("BingoGO", self)
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setFont(QFont("Arial", 50))
        self.left_layout.addWidget(app_name)

        # Nombre del juego
        header_label = QLabel(f'Juego: {self.game_name}', self)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 20))
        self.left_layout.addWidget(header_label)

        # Numero de la ronda
        header_label_number = QLabel(f'Ronda número: {self.round_number}', self)
        header_label_number.setAlignment(Qt.AlignCenter)
        header_label_number.setFont(QFont("Arial", 20))
        self.left_layout.addWidget(header_label_number)

        # Duración de la ronda
        self.duration_label = QLabel("Duración: 00:00:00", self)
        self.duration_label.setAlignment(Qt.AlignCenter)
        self.duration_label.setFont(QFont("Arial", 10))
        self.left_layout.addWidget(self.duration_label)
        
        # Temporizador para actualizar la duración de la ronda
        self.round_duration_timer = QTimer(self)
        self.round_duration_timer.timeout.connect(self.update_round_duration)
        self.round_duration_timer.start(1000)

        # Instrucciones de accionar
        self.instrucciones_acciones = QLabel("Escriba las letras y números que vayan dictando:", self)
        self.instrucciones_acciones.setAlignment(Qt.AlignCenter)
        self.instrucciones_acciones.setFont(QFont("Arial", 15))
        self.left_layout.addWidget(self.instrucciones_acciones)

        # Agregar acciones del juego
        self.actions_game()

        # Instrucciones de la figura de Bingo
        self.instrucciones_image_label = QLabel("La forma del Bingo que se jugará es la siguiente:", self)
        self.instrucciones_image_label.setAlignment(Qt.AlignCenter)
        self.instrucciones_image_label.setFont(QFont("Arial", 15))
        self.left_layout.addWidget(self.instrucciones_image_label)

        # Imagen de la figura a jugar
        image_label = QLabel(self)
        image_label.setPixmap(QPixmap(self.current_round['grid_image']))
        image_label.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(image_label)

        # Botones de guardar y salir
        self.save_buttons()

        # Botón para registrar un ganador externo
        self.external_winner_btn = QPushButton("Registrar Ganador Externo")
        self.external_winner_btn.clicked.connect(self.register_external_winner)
        self.left_layout.addWidget(self.external_winner_btn)

    def create_right_widgets(self):
        # Crear estadísticas del juego
        self.create_statistics_section()

        # Visualización de Bingos
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
        self.left_layout.addLayout(self.input_layout)

    def create_bingo_visualization(self):
        self.bingo_group_box = QGroupBox("Visualización de Bingos")
        self.bingo_layout = QGridLayout()  # Cambiamos a QGridLayout para organizarlos en filas y columnas.

        # Crear un widget de visualización por cada cartón de Bingo
        self.bingo_widgets = {}
        row, col = 0, 0  # Inicializar fila y columna

        for i, bingo_name in enumerate(self.bingos_carts.keys()):
            # Crear etiquetas para el nombre del bingo
            label = QLabel(f"Bingo: {bingo_name}")
            label.setFont(QFont("Arial", 15))

            # Crear visualización del bingo
            bingo_view = QLabel(self)
            bingo_view.setAlignment(Qt.AlignCenter)

            # Agregar a la cuadrícula
            self.bingo_layout.addWidget(label, row, col)
            self.bingo_layout.addWidget(bingo_view, row + 1, col)

            # Guardar las referencias a los widgets
            self.bingo_widgets[bingo_name] = bingo_view

            # Crear y agregar el contador de casillas restantes
            missing_cells_label = QLabel(self)
            missing_cells_label.setAlignment(Qt.AlignCenter)
            self.bingo_layout.addWidget(missing_cells_label, row + 2, col)
            self.bingo_widgets[bingo_name + "_missing"] = missing_cells_label

            # Avanzar la columna, y si llegamos a tres, saltamos a la siguiente fila
            col += 1
            if col == 3:  # Tres bingos por fila
                col = 0
                row += 3  # Saltamos a la siguiente fila (3 posiciones por fila: nombre, visualización, casillas restantes)

        self.bingo_group_box.setLayout(self.bingo_layout)
        self.right_layout.addWidget(self.bingo_group_box)

    def create_statistics_section(self):
        # Crear un grupo para la sección de estadísticas
        self.statistics_group_box = QGroupBox("Estadísticas del Juego")
        self.statistics_layout = QVBoxLayout()

        # Última jugada
        self.last_action_label = QLabel("Última acción: N/A")
        self.statistics_layout.addWidget(self.last_action_label)

        # Contador de jugadas realizadas
        self.actions_count_label = QLabel("Total de jugadas: 0")
        self.statistics_layout.addWidget(self.actions_count_label)

        # Crear la tabla de efectividad
        self.statistics_table = QTableWidget(1, 3)  # 1 fila y 3 columnas
        self.statistics_table.setHorizontalHeaderLabels(["Efectivo:", "Parcialmente efectivo:", "No fue efectivo:"])
        self.statistics_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Desactivar la edición
        self.statistics_table.setFixedHeight(150)  # Altura fija compacta
        # Ajustar el ancho de las columnas
        self.statistics_table.setColumnWidth(0, 400)
        self.statistics_table.setColumnWidth(1, 400)
        self.statistics_table.setColumnWidth(2, 400)
        # Agregar la tabla al layout
        self.statistics_layout.addWidget(self.statistics_table)

        #  Tabla de números jugados
        self.statistics_layout.addWidget(QLabel("Números jugados:"))
        self.setup_numbers_table()
        self.statistics_layout.addWidget(self.numbers_table)

        self.statistics_group_box.setLayout(self.statistics_layout)
        self.right_layout.addWidget(self.statistics_group_box)

    def save_buttons(self):
        # Botón "Jugar"
        self.play_button = QPushButton("Jugar", self)
        self.play_button.clicked.connect(self.check_bingo_card)
        self.left_layout.addWidget(self.play_button)

        # Botón "Salir"
        self.exit_button = QPushButton("Salir", self)
        self.exit_button.clicked.connect(self.close)
        self.left_layout.addWidget(self.exit_button)

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

        # Validar que el número esté en el rango permitido 
        dict_letter = {'B': 0, 'I': 1, 'N': 2, 'G': 3, 'O': 4}
        id_column = dict_letter[letter]
        rangos = ranges[id_column][0], ranges[id_column][1]

        if int(number_input) < rangos[0] or int(number_input) > rangos[1]:
            QMessageBox.critical(self, "Error", f"En la columna '{letter}' solo pueden haber números entre {rangos[0]} y {rangos[1]}")
            return False

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
        self.update_statistics()
        self.update_data()

    def process_bingo(self):
        self.red_current_action, self.yellow_current_action, self.na_current_action = [], [], []

        # Iterado por cada uno de los bingos
        for bingo_name, data in self.bingos_carts.items():
            bingo_numbers = data['numbers']

            red_highlight, yellow_highlight = [], []
            # Iterado por cada una de las acciones
            for action in self.current_round['actions']:
                red_current_action, yellow_current_action = self.check_bingo_actions(bingo_name, bingo_numbers, 
                                                                        self.current_round["grid_matrix"], 
                                                                        action)
        
                # Listas para guardar el historial de cambios de la acción actual
                if action == self.current_action:
                    self.update_action_status(bingo_name, red_current_action, yellow_current_action)
                
                red_highlight.extend(red_current_action)
                yellow_highlight.extend(yellow_current_action)

            # Actualizar la visualización del cartón de Bingo
            self.update_bingo_visualization(bingo_name, bingo_numbers, red_highlight, yellow_highlight)

    def check_bingo_actions(self, bingo_name, bingo_numbers, grid_matrix, action):       
        # Diccionario para asociar las letras con los índices de las columnas
        column_mapping = {'B': 0, 'I': 1, 'N': 2, 'G': 3, 'O': 4}

        # Listas para guardar las acciones resaltadas
        red_highlight = []
        yellow_highlight = []

        letter = action[0]  # Primera parte de la acción (B, I, N, G, O)
        number = int(action[1:])  # Parte numérica de la acción

        # Determinar el índice de la columna con base en la letra
        column_index = column_mapping[letter]

        # Buscar el número en la columna correspondiente
        for row_index in range(len(bingo_numbers)):
            if bingo_numbers[row_index][column_index] == number:
                #Casillas de efectividad completa
                if grid_matrix[row_index][column_index] == 1:
                    red_highlight.append(action)
                    self.bingos_carts[bingo_name]['boxes_to_fill'] -= 1

                #Casillas de efectividad parcial
                else:
                    yellow_highlight.append(action)
                    
                remaining_cells = self.bingos_carts[bingo_name]['boxes_to_fill']
                self.bingo_widgets[bingo_name + "_missing"].setText(f"Casillas restantes para completar el Bingo: {remaining_cells}")
                break  # Salir del bucle una vez se ha encontrado la acción

        return red_highlight, yellow_highlight

    def setup_numbers_table(self):
        # Configuración de la tabla
        self.numbers_table = QTableWidget(5, 15)  # 5 filas (BINGO) y 16 columnas
        self.numbers_table.setHorizontalHeaderLabels([str(i) for i in range(1, 16)])
        self.numbers_table.setVerticalHeaderLabels(['B', 'I', 'N', 'G', 'O'])
        self.numbers_table.setFixedSize(1208, 290)  # Ajusta el tamaño total de la tabla
        self.numbers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Configura el tamaño de cada celda para que encaje en el tamaño de la tabla
        for i in range(5):
            for j in range(15):
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignCenter)
                item.setFont(QFont("Arial", 8))  # Tamaño de fuente reducido
                self.numbers_table.setItem(i, j, item)
                self.numbers_table.setColumnWidth(j, 25)  # Ajusta el ancho de las columnas
            self.numbers_table.setRowHeight(i, 20)  # Ajusta la altura de las filas
        
        # Inserta los números en la tabla
        for i, (start, end) in enumerate(ranges):
            for j in range(start, end+1):
                self.numbers_table.item(i, j - start).setText(str(j))
                         
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

    def update_action_status(self, bingo_name, red_action, yellow_action):
        if red_action: self.red_current_action.append(bingo_name)
        elif yellow_action: self.yellow_current_action.append(bingo_name)
        else: self.na_current_action.append(bingo_name)

    def update_statistics(self):
        # Actualizar la última acción jugada
        self.last_action_label.setText(f"Última jugada: {self.current_action}")
        
        # Actualizar la cantidad total de jugadas realizadas
        self.actions_count_label.setText(f"\nTotal de jugadas: {len(self.current_round['actions'])}")
        
        # Evaluar el estado de la acción anterior
        if self.red_current_action:
            bingo_names_red = ", ".join(self.red_current_action)
        else: bingo_names_red = "N/A"
            
        if self.yellow_current_action:
            bingo_names_yellow = ", ".join(self.yellow_current_action)
        else: bingo_names_yellow = "N/A"
            
        if self.na_current_action:
            bingo_names_na = ", ".join(self.na_current_action)
        else: bingo_names_na = "N/A"
        
        # Insertar datos en la tabla
        self.statistics_table.setItem(0, 0, QTableWidgetItem(bingo_names_red))
        self.statistics_table.setItem(0, 1, QTableWidgetItem(bingo_names_yellow))
        self.statistics_table.setItem(0, 2, QTableWidgetItem(bingo_names_na))

    def update_numbers_table(self):        
        for i, (start, end) in enumerate(ranges):
            for j in range(start, end):
                item = self.numbers_table.item(i, j - start)
                if j in self.played_numbers:
                    item.setBackground(QColor('yellow'))  # Resaltar en amarillo
                else:
                    item.setBackground(QColor('white'))  # Fondo blanco si no está jugado

    def update_data(self):
        print(f">>> Jugada: {self.current_action}")

        # Añadir nuevo número jugado y actualizar la tabla
        new_number = int(self.current_action[1:])
        if new_number not in self.played_numbers:
            self.played_numbers.append(new_number)
            self.update_numbers_table()

        # Actualizar información de bingos
        for key in self.bingos_carts.keys():
            if self.bingos_carts[key]['boxes_to_fill'] == 0:
                self.current_game['rounds'][self.round_number]['Ganador'] = "User"
                self.round_win_details = key
                self.round_win.emit()  # Emitir la señal cuando se gana la ronda
                
            self.bingos_carts[key]['boxes_to_fill'] = self.boxes_to_fill_total

    def register_external_winner(self):
        # Abrir un cuadro de diálogo para ingresar el nombre del ganador
        winner_name, ok = QInputDialog.getText(self, 'Ganador Externo', 'Alguien externo ha ganado. \nIngrese el nombre del ganador:')
        
        if ok and winner_name:
            # Guardar o procesar el nombre del ganador según sea necesario
            print(f">>> El ganador de la ronda: {winner_name}")
            self.current_game['rounds'][self.round_number]['Ganador'] = winner_name
            self.round_completed.emit()

    def save_game_data(self):
        #Actualizar ronda 
        self.current_round["modification_time"] = str(datetime.now())  

        #Actualizar la acción
        if self.current_action:
            if self.current_action not in self.current_round['actions']:      
                self.current_round['actions'].append(self.current_action)

        # Actualiza del juego
        self.current_game['rounds'][self.round_number] = self.current_round
        self.current_game['modification_time'] = str(datetime.now())

        # Actualización general
        self.games[self.game_name] = self.current_game  

        with open(saved_games_path, 'w') as file:
            json.dump(self.games, file, indent=4)

    def closeEvent(self, event):
        if self.show_exit_confirmation:
            # Confirmar salida
            reply = QMessageBox.question(self, 'Salir', '¿Estás seguro de que quieres salir?', 
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()  # Salir directamente sin preguntar

    def exit_without_confirmation(self):
        """Función para salir sin mostrar la confirmación de QMessageBox."""
        self.show_exit_confirmation = False
        self.close()




