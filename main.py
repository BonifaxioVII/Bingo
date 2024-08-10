import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from BingoCardStructure import BingoCard, EditViewWindow, NewGameWindow

class MainWindow(QMainWindow): 
    def __init__(self):
        super().__init__()
        
        # Inicializar la interfaz de usuario
        self.initUI()
    
    # Organización de Widgets
    def initUI(self):
        # Configurar el título de la ventana
        self.setWindowTitle('BingoGO')
        self.showFullScreen()
        
        # Crear el widget central y el layout principal
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Nombre de la app
        app_name = QLabel("BingoGO", self)
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setFont(QFont("Arial", 100))

        # Crear y configurar el mensaje de bienvenida
        bienvenida = QLabel("Creado por DanBuiv", self)
        bienvenida.setAlignment(Qt.AlignCenter)
        bienvenida.setFont(QFont("Arial", 15))
        
        # Crear y configurar el mensaje de opciones
        opciones = QLabel("Elige una de las siguientes opciones:", self)
        opciones.setAlignment(Qt.AlignCenter)
        opciones.setFont(QFont("Arial", 25))
        
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
        
        # Configurar el layout principal
        layout.addWidget(app_name)
        layout.addWidget(bienvenida)
        layout.addWidget(opciones)
        layout.addWidget(btn_continuar_juego)
        layout.addWidget(btn_nuevo_carton)
        layout.addWidget(btn_crear_juego)
        layout.addWidget(btn_editar_ver_juegos)
        layout.addWidget(btn_salir)
        
        # Establecer el widget central
        self.setCentralWidget(central_widget)
    
    # Función para manejar el evento de "Continuar Juego"
    def continuar_juego(self):
        QMessageBox.information(self, "Continuar Juego", "Has seleccionado 'Continuar Juego'.")
    
    # Función para manejar el evento de "Crear nuevo cartón Bingo"
    def nuevo_carton_bingo(self):
        # Crear y mostrar la ventana de BingoCard
        self.bingo_card_window = BingoCard()
        self.bingo_card_window.setWindowModality(Qt.ApplicationModal)
        self.bingo_card_window.show()

    # Función para manejar el evento de "Crear Juego"
    def nuevo_juego(self):
        # Crear y mostrar la ventana de NewGameWindow
        self.new_game_window = NewGameWindow()
        self.new_game_window.show()

    # Función para manejar el evento de "Editar/Ver Juegos y Cartones"
    def editar_ver_juegos(self):
        # Crear y mostrar la ventana de EditViewWindow
        self.edit_view_window = EditViewWindow()
        self.edit_view_window.show()

    # Función para manejar el evento de "Salir"
    def salir(self):
        self.close()

# Crear la aplicación y la ventana principal
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()

# Ejecutar la aplicación
app.exec()

