import sys
import re
import PyPDF2
import mysql.connector
from mysql.connector import Error
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit, 
                             QVBoxLayout, QHBoxLayout, QWidget, QProgressBar, QMessageBox, 
                             QLabel, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QDialogButtonBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal, Qt  

# Función para conectar a la base de datos MySQL
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Conexión a MySQL exitosa")
        print("API key Aceptada")
    except Error as e:
        print(f"El error '{e}' ocurrió")
    
    return connection

# Función para ejecutar una consulta SQL
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Consulta ejecutada exitosamente")
    except Error as e:
        print(f"El error '{e}' ocurrió")

# Función para clasificar el texto extraído
def classify_text(text):
    data = {
        "name": None,
        "date_of_birth": None,
        "cell_number": None,
        "email": None,
        "fax": None,
        "id": None,
        "languages": None
    }
    
    patterns = {
        "name": r"(?i)(?:name|nombre):?\s*(.+)",
        "date_of_birth": r"(?i)(?:date of birth|fecha de nacimiento):?\s*(\d{2}/\d{2}/\d{4})",
        "cell_number": r"(?i)(?:cell|celular|phone|teléfono):?\s*(\+?\d[\d\s-]{7,})",
        "email": r"(?i)(?:email|correo electrónico):?\s*([\w\.-]+@[\w\.-]+)",
        "fax": r"(?i)(?:fax|cedula):?\s*(\+?\d[\d\s-]{10,})",
        "id": r"(?i)(?:id|identificación|id_):?\s*(\w+)",
        "languages": r"(?i)(?:lenguaje|idiomas):?\s*(.+)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            data[key] = match.group(1).strip()
    
    return data

class PDFProcessThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool)

    def __init__(self, pdf_path):
        super().__init__()
        self.pdf_path = pdf_path

    def run(self):
        try:
            pdf_file_obj = open(self.pdf_path, 'rb')
            pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
            num_pages = pdf_reader.getNumPages()

            connection = create_connection("localhost", "root", "", "datos_empresariales_extraidos")

            for page in range(num_pages):
                page_obj = pdf_reader.getPage(page)
                text = page_obj.extract_text().strip()
                
                classified_data = classify_text(text)
                
                # Preparar los datos para la inserción
                name = classified_data["name"]
                date_of_birth = classified_data["date_of_birth"]
                if date_of_birth:
                    date_of_birth = "-".join(reversed(date_of_birth.split("/")))  # Convertir a formato YYYY-MM-DD
                cell_number = classified_data["cell_number"]
                email = classified_data["email"]
                fax = classified_data["fax"]
                id_doc = classified_data["id"]
                languages = classified_data["languages"]
                
                # Insertar datos en la base de datos
                insert_text_query = f"""
                INSERT INTO pdf_data (file_name, page_number, name, date_of_birth, cell_number, email, fax, id_doc, languages)
                VALUES ('{self.pdf_path}', {page}, "{name}", "{date_of_birth}", "{cell_number}", "{email}", "{fax}", 
                "{id_doc}", "{languages}")
                """
                execute_query(connection, insert_text_query)
                
                self.progress.emit(int((page + 1) / num_pages * 100))

            pdf_file_obj.close()
            connection.close()
            self.finished.emit(True)
        except Exception as e:
            print(f"Error: {e}")
            self.finished.emit(False)

class PDFExtractorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdfPath = None  # Initialize pdfPath
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PDF Data Extractor')
        self.setGeometry(100, 100, 800, 600)

        # Crear widget central y layout principal
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Grupo de selección y procesamiento de PDF
        pdf_group = QGroupBox("Operaciones PDF")
        pdf_layout = QHBoxLayout()

        self.selectButton = QPushButton('Seleccionar PDF', self)
        self.selectButton.setIcon(QIcon('icons/open.png'))  # Asegúrate de tener este icono
        self.selectButton.clicked.connect(self.selectPDF)

        self.processButton = QPushButton('Extraer Datos', self)
        self.processButton.setIcon(QIcon('icons/process.png'))  # Asegúrate de tener este icono
        self.processButton.clicked.connect(self.processPDF)

        pdf_layout.addWidget(self.selectButton)
        pdf_layout.addWidget(self.processButton)
        pdf_group.setLayout(pdf_layout)

        # Barra de progreso
        self.progressBar = QProgressBar(self)

        # Etiquetas informativas
        self.infoLabel = QLabel('AUTOMATIZACION DE PROCESOS ROBOTICOS: ROBOTS DIGITALES.', self)
        self.infoLabel.setWordWrap(True)  # Permite que el texto se ajuste a múltiples líneas

        # Tabla para mostrar datos
        self.dataTable = QTableWidget()
        self.dataTable.setColumnCount(10)  # Ajusta este número según las columnas que tengas
        self.dataTable.setHorizontalHeaderLabels(["ID", "Archivo", "Página", "Nombre", "FdN", "Celular", "Email", "Cédula", "ID Doc", "Idiomas"])
        
        # Botón para ver datos
        self.viewDataButton = QPushButton('Actualizar Base de Datos', self)
        self.viewDataButton.setIcon(QIcon('icons/view.png'))  # Asegúrate de tener este icono
        self.viewDataButton.clicked.connect(self.viewData)

        # Botón para preguntar si desea agregar otro archivo o salir
        self.addAnotherButton = QPushButton('Agregar otro archivo o Salir', self)
        self.addAnotherButton.setIcon(QIcon('icons/question.png'))  # Asegúrate de tener este icono
        self.addAnotherButton.clicked.connect(self.askAddAnotherOrExit)

        # Agregar widgets al layout principal
        main_layout.addWidget(self.infoLabel)
        main_layout.addWidget(pdf_group)
        main_layout.addWidget(self.progressBar)
        main_layout.addWidget(self.dataTable)
        main_layout.addWidget(self.viewDataButton)
        main_layout.addWidget(self.addAnotherButton)

        self.setCentralWidget(central_widget)

        # Aplicar estilos
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                
            }
            QPushButton {
                background-color: #849ED0;
                color: white;
                border: none;
                padding: 10px 20px;
                margin: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #98BAD2;
            }
            QGroupBox {
                font-weight: bold;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9f9f9;
            }
        """)

    def selectPDF(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Seleccionar PDF", "", "PDF Files (*.pdf)", options=options)
        if fileName:
            self.pdfPath = fileName
            QMessageBox.information(self, "Archivo: ", f"Selected file: {fileName}")

    def processPDF(self):
        if not self.pdfPath:
            QMessageBox.warning(self, "Error", "Por favor, seleccione un archivo PDF primero.")
            return

        self.progressBar.setValue(0)
        self.processButton.setEnabled(False)
        self.selectButton.setEnabled(False)

        self.thread = PDFProcessThread(self.pdfPath)
        self.thread.progress.connect(self.updateProgress)
        self.thread.finished.connect(self.onProcessFinished)
        self.thread.start()

    def updateProgress(self, value):
        self.progressBar.setValue(value)

    def onProcessFinished(self, success):
        self.processButton.setEnabled(True)
        self.selectButton.setEnabled(True)
        if success:
            QMessageBox.information(self, "Éxito", "El PDF ha sido procesado exitosamente.")
        else:
            QMessageBox.warning(self, "Error", "Hubo un error al procesar el PDF.")

    def viewData(self):
        try:
            connection = create_connection("localhost", "root", "", "datos_empresariales_extraidos")
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM pdf_data")
            rows = cursor.fetchall()
            
            self.dataTable.setRowCount(0)
            for row_number, row_data in enumerate(rows):
                self.dataTable.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.dataTable.setItem(row_number, column_number, QTableWidgetItem(str(data)))
                    
            cursor.close()
            connection.close()
        except Error as e:
            print(f"El error '{e}' ocurrió")

    def askAddAnotherOrExit(self):
        reply = QMessageBox.question(self, 'Add Another or Exit', 
                                     '¿Desea agregar otro archivo o salir?', 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.selectPDF()
        else:
            self.close()

def main():
    app = QApplication(sys.argv)
    ex = PDFExtractorApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

