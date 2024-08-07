import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from EstructuraBingo import BingoCard, EditViewWindow, NewGameWindow

class MainWindow(QWidget): 
    def __init__(self):
        super().__init__()
        
        # Inicializar la interfaz de usuario
        self.initUI()
    
    def initUI(self):
        # Configurar el título de la ventana
        self.setWindowTitle('BingoGO')
        self.setGeometry(100, 100, 400, 300)
        
        # Crear el layout principal
        layout = QVBoxLayout()
        
        # Crear y configurar el mensaje de bienvenida
        bienvenida = QLabel("Bienvenido a una herramienta de ayuda para jugar BINGO", self)
        bienvenida.setAlignment(Qt.AlignCenter)
        bienvenida.setFont(QFont("Arial", 14))
        
        # Crear y configurar el mensaje de opciones
        opciones = QLabel("Elige una de las siguientes opciones:", self)
        opciones.setAlignment(Qt.AlignCenter)
        opciones.setFont(QFont("Arial", 12))
        
        # Botón para Continuar Juego
        btn_continuar_juego = QPushButton("Continuar Juego", self)
        btn_continuar_juego.clicked.connect(self.continuar_juego)

        # Botón para agregar un nuevo cartón de bingo
        btn_nuevo_carton = QPushButton("Agregar cartón de Bingo", self)
        btn_nuevo_carton.clicked.connect(self.nuevo_carton_bingo)
        
        # Botón para Crear Juego
        btn_crear_juego = QPushButton("Nuevo Juego", self)
        btn_crear_juego.clicked.connect(self.nuevo_juego)
        
        # Botón para Editar/Ver Juegos
        btn_editar_ver_juegos = QPushButton("Editar/Ver Juegos", self)
        btn_editar_ver_juegos.clicked.connect(self.editar_ver_juegos)
        
        # Botón para salir
        btn_salir = QPushButton("Salir", self)
        btn_salir.clicked.connect(self.salir)
        
        # Configurar el layout principa
        layout.addWidget(bienvenida)
        layout.addWidget(opciones)
        layout.addWidget(btn_continuar_juego)
        layout.addWidget(btn_nuevo_carton)
        layout.addWidget(btn_crear_juego)
        layout.addWidget(btn_editar_ver_juegos)
        layout.addWidget(btn_salir)
        self.setLayout(layout)
    
    # Función para manejar el evento de "Continuar Juego"
    def continuar_juego(self):
        QMessageBox.information(self, "Continuar Juego", "Has seleccionado 'Continuar Juego'.")
    
    # Función para manejar el evento de "Crear nuevo cartón Bingo"
    def nuevo_carton_bingo(self):
        # Crear y mostrar la ventana de BingoCard
        self.bingo_card_window = BingoCard()
        self.bingo_card_window.show()

    # Función para manejar el evento de "Crear Juego"
    def nuevo_juego(self):
        # Crear y mostrar la ventana de EditViewWindow
        self.edit_card_window = NewGameWindow()
        self.edit_card_window.show()

    # Función para manejar el evento de "Editar/Ver Juegos y Cartones"
    def editar_ver_juegos(self):
        # Crear y mostrar la ventana de EditViewWindow
        self.new_game_window = EditViewWindow()
        self.new_game_window.show()

    # Función para manejar el evento de "Salir"
    def salir(self):
        self.close()

# Crear la aplicación y la ventana principal
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()

# Ejecutar la aplicación
sys.exit(app.exec_())
