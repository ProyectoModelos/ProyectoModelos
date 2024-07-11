import PyPDF2
import mysql.connector
from mysql.connector import Error

pdf_file_obj = open('doc2.pdf', 'rb')

pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
# print(pdf_reader.documentInfo)
print(pdf_reader.getNumPages())

for page in range(pdf_reader.getNumPages()):

    page_obj = pdf_reader.getPage(page)

    text = page_obj.extract_text()

    print(text.strip())

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

# Conexión a la base de datos
connection = create_connection("localhost", "root", "", "datos_empresariales_extraidos")

# Crear tabla si no existe
create_table_query = """
CREATE TABLE IF NOT EXISTS pdf_data (
  id INT AUTO_INCREMENT, 
  file_name VARCHAR(100) NOT NULL,
  page_number INT NOT NULL,
  text TEXT NOT NULL, 
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
    
    # Insertar datos en la base de datos
    insert_text_query = f"""
    INSERT INTO pdf_data (file_name, page_number, text) 
    VALUES ('doc2.pdf', {page}, "{text}")
    """
    execute_query(connection, insert_text_query)

print("Datos insertados en la base de datos.")

