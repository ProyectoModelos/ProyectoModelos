from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Configura el path a tu WebDriver
driver_path = r'C:\Users\crist\Downloads\chromedriver-win64\chromedriver.exe'  # Reemplaza esto con el path a tu WebDriver

# Inicializa el servicio de Chrome
service = Service(driver_path)

# Inicializa el navegador
driver = webdriver.Chrome(service=service)  # Cambia a webdriver.Firefox() o webdriver.Edge() si usas otro navegador

# Abre la página de ChatGPT
driver.get('https://www.youtube.com/')

# Espera a que la página cargue y se muestre el campo de entrada
time.sleep(5)  # Ajusta el tiempo según sea necesario

# Encuentra el campo de entrada del chat (esto puede variar dependiendo del HTML de la página)
input_field = driver.find_element(By.NAME, 'search_query')

# La frase que queremos pegar
text_to_paste = 'Josedeodo'

# Escribe la frase en el campo de entrada
input_field.send_keys(text_to_paste)

# Presiona Enter
input_field.send_keys(Keys.ENTER)

time.sleep(5)

# Encuentra la primera opción seleccionable y haz clic en ella (esto puede variar dependiendo del HTML de la página)
# Asegúrate de inspeccionar la página y encontrar el selector correcto para el elemento que quieres hacer clic
first_option = driver.find_element(By.CSS_SELECTOR, '.ytd-video-renderer')  # Reemplaza con el selector adecuado
first_option.click()
# Espera unos segundos para ver el resultado
time.sleep(150)

# Cierra el navegador
#driver.quit()
