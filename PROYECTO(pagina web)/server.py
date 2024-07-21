from flask import Flask, request, jsonify
import os
import PyPDF2
import mysql.connector
import re

app = Flask(__name__)

# Función para conectar a la base de datos MySQL
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="datos_empresariales_extraidos"
        )
    except mysql.connector.Error as e:
        print(f"El error '{e}' ocurrió")
    
    return connection

# Función para ejecutar una consulta SQL
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except mysql.connector.Error as e:
        print(f"El error '{e}' ocurrió")

# Función para clasificar el texto extraído
def classify_text(text):
    data = {
        "nombre": None,
        "fecha_nacimiento": None,
        "telefono": None,
        "correo": None,
        "fax": None,
        "id": None,
        "idiomas": None
    }
    
    patterns = {
        "nombre": r"(?i)(?:name|nombre):?\s*(.+)",
        "fecha_nacimiento": r"(?i)(?:date of birth|fecha de nacimiento):?\s*(\d{2}/\d{2}/\d{4})",
        "telefono": r"(?i)(?:cell|celular|phone|teléfono):?\s*(\+?\d[\d\s-]{7,})",
        "correo": r"(?i)(?:email|correo electrónico):?\s*([\w\.-]+@[\w\.-]+)",
        "fax": r"(?i)(?:fax):?\s*(\+?\d[\d\s-]{7,})",
        "id": r"(?i)(?:id|identificación|id_):?\s*(\w+)",
        "idiomas": r"(?i)(?:languages|idiomas):?\s*(.+)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            data[key] = match.group(1).strip()
    
    return data

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    file = request.files['pdf']
    if file and file.filename.endswith('.pdf'):
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        try:
            pdf_file_obj = open(file_path, 'rb')
            pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
            num_pages = pdf_reader.getNumPages()

            connection = create_connection()

            for page in range(num_pages):
                page_obj = pdf_reader.getPage(page)
                text = page_obj.extract_text().strip()
                
                classified_data = classify_text(text)
                
                nombre = classified_data["nombre"]
                fecha_nacimiento = classified_data["fecha_nacimiento"]
                if fecha_nacimiento:
                    fecha_nacimiento = "-".join(reversed(fecha_nacimiento.split("/")))  # Convertir a formato YYYY-MM-DD
                telefono = classified_data["telefono"]
                correo = classified_data["correo"]
                fax = classified_data["fax"]
                id_doc = classified_data["id"]
                idiomas = classified_data["idiomas"]
                
                insert_text_query = f"""
                INSERT INTO pdf_data (file_name, page_number, nombre, fecha_nacimiento, telefono, correo, fax, id_doc, idiomas)
                VALUES ('{file.filename}', {page}, "{nombre}", "{fecha_nacimiento}", "{telefono}", "{correo}", "{fax}", 
                "{id_doc}", "{idiomas}")
                """
                execute_query(connection, insert_text_query)

            pdf_file_obj.close()
            connection.close()
            return 'PDF procesado exitosamente', 200
        except Exception as e:
            print(f"Error: {e}")
            return 'Error al procesar el PDF', 500

@app.route('/view_data', methods=['GET'])
def view_data():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM pdf_data")
        rows = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify(rows), 200
    except mysql.connector.Error as e:
        print(f"El error '{e}' ocurrió")
        return 'Error al obtener los datos', 500

if __name__ == '__main__':
    app.run(debug=True)
