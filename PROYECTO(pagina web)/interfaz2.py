import sys
import re
import PyPDF2
import mysql.connector
from mysql.connector import Error
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit, 
                             QVBoxLayout, QHBoxLayout, QWidget, QProgressBar, QMessageBox, 
                             QLabel, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QDialogButtonBox)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import openai

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
    except Error as e:
        print(f"El error '{e}' ocurrió")
    
    return connection

# Función para ejecutar una consulta SQL
def execute_query(connection, query):
    if connection is None:
        print("No se pudo ejecutar la consulta porque la conexión es None")
        return

    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Consulta ejecutada exitosamente")
    except Error as e:
        print(f"El error '{e}' ocurrió")

# Función para clasificar el texto extraído usando la API de OpenAI
def classify_text(entrada):
    openai.api_key = "sk-proj-kFAeLWMpogHSNYg2yCeyT3BlbkFJNwruWopGQKHl4JAUqXEL"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente útil."},
                {"role": "user", "content": f"Clasifica el siguiente texto: {entrada}"}
            ],
            max_tokens=1000,
            temperature=0.6
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error en classify_text: {e}")
        return None

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
                if classified_data is None:
                    raise Exception("Error en la clasificación del texto.")
                
                # Preparar los datos para la inserción
                nombre = classified_data.get("nombre", "")
                fecha_nacimiento = classified_data.get("fecha_nacimiento", "")
                if fecha_nacimiento:
                    fecha_nacimiento = "-".join(reversed(fecha_nacimiento.split("/")))  # Convertir a formato YYYY-MM-DD
                telefono = classified_data.get("telefono", "")
                correo = classified_data.get("correo", "")
                fax = classified_data.get("fax", "")
                id_doc = classified_data.get("id", "")
                idiomas = classified_data.get("idiomas", "")
                
                # Insertar datos en la base de datos
                insert_text_query = f"""
                INSERT INTO pdf_data (file_name, page_number, nombre, fecha_nacimiento, telefono, correo, fax, id_doc, idiomas)
                VALUES ('{self.pdf_path}', {page}, "{nombre}", "{fecha_nacimiento}", "{telefono}", "{correo}", "{fax}", 
                "{id_doc}", "{idiomas}")
                """
                execute_query(connection, insert_text_query)
                
                self.progress.emit(int((page + 1) / num_pages * 100))

            pdf_file_obj.close()
            if connection:
                connection.close()
            self.finished.emit(True)
        except Exception as e:
            print(f"Error en PDFProcessThread: {e}")
            self.finished.emit(False)

class PDFExtractorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdfPath = None  # Initialize pdfPath
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Extracto de Datos de PDF')
        self.setGeometry(100, 100, 800, 600)

        # Crear widget central y layout principal
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Grupo de selección y procesamiento de PDF
        pdf_group = QGroupBox("Operaciones de PDF")
        pdf_layout = QHBoxLayout()

        self.selectButton = QPushButton('Seleccionar Archivo PDF', self)
        self.selectButton.setIcon(QIcon('icons/open.png'))  # Asegúrate de tener este icono
        self.selectButton.clicked.connect(self.selectPDF)

        self.processButton = QPushButton('Procesar PDF', self)
        self.processButton.setIcon(QIcon('icons/process.png'))  # Asegúrate de tener este icono
        self.processButton.clicked.connect(self.processPDF)

        pdf_layout.addWidget(self.selectButton)
        pdf_layout.addWidget(self.processButton)
        pdf_group.setLayout(pdf_layout)

        # Barra de progreso
        self.progressBar = QProgressBar(self)

        # Etiquetas informativas
        self.infoLabel = QLabel('AUTOMATIZACION DE PROCESOS ROBOTICOS: ROBOTS DIGITALES', self)
        self.infoLabel.setWordWrap(True)  # Permite que el texto se ajuste a múltiples líneas

        # Tabla para mostrar datos
        self.dataTable = QTableWidget()
        self.dataTable.setColumnCount(10)  # Ajusta este número según las columnas que tengas
        self.dataTable.setHorizontalHeaderLabels(["ID", "Archivo", "Página", "Nombre", "Fecha de Nacimiento", "Teléfono", "Correo", "Fax", "ID Doc", "Idiomas"])
        
        # Botón para ver datos
        self.viewDataButton = QPushButton('Ver Datos de la Base de Datos', self)
        self.viewDataButton.setIcon(QIcon('icons/view.png'))  # Asegúrate de tener este icono
        self.viewDataButton.clicked.connect(self.viewData)

        # Botón para preguntar si desea agregar otro archivo o salir
        self.addAnotherButton = QPushButton('Agregar Otro Archivo o Salir', self)
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
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                margin: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
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
        fileName, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo PDF", "", "PDF Files (*.pdf)", options=options)
        if fileName:
            self.pdfPath = fileName
            QMessageBox.information(self, "Archivo Seleccionado", f"Archivo: {fileName}")

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
        if success:
            QMessageBox.information(self, "Éxito", "Procesamiento de PDF completado con éxito.")
        else:
            QMessageBox.critical(self, "Error", "Hubo un error en el procesamiento del PDF.")
        
        self.processButton.setEnabled(True)
        self.selectButton.setEnabled(True)

    def viewData(self):
        connection = create_connection("localhost", "root", "", "datos_empresariales_extraidos")
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM pdf_data")
            rows = cursor.fetchall()
            self.dataTable.setRowCount(0)
            for row in rows:
                rowPosition = self.dataTable.rowCount()
                self.dataTable.insertRow(rowPosition)
                for column, data in enumerate(row):
                    self.dataTable.setItem(rowPosition, column, QTableWidgetItem(str(data)))
            cursor.close()
            connection.close()

    def askAddAnotherOrExit(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("¿Qué desea hacer?")
        dialog_layout = QVBoxLayout()
        
        question_label = QLabel("¿Desea agregar otro archivo o salir?")
        dialog_layout.addWidget(question_label)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.button(QDialogButtonBox.Ok).setText("Agregar Otro Archivo")
        buttonBox.button(QDialogButtonBox.Cancel).setText("Salir")
        dialog_layout.addWidget(buttonBox)
        
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)
        
        dialog.setLayout(dialog_layout)
        
        if dialog.exec() == QDialog.Accepted:
            self.selectPDF()
        else:
            QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFExtractorApp()
    window.show()
    sys.exit(app.exec())
