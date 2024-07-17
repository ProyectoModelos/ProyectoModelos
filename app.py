import re
import PyPDF2
import mysql.connector
from mysql.connector import Error

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

    # Regex patterns para cada categoría
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

# Conexión a la base de datos
connection = create_connection("localhost", "root", "", "datos_empresariales_extraidos")

# Crear tabla si no existe
create_table_query = """
CREATE TABLE IF NOT EXISTS pdf_data (
  id INT AUTO_INCREMENT, 
  file_name VARCHAR(100) NOT NULL,
  page_number INT NOT NULL,
  name VARCHAR(100),
  date_of_birth DATE,
  cell_number VARCHAR(20),
  email VARCHAR(100),
  fax VARCHAR(20),
  id_doc VARCHAR(20),
  languages TEXT, 
  PRIMARY KEY (id)
) ENGINE = InnoDB
"""
execute_query(connection, create_table_query)

# Leer y procesar el archivo PDF
pdf_file_obj = open('doc2.pdf', 'rb')
pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
print(pdf_reader.getNumPages())

for page in range(pdf_reader.getNumPages()):
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
    VALUES ('doc2.pdf', {page}, "{name}", "{date_of_birth}", "{cell_number}", "{email}", "{fax}", "{id_doc}", "{languages}")
    """
    execute_query(connection, insert_text_query)

print("Datos insertados en la base de datos.")

