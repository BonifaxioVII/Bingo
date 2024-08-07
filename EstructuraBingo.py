import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QApplication, QFrame, QScrollArea,
                            QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QListWidget, QGridLayout, QMessageBox, 
                            QHBoxLayout, QAbstractItemView, QListWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QColor
from PIL import Image, ImageDraw, ImageFont

# Configuración inicial Bingos
def conf_carts():
    # Ruta de los BingosInfo
    saved_carts_path = os.path.join('Data', "Bingos.txt")
    # Crear carpeta data si no existe
    if not os.path.exists('Data'):
        os.makedirs('Data')
    # Crear txt Bingos si no existe
    if not os.path.exists(saved_carts_path):
        with open(saved_carts_path, 'w') as file:
            json.dump({}, file)
    # Asegurar que la carpeta ImgCard existe
    img_cart_dir = os.path.join('Data', 'ImgCard')
    if not os.path.exists(img_cart_dir):
        os.makedirs(img_cart_dir)

    return saved_carts_path, img_cart_dir
saved_carts_path, img_cart_dir = conf_carts()

# Interfaz del cartón de Bingo
class BingoCard(QWidget):
    def __init__(self, parent=None, card_id=None):
        super().__init__(parent)
        self.new_card_id = card_id
        self.bingo_numbers = []
        
        # Leer los datos existentes de bingos
        with open(saved_carts_path, 'r') as file:
            self.bingos = json.load(file)

        # Configurar la ventana secundaria
        self.setWindowTitle('Digitalización del Cartón de Bingo')
        
        # Layout principal
        self.layout = QVBoxLayout()
        
        # Crear widgets y el grid de entrada
        self.create_widgets()
        
        # Establecer el layout
        self.setLayout(self.layout)

        # Cargar información del cartón si este tiene historial
        if self.new_card_id:
            self.load_bingo_card(self.new_card_id)
    
    def create_widgets(self):
        # Etiqueta de bienvenida y entrada para el número del cartón de bingo de acuerdo con el historial del cartón
        if not self.new_card_id:
            bienvenida = QLabel("Crear BINGO\nInserte el código del cartón de bingo:", self)
        else:
            bienvenida = QLabel("Editar BINGO\nCodigo del cartón:", self)
        bienvenida.setAlignment(Qt.AlignCenter)
        bienvenida.setFont(QFont("Arial", 12))
        self.layout.addWidget(bienvenida)
        
        #Espacil con el ID del bingo
        self.id_card_space = QLineEdit(self)
        self.id_card_space.setFixedWidth(250)
        self.id_card_space.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.id_card_space)
        
        #Establecer ID del bingo
        if self.new_card_id:
            self.id_card_space.setText(self.new_card_id) 
            self.id_card_space.setDisabled(True)
            self.card_id = self.new_card_id

        # Texto explicativo
        instructions = QLabel("\nRellene la plantilla de a continuación de acuerdo con su cartón físico.", self)
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setFont(QFont("Arial", 12))
        self.layout.addWidget(instructions)

        #Crear grid
        self.create_grid()

        # Botones para guardar y cancelar
        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)
        
        save_button = QPushButton("Guardar", self)
        save_button.clicked.connect(self.save_data)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancelar", self)
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)
        
        self.layout.addWidget(button_frame)

    def create_grid(self):
        grid_frame = QWidget()
        grid_layout = QGridLayout(grid_frame)
        
        # Encabezados BINGO
        self.headers = ['B', 'I', 'N', 'G', 'O']
        for col, header in enumerate(self.headers):
            label = QLabel(header, self)
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont("Arial", 14))
            grid_layout.addWidget(label, 0, col)
        
        # Guardar numeros en matriz cells
        self.cells = []
        for i in range(5):
            row = []
            for j in range(5):
                if i == 2 and j == 2:
                    # Espacio libre en el centro del cartón de bingo
                    cell = QLabel("GO", self)
                    cell.setAlignment(Qt.AlignCenter)
                    cell.setFixedSize(40, 40)
                    cell.setStyleSheet("background-color: lightgrey;")
                    grid_layout.addWidget(cell, i + 1, j)
                    row.append(None)
                    continue
                    
                # Espacios para que el usuario ingrese los números
                cell = QLineEdit(self)
                cell.setFixedSize(40, 40)
                cell.setAlignment(Qt.AlignCenter)
                grid_layout.addWidget(cell, i + 1, j)
                row.append(cell)
            self.cells.append(row)
        
        self.layout.addWidget(grid_frame)
    
    def save_data(self):
        #Verificar el ID del tarjeton
        if self.checkID() == False: return

        #Verificar estado del grid
        if self.checkGrid() == False: return
        
        # Añadir fecha y hora de creación
        hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.new_card_id:
            self.creation_time 
            self.modification_time = hora_actual
        else:
            self.creation_time = hora_actual
            self.modification_time = None

        # Crear imagen del bingo
        self.save_as_image(self.card_id, self.bingo_numbers)

        # Guardar en archivo
        self.save_to_file(self.card_id, self.bingo_numbers, self.creation_time, self.modification_time, self.img_save_path)

        # Aquí puedes procesar los números y el número del cartón como necesites
        print("Código del Cartón:", self.card_id)
        print("Números del Cartón:", self.bingo_numbers)
        print("Hora de creación:", self.creation_time)
        print("Ultima modificación:", self.modification_time)
        print("Ruta de imagen:", self.img_save_path)
        
        QMessageBox.information(self, "Guardado", f"El cartón {self.card_id} ha sido guardado exitosamente.")

        # Cerrar ventana de creación de bingo
        self.close()

    def checkID(self) -> bool:
        if self.new_card_id: return True

        #Verificar la existencia del ID
        self.card_id = self.id_card_space.text()

        #Verificar la existencia del ID
        if not self.card_id:
            QMessageBox.critical(self, "Error", "Por favor, ingrese el código del cartón de bingo.")
            return False
        
        if self.card_id in self.bingos:
            QMessageBox.critical(self, "Error", f"El ID del cartón {self.card_id} ya ha sido usado.")
            return False
        
        return True

    def checkGrid(self) -> bool:
        #Verificar estado del grid
        self.bingo_numbers = []
        numbers_set = set()
        for row in self.cells:
            row_numbers = []
            for cell in row:
                if cell is None:
                    row_numbers.append("GO")
                    continue

                value = cell.text()
                if not value.isdigit():
                    QMessageBox.critical(self, "Error", "Todas las casillas deben estar llenas con números válidos.")
                    return False
                if int(value) > 80:
                    QMessageBox.critical(self, "Error", "Los números deben ser menores o iguales a 80.")
                    return False
                if int(value) in numbers_set:
                    QMessageBox.critical(self, "Error", "No se pueden repetir números en diferentes casillas.")
                    return False
                
                row_numbers.append(int(value))
                numbers_set.add(int(value))
            self.bingo_numbers.append(row_numbers)

        return True

    def save_as_image(self, card_number, bingo_number):
        # Definir dimensiones y colores
        cell_size = 60
        header_size = 70
        img_width = cell_size * 5
        img_height = header_size + cell_size * 5
        background_color = (255, 255, 255)
        line_color = (0, 0, 0)
        font_color = (0, 0, 0)
        free_space_color = (200, 200, 200)

        # Crear una nueva imagen
        img = Image.new('RGB', (img_width, img_height), background_color)
        draw = ImageDraw.Draw(img)
        
        # Cargar una fuente
        font = ImageFont.truetype("arial.ttf", 32)

        # Dibujar encabezados BINGO
        for col, header in enumerate(self.headers):
            draw.text((col * cell_size + cell_size / 2 - 10, 15), header, fill=font_color, font=font)

        # Dibujar líneas de la cuadrícula
        for i in range(6):
            # Líneas horizontales
            draw.line([(0, header_size + i * cell_size), (img_width, header_size + i * cell_size)], fill=line_color)
            # Líneas verticales
            draw.line([(i * cell_size, header_size), (i * cell_size, img_height)], fill=line_color)

        # Dibujar números en la cuadrícula
        for i, row in enumerate(bingo_number):
            for j, number in enumerate(row):
                if number == "GO":
                    draw.rectangle([(j * cell_size, header_size + i * cell_size), 
                                    ((j + 1) * cell_size, header_size + (i + 1) * cell_size)], 
                                    fill=free_space_color)
                    draw.text((j * cell_size + cell_size / 2 - 20, header_size + i * cell_size + cell_size / 4), 
                              "GO", fill=font_color, font=font)
                else:
                    draw.text((j * cell_size + cell_size / 2 - 10, header_size + i * cell_size + cell_size / 4), 
                              str(number), fill=font_color, font=font)

        # Guardar la imagen
        self.img_save_path = os.path.join(img_cart_dir, f'{card_number}.png')
        img.save(self.img_save_path)

    def save_to_file(self, card_number, bingo_number, creation_time, modification_time, img_path):       
        file_path = saved_carts_path
        bingos = {}
        
        # Leer datos existentes 
        with open(file_path, 'r') as file:
            bingos = json.load(file)
        
        # Añadir el nuevo bingo
        bingos[card_number] = {
            "bingo_numbers": bingo_number,
            "creation_time": creation_time,
            "modification_time": modification_time,
            "img_path": img_path}
        
        # Escribir los datos actualizados de nuevo al archivo
        with open(file_path, 'w') as file:
            json.dump(bingos, file, indent=4)

    def load_bingo_card(self, card_id):       
        if card_id in self.bingos:
            bingo_data = self.bingos[card_id]["bingo_numbers"]
            
            #Establecer hora de creación
            self.creation_time = self.bingos[card_id]["creation_time"]
            
            #Establecer celdas del bingo
            for i, row in enumerate(bingo_data):
                for j, value in enumerate(row):
                    if self.cells[i][j] is None:  # Ignorar el espacio libre en el centro
                        continue
                    self.cells[i][j].setText(str(value))

