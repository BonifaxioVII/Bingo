import os
import json
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QGridLayout, QMessageBox, QHBoxLayout, QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Configuración inicial 
saved_carts_path = os.path.join('Data', "Bingos.txt")
if not os.path.exists('Data'):
    os.makedirs('Data')
if not os.path.exists(saved_carts_path):
    with open(saved_carts_path, 'w') as file:
        json.dump({}, file)


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

        if self.new_card_id:
            self.load_bingo_card(self.new_card_id)
    
    def create_widgets(self):
        # Etiqueta de bienvenida y entrada para el número del cartón de bingo
        bienvenida = QLabel("Crear BINGO\nInserte el código del cartón de bingo:", self)
        bienvenida.setAlignment(Qt.AlignCenter)
        bienvenida.setFont(QFont("Arial", 12))
        self.layout.addWidget(bienvenida)
        
        self.id_card_space = QLineEdit(self)
        self.id_card_space.setFixedWidth(250)
        self.id_card_space.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.id_card_space)
        
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
        headers = ['B', 'I', 'N', 'G', 'O']
        for col, header in enumerate(headers):
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
                    cell = QLabel("BINGO", self)
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


        # Guardar en archivo
        self.save_to_file(self.card_id, self.bingo_numbers, self.creation_time, self.modification_time)

        # Aquí puedes procesar los números y el número del cartón como necesites
        print("Código del Cartón:", self.card_id)
        print("Números del Cartón:", self.bingo_numbers)
        print("Hora de creación:", self.creation_time)
        print("Ultima modificación:", self.modification_time)
        
        QMessageBox.information(self, "Guardado", f"El cartón {self.card_id} ha sido guardado exitosamente.")

        # Cerrar ventana de creación de bingo
        self.close()

    def checkID(self) -> bool:
        #Conocer si hay ID pre-establecido
        if self.new_card_id:
            self.id_card_space.setText(self.new_card_id) 
            self.id_card_space.setDisabled(True)
            self.card_id = self.new_card_id
            return True

        else: 
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

    def save_to_file(self, card_number, bingo_number, creation_time, modification_time):       
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
            "modification_time": modification_time}
        
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
