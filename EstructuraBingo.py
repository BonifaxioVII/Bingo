import os
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class BingoCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configurar la ventana secundaria
        self.setWindowTitle('Digitalización del Cartón de Bingo')
        
        # Layout principal
        self.layout = QVBoxLayout()
        
        # Crear widgets y el grid de entrada
        self.create_widgets()
        self.create_grid()
        
        # Establecer el layout
        self.setLayout(self.layout)
        
    def create_widgets(self):
        # Etiqueta de bienvenida y entrada para el número del cartón de bingo
        bienvenida = QLabel("Crear BINGO\nInserte el código del cartón de bingo:", self)
        bienvenida.setAlignment(Qt.AlignCenter)
        bienvenida.setFont(QFont("Arial", 12))
        
        self.id_card_space = QLineEdit(self)
        self.id_card_space.setFixedWidth(250)
        self.id_card_space.setAlignment(Qt.AlignCenter)
        
        # Texto explicativo
        instructions = QLabel("\nRellene la plantilla de a continuación de acuerdo con su cartón físico.", self)
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setFont(QFont("Arial", 12))
        
        self.layout.addWidget(bienvenida)
        self.layout.addWidget(self.id_card_space)
        self.layout.addWidget(instructions)

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
        
        self.cells = {}
        for i in range(5):
            for j in range(5):
                if i == 2 and j == 2:
                    # Espacio libre en el centro del cartón de bingo
                    cell = QLabel("BINGO", self)
                    cell.setAlignment(Qt.AlignCenter)
                    cell.setFixedSize(40, 40)
                    cell.setStyleSheet("background-color: lightgrey;")
                    grid_layout.addWidget(cell, i + 1, j)
                    self.cells[(i, j)] = cell
                else:
                    # Espacios para que el usuario ingrese los números
                    cell = QLineEdit(self)
                    cell.setFixedSize(40, 40)
                    cell.setAlignment(Qt.AlignCenter)
                    grid_layout.addWidget(cell, i + 1, j)
                    self.cells[(i, j)] = cell
        
        self.layout.addWidget(grid_frame)
        
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
    
    def save_numbers(self):
        self.id_card = self.id_card_space.text()
        if not self.id_card:
            QMessageBox.critical(self, "Error", "Por favor, ingrese el código del cartón de bingo.")
            return
        
        self.bingo_numbers = {}
        numbers_set = set()
        for key, cell in self.cells.items():
            if isinstance(cell, QLineEdit):
                value = cell.text()
                if not value.isdigit():
                    QMessageBox.critical(self, "Error", "Todas las casillas deben estar llenas con números.")
                    return
                if int(value) in numbers_set:
                    QMessageBox.critical(self, "Error", "No se pueden repetir números en diferentes casillas.")
                    return
                self.bingo_numbers[str(key)] = int(value)
                numbers_set.add(int(value))
        
        # Guardar en archivo
        self.save_to_file(self.id_card, self.bingo_numbers)

        # Aquí puedes procesar los números y el número del cartón como necesites
        print(f"Código del Cartón: {self.id_card}")
        print("Números del Cartón:", self.bingo_numbers)
        QMessageBox.information(self, "Guardado", f"El cartón {self.id_card} ha sido guardado exitosamente.")

        # Cerrar ventana de creación de bingo
        self.close()

    def save_to_file(self, card_number, bingo_numbers):
        # Asegurar que la carpeta Data existe
        if not os.path.exists('Data'):
            os.makedirs('Data')
        
        file_path = os.path.join('Data', 'Bingos.txt')
        bingos = {}
        
        # Leer datos existentes si el archivo ya existe
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                try:
                    bingos = json.load(file)
                except json.JSONDecodeError:
                    pass
        
        # Añadir el nuevo bingo
        bingos[card_number] = bingo_numbers
        
        # Escribir los datos actualizados de nuevo al archivo
        with open(file_path, 'w') as file:
            json.dump(bingos, file, indent=4)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = BingoCard()
    window.show()
    sys.exit(app.exec_())
