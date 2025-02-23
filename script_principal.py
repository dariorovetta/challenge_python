import time
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from google.cloud import bigquery
import os
import platform

### --- 1. FUNCIONES PARA SCRAPING --- ###
def extract_initial_news(driver):
    """Extrae noticias desde Yogonet en una primera etapa, dejando None en los kickers faltantes."""
    
    url = "https://www.yogonet.com/international/"
    driver.get(url)

    news_data = []
    articles = driver.find_elements(By.CSS_SELECTOR, ".contenedor_dato_modulo")

    print(f"Cantidad de artículos encontrados: {len(articles)}")

    for article in articles:
        try:
            kicker = article.find_element(By.CSS_SELECTOR, ".volanta.fuente_roboto_slab").text
        except:
            kicker = None  # Dejar en None si no se encuentra

        try:
            title = article.find_element(By.CSS_SELECTOR, ".titulo.fuente_roboto_slab").text
            image = article.find_element(By.CSS_SELECTOR, ".imagen img").get_attribute("src")
            link = article.find_element(By.CSS_SELECTOR, ".titulo.fuente_roboto_slab a").get_attribute("href")
        except Exception as e:
            print(f"Error al extraer datos de una noticia: {e}")
            continue  # Salta a la siguiente noticia en caso de error

        news_data.append({
            "Title": title,
            "Kicker": kicker,
            "Image": image,
            "Link": link
        })

    return pd.DataFrame(news_data)

def update_missing_kickers(driver, df):
    """Accede a los enlaces de las noticias y actualiza los kickers que son None."""
    
    for index, row in df.iterrows():
        if row["Kicker"] is None:  # Solo accede a los enlaces donde falta el kicker
            try:
                driver.get(row["Link"])
                time.sleep(2)  # Esperar a que la página cargue completamente
                
                kicker = driver.find_element(By.XPATH, "/html/body/div[4]/div[5]/div/div[2]/div").text
                df.at[index, "Kicker"] = kicker
                print(f"Kicker actualizado para: {row['Title']} → {kicker}")
            except:
                df.at[index, "Kicker"] = "Kicker no encontrado"

    return df

### --- 2. FUNCIONES PARA POST-PROCESAMIENTO --- ###
def count_words(title):
    """Cuenta la cantidad de palabras en el título."""
    if pd.isna(title):  
        return 0
    return len(str(title).split())

def count_chars(title):
    """Cuenta la cantidad de caracteres en el título."""
    if pd.isna(title):
        return 0
    return len(str(title))

def capitalized_words(title):
    """Devuelve una lista de palabras con la primera letra en mayúscula."""
    if pd.isna(title):
        return []
    
    cleaned_title = re.sub(r"[^a-zA-Z\s]", "", title)  
    return [word for word in cleaned_title.split() if word and word[0].isupper()]

def process_news_data(df):
    """Añade métricas al DataFrame de noticias."""
    
    df["Word_Count"] = df["Title"].apply(count_words)
    df["Character_Count"] = df["Title"].apply(count_chars)
    df["Capitalized_Words"] = df["Title"].apply(lambda x: ", ".join(capitalized_words(x)))

    print("Post-procesamiento completado.")
    return df

### --- 3. FUNCIÓN PARA CARGAR A BIGQUERY --- ###
def upload_to_bigquery(df):
    """Sube los datos a BigQuery, adaptando la ruta de credenciales según el entorno."""

    # Detectar si el script se ejecuta en Windows o en Docker (Linux)
    if platform.system() == "Windows":
        print("Ejecutando en Windows...")
        credentials_path = "C:/Users/dario/OneDrive/Escritorio/daroPotterHead/05_challenge_we_are_pipol_python/cloudrun_bigquery_service.json"
    else:
        print("Ejecutando en Docker (Linux)...")
        credentials_path = "/app/cloudrun_bigquery_service.json"

    # Verificar si el archivo de credenciales existe antes de intentar usarlo
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"❌ Archivo de credenciales no encontrado: {credentials_path}")

    # Configurar cliente de BigQuery
    client = bigquery.Client.from_service_account_json(credentials_path)

    # Definir el ID de proyecto y la tabla
    project_id = "mi-proyecto-cloudrun"  # Reemplaza con tu ID de proyecto
    dataset_id = "scraping_dataset"  # Nombre del dataset en BigQuery
    table_id = f"{project_id}.{dataset_id}.noticias"  # Nombre completo de la tabla

    print(f"Cargando datos en: {table_id}...")

    # Configuración de la carga
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")

    # Cargar datos a BigQuery
    try:
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()  # Esperar a que la carga termine
        print("✅ Datos cargados correctamente en BigQuery.")
    except Exception as e:
        print(f"❌ Error al subir datos a BigQuery: {e}")

### --- 4. FUNCIÓN WEB DRIVER --- ###
def get_driver():
    """Configura y devuelve una instancia del WebDriver de Chrome, adaptado para Windows y Docker."""

    options = Options()
    options.add_argument("--headless")  # Modo sin interfaz gráfica
    options.add_argument("--no-sandbox")  # Requerido para entornos Docker
    options.add_argument("--disable-dev-shm-usage")  # Usar /tmp en lugar de /dev/shm
    options.add_argument("--disable-gpu")  # Deshabilitar aceleración de hardware

    # Detectar si el script se ejecuta en Windows o en Docker (Linux)
    if platform.system() == "Windows":
        print("Ejecutando en Windows...")
        options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # Ruta de Chrome en Windows
        service = Service("C:/WebDriver/chromedriver.exe")  # Ruta de ChromeDriver en Windows
    else:
        print("Ejecutando en Docker (Linux)...")
        options.binary_location = "/usr/bin/chromium"  # Ruta de Chrome en Docker
        service = Service("/usr/bin/chromedriver")  # Ruta de ChromeDriver en Docker

    driver = webdriver.Chrome(service=service, options=options)
    return driver


### --- 5. FUNCIÓN PRINCIPAL --- ###
def main():
    """Ejecuta todo el proceso de scraping y post-procesamiento en un solo flujo."""
    
    # Iniciar web driver
    driver = get_driver()

    # Primera etapa: extraer datos iniciales
    df_news = extract_initial_news(driver)
    print("Primera extracción completada.")
    
    # Segunda etapa: actualizar kickers faltantes
    df_news = update_missing_kickers(driver, df_news)
    print("Actualización de kickers completada.")

    # Tercera etapa: post-procesamiento
    df_news = process_news_data(df_news)
    print("Post-procesamiento finalizado.")

    driver.quit()

    # Cuarta etapa: subir a BigQuery
    upload_to_bigquery(df_news)

    return df_news


# Ejecutar el proceso completo
df_final = main()
print(df_final.head())  # Mostrar primeras filas para verificar