# Ventana de edición de contenido guardado
class EditViewWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Editar/Ver Juego')
        self.setGeometry(100, 100, 500, 350)
        
        # Layout principal
        self.layout = QVBoxLayout()
        
        # Opciones de edición/visualización
        self.create_options()
        
        self.setLayout(self.layout)

    def create_options(self):
        # Introducción
        intro_label = QLabel("Bienvenido a la sección de edición y visualización \nElija la opción que desea realizar:", self)
        intro_label.setAlignment(Qt.AlignCenter)
        intro_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(intro_label)

        # Opción para editar/ver juego
        game_button = QPushButton("Editar/Ver Juego", self)
        game_button.clicked.connect(self.edit_view_game)
        self.layout.addWidget(game_button)

        # Opción para editar/ver bingo
        bingo_button = QPushButton("Editar/Ver Bingo", self)
        bingo_button.clicked.connect(self.edit_view_bingo)
        self.layout.addWidget(bingo_button)

        # Opción para salir
        exit_button = QPushButton("Salir", self)
        exit_button.clicked.connect(self.close)
        self.layout.addWidget(exit_button)

    def edit_view_game(self):
        QMessageBox.information(self, "Editar/Ver Juego", "Funcionalidad de edición y visualización de juegos aún no implementada.")

    def edit_view_bingo(self):
        # Leer bingos desde el archivo
        with open(saved_carts_path, 'r') as file:
            self.bingos = json.load(file)
            
        # Comprobar que existan bingos para mostrar
        if not self.bingos:
            QMessageBox.information(self, "Sin Bingos", "No hay bingos para mostrar.")
            return

        # Crear ventana para mostrar los bingos
        self.bingo_window = QWidget()
        self.bingo_window.setWindowTitle('Editar/Ver Bingo')
        self.bingo_window.setGeometry(150, 150, 1500, 750)

        # Layout principal para la ventana de bingos
        bingo_layout = QVBoxLayout()

        # Mensaje al usuario
        info_label = QLabel("Haga click sobre el cartón que desea editar", self.bingo_window)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setFont(QFont("Arial", 14))
        bingo_layout.addWidget(info_label)

        # Establecer ScrollBar
        scroll_area = QScrollArea(self.bingo_window)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.list_bingos(scroll_layout)

        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        bingo_layout.addWidget(scroll_area)

        # Botón para regresar a la ventana principal
        back_button = QPushButton("Regresar a editar/ver", self.bingo_window)
        back_button.clicked.connect(self.bingo_window.close)
        bingo_layout.addWidget(back_button)


        self.bingo_window.setLayout(bingo_layout)
        self.bingo_window.show()

    def list_bingos(self, layout):        
        for card_id, data in self.bingos.items():
            bingo_frame = QFrame(self.bingo_window)
            bingo_layout = QHBoxLayout(bingo_frame)

            # Mostrar ID, fecha de creación y última modificación
            info = f"ID: {card_id}\nCreación: {data['creation_time']}\nÚltima Modificación: {data['modification_time']}"
            info_label = QLabel(info, self.bingo_window)
            info_label.setFont(QFont("Arial", 12))
            bingo_layout.addWidget(info_label)

            # Mostrar imagen del cartón de bingo
            img_path = data["img_path"]
            img_label = QLabel(self.bingo_window)
            pixmap = QPixmap(img_path)
            img_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            bingo_layout.addWidget(img_label)

            # Botón para editar el cartón
            edit_button = QPushButton("Editar", self.bingo_window)
            edit_button.clicked.connect(lambda _, card_id=card_id: self.edit_bingo_card(card_id))
            bingo_layout.addWidget(edit_button)

            # Botón para eliminar el cartón
            delete_button = QPushButton("Eliminar", self.bingo_window)
            delete_button.clicked.connect(lambda _, card_id=card_id: self.delete_bingo_card(card_id))
            bingo_layout.addWidget(delete_button)

            layout.addWidget(bingo_frame)

    def edit_bingo_card(self, card_id):
        # Cerrar la ventana de ver/editar bingo
        self.bingo_window.close()
        
        self.bingo_card_window = BingoCard(card_id=card_id)
        self.bingo_card_window.show()

    def delete_bingo_card(self, card_id):
        # Confirmación de eliminación
        reply = QMessageBox.question(self, 'Eliminar Bingo', f"¿Está seguro de que desea eliminar el cartón de bingo con ID {card_id}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.No: return

        # Leer y eliminar el cartón de bingo del archivo
        file_path = saved_carts_path

        if card_id in self.bingos:
            # Eliminar la imagen asociada
            img_path = self.bingos[card_id]["img_path"]
            if img_path and os.path.exists(img_path):
                os.remove(img_path)

            # Eliminar el cartón del diccionario
            del self.bingos[card_id]

            # Guardar los cambios
            with open(file_path, 'w') as file:
                json.dump(self.bingos, file, indent=4)
            
            QMessageBox.information(self, "Eliminar Bingo", f"El cartón de bingo con ID {card_id} ha sido eliminado.")
            
            # Actualizar la lista de bingos
            # Refrescar la lista de bingos
            self.bingo_window.close()
            self.edit_view_bingo()

# Ventana de creación de nuevo juego
class NewGameWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Nuevo Juego')
        self.setGeometry(100, 100, 900, 700)
        
        # Layout principal
        self.layout = QVBoxLayout()
        
        # Leer los datos existentes de bingos
        with open(saved_carts_path, 'r') as file:
            self.bingos = json.load(file)

        # Crear widgets
        self.create_widgets()

        # Establecer el layout
        self.setLayout(self.layout)

    def create_widgets(self):
        # Introducción
        intro_label = QLabel("Bienvenido a la sección de creación de un nuevo juego", self)
        intro_label.setAlignment(Qt.AlignCenter)
        intro_label.setFont(QFont("Arial", 14))
        self.layout.addWidget(intro_label)
        
        # Pedir nombre del juego
        game_name_label = QLabel("Ingrese el nombre del juego:", self)
        game_name_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(game_name_label)
        
        self.game_name_input = QLineEdit(self)
        self.layout.addWidget(self.game_name_input)
        
        # Pedir selección de cartones de bingo
        bingo_selection_label = QLabel("Seleccione los cartones de bingo que se jugarán:", self)
        bingo_selection_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(bingo_selection_label)
        
        # Lista de cartones de bingo
        self.bingo_list_widget = QListWidget(self)
        self.bingo_list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.load_bingo_list()
        self.layout.addWidget(self.bingo_list_widget)
        
        # Botones de acción
        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)
        
        play_button = QPushButton("Jugar", self)
        play_button.clicked.connect(self.play_game)
        button_layout.addWidget(play_button)
        
        cancel_button = QPushButton("Cancelar", self)
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)
        
        self.layout.addWidget(button_frame)

    def load_bingo_list(self):     
        # Posibles cartones de bingo para jugar           
        for card_id, data in self.bingos.items():
            item_text = f"ID: {card_id} | Creación: {data['creation_time']} | Última Modificación: {data.get('last_modified', 'N/A')}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, card_id)
            self.bingo_list_widget.addItem(item)
    
        # Opción de agregar nuevo bingo
        add_bingo_item = QListWidgetItem("Agregar nuevo Bingo")
        add_bingo_item.setForeground(QColor("blue"))
        add_bingo_item.setData(Qt.UserRole, "add_new")
        self.bingo_list_widget.addItem(add_bingo_item)
        self.bingo_list_widget.itemClicked.connect(self.add_new_bingo)

    def add_new_bingo(self, item):
        if item.data(Qt.UserRole) == "add_new":
            self.new_bingo_window = BingoCard()
            self.new_bingo_window.show()
            self.close()
            self.new_bingo_window.closeEvent = self.refresh_window
            
    def play_game(self):
        # Obtener nombre del juego
        game_name = self.game_name_input.text()
        if not game_name:
            QMessageBox.critical(self, "Error", "Por favor, ingrese el nombre del juego.")
            return
        
        # Obtener los bingos seleccionados
        selected_items = self.bingo_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.critical(self, "Error", "Por favor, seleccione al menos un cartón de bingo.")
            return
        
        selected_bingos = [item.data(Qt.UserRole) for item in selected_items]
        
        # Aquí se procesarán los bingos seleccionados para el juego
        print("Nombre del Juego:", game_name)
        print("Cartones de Bingo Seleccionados:", selected_bingos)
        
        # Aquí implementarás la funcionalidad del juego en el futuro
        self.close()

    def refresh_window(self, event):
        self.__init__()
        self.show()