import sys
import re
import PyPDF2
import mysql.connector
from mysql.connector import Error
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit, 
                             QVBoxLayout, QHBoxLayout, QWidget, QProgressBar, QMessageBox, 
                             QLabel, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QDialog, QDialogButtonBox, QGridLayout)
from PyQt5.QtGui import QIcon, QPixmap
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
        "fax": r"(?i)(?:fax):?\s*(\+?\d[\d\s-]{7,})",
        "id": r"(?i)(?:id|identificación|id_):?\s*(\w+)",
        "languages": r"(?i)(?:languages|idiomas):?\s*(.+)"
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
        self.setGeometry(100, 100, 1000, 800)

        # Crear widget central y layout principal
        central_widget = QWidget()
        main_layout = QGridLayout(central_widget)

        # Crear área para arrastrar y soltar archivos PDF
        self.dropArea = QLabel('Arrastra el PDF aquí', self)
        self.dropArea.setAlignment(Qt.AlignCenter)
        self.dropArea.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                font-size: 16px;
                padding: 50px;
            }
        """)
        self.dropArea.setAcceptDrops(True)
        self.dropArea.setFixedHeight(150)

        # Grupo de selección y procesamiento de PDF
        pdf_group = QGroupBox("Operaciones de PDF")
        pdf_layout = QHBoxLayout()

        self.selectButton = QPushButton('Selecciona el Archivo PDF', self)
        self.selectButton.setIcon(QIcon('icons/open.png'))  # Asegúrate de tener este icono
        self.selectButton.clicked.connect(self.selectPDF)

        self.processButton = QPushButton('Procesar el PDF', self)
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
        self.dataTable.setHorizontalHeaderLabels(["ID", "File", "Page", "Name", "DOB", "Phone", "Email", "Fax", "ID Doc", "Languages"])
        
        # Previsualización de PDF
        self.pdfPreview = QLabel('Vista previa del PDF', self)
        self.pdfPreview.setAlignment(Qt.AlignCenter)
        self.pdfPreview.setStyleSheet("QLabel { background-color: #fff; border: 1px solid #ccc; padding: 10px; }")
        self.pdfPreview.setFixedHeight(300)

        # Botón para ver datos
        self.viewDataButton = QPushButton('Ver los datos de la Base de datos', self)
        self.viewDataButton.setIcon(QIcon('icons/view.png'))  # Asegúrate de tener este icono
        self.viewDataButton.clicked.connect(self.viewData)

        # Botón para preguntar si desea agregar otro archivo o salir
        self.addAnotherButton = QPushButton('Agregar otro Archivo o Salir', self)
        self.addAnotherButton.setIcon(QIcon('icons/question.png'))  # Asegúrate de tener este icono
        self.addAnotherButton.clicked.connect(self.askAddAnotherOrExit)

        # Agregar widgets al layout principal
        main_layout.addWidget(self.infoLabel, 0, 0, 1, 2)
        main_layout.addWidget(self.dropArea, 1, 0, 1, 2)
        main_layout.addWidget(pdf_group, 2, 0, 1, 2)
        main_layout.addWidget(self.progressBar, 3, 0, 1, 2)
        main_layout.addWidget(self.pdfPreview, 4, 0, 1, 2)
        main_layout.addWidget(self.dataTable, 5, 0, 1, 2)
        main_layout.addWidget(self.viewDataButton, 6, 0)
        main_layout.addWidget(self.addAnotherButton, 6, 1)

        self.setCentralWidget(central_widget)

        # Aplicar estilos
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton {
                font-size: 14px;
            }
            QLabel {
                font-size: 14px;
            }
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            if url.isLocalFile() and url.toLocalFile().lower().endswith('.pdf'):
                self.pdfPath = url.toLocalFile()
                self.dropArea.setText(f'Archivo cargado: {self.pdfPath}')
                pixmap = QPixmap(self.pdfPath)
                self.pdfPreview.setPixmap(pixmap.scaled(self.pdfPreview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                break

    def selectPDF(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo PDF", "", "PDF Files (*.pdf)", options=options)
        if fileName:
            self.pdfPath = fileName
            self.dropArea.setText(f'Archivo cargado: {self.pdfPath}')
            pixmap = QPixmap(self.pdfPath)
            self.pdfPreview.setPixmap(pixmap.scaled(self.pdfPreview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def processPDF(self):
        if self.pdfPath:
            self.thread = PDFProcessThread(self.pdfPath)
            self.thread.progress.connect(self.updateProgress)
            self.thread.finished.connect(self.onProcessFinished)
            self.thread.start()

    def updateProgress(self, value):
        self.progressBar.setValue(value)

    def onProcessFinished(self, success):
        if success:
            QMessageBox.information(self, "Completado", "Procesamiento del PDF completado con éxito.")
            self.loadDataIntoTable()
        else:
            QMessageBox.warning(self, "Error", "Hubo un problema al procesar el PDF.")

    def loadDataIntoTable(self):
        connection = create_connection("localhost", "root", "", "datos_empresariales_extraidos")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM pdf_data WHERE file_name = %s", (self.pdfPath,))
        rows = cursor.fetchall()

        self.dataTable.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.dataTable.setItem(i, j, QTableWidgetItem(str(val)))

        self.dataTable.resizeColumnsToContents()
        self.dataTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        cursor.close()
        connection.close()

    def viewData(self):
        self.loadDataIntoTable()

    def askAddAnotherOrExit(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Continuar o Salir")
        
        dialog_layout = QVBoxLayout()
        question_label = QLabel("¿Deseas agregar otro archivo PDF o salir de la aplicación?")
        dialog_layout.addWidget(question_label)

        button_box = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        button_box.button(QDialogButtonBox.Yes).setText("Agregar otro PDF")
        button_box.button(QDialogButtonBox.No).setText("Salir")

        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        dialog_layout.addWidget(button_box)
        dialog.setLayout(dialog_layout)
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.resetUI()
        else:
            self.close()

    def resetUI(self):
        self.pdfPath = None
        self.dropArea.setText('Arrastra el PDF aquí')
        self.pdfPreview.clear()
        self.progressBar.setValue(0)
        self.dataTable.setRowCount(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PDFExtractorApp()
    ex.show()
    sys.exit(app.exec_())
