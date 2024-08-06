import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QMainWindow,
                            QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QListWidget, QGridLayout, QMessageBox, 
                            QHBoxLayout, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
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
        save_button.clicked.connect(self.save_numbers)
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
    
    def save_numbers(self):
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

        # Leer los datos existentes para verificar duplicados ID
        file_path = saved_carts_path
        bingos = {}
        with open(file_path, 'r') as file:
            try:
                bingos = json.load(file)
            except json.JSONDecodeError:
                pass
        
        if self.card_id in bingos:
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
                    row_numbers.append("BINGO")
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
                if number == "BINGO":
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
            try:
                bingos = json.load(file)
            except json.JSONDecodeError:
                pass
        
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
        file_path = saved_carts_path
        if not os.path.exists(file_path):
            return
        
        with open(file_path, 'r') as file:
            try:
                bingos = json.load(file)
                if card_id in bingos:
                    bingo_data = bingos[card_id]["bingo_numbers"]
                    
                    #Establecer hora de creación
                    self.creation_time = bingos[card_id]["creation_time"]
                    
                    #Establecer celdas del bingo
                    for i, row in enumerate(bingo_data):
                        for j, value in enumerate(row):
                            if value != "BINGO" and self.cells[i][j] is not None:
                                self.cells[i][j].setText(str(value))
            except json.JSONDecodeError:
                QMessageBox.critical(self, "Error", "No se pudo cargar el cartón de bingo.")



if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = BingoCard()
    window.show()
    sys.exit(app.exec_())
