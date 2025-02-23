import pandas as pd
import os
import re

# Ruta del archivo original y del archivo procesado
file_path = "05_challenge_we_are_pipol_python/noticias.xlsx"
processed_file_path = "05_challenge_we_are_pipol_python/Noticias_Procesadas.xlsx"

# Verificar si el archivo original existe
if not os.path.exists(file_path):
    print(f"El archivo {file_path} no existe.")
else:
    # Cargar el Excel original
    df = pd.read_excel(file_path)

    # Función para contar palabras en el título
    def count_words(title):
        return len(str(title).split())

    # Función para contar caracteres en el título
    def count_chars(title):
        return len(str(title))

    def capitalized_words(title):
        # Limpiar caracteres no alfabéticos que podrían interferir
        cleaned_title = re.sub(r"[^a-zA-Z\s]", "", title)
    
        # Filtrar las palabras que empiezan con mayúscula
        return [word for word in cleaned_title.split() if word[0].isupper()]

    # Agregar nuevas columnas
    df["Word Count"] = df["Title"].apply(count_words)
    df["Character Count"] = df["Title"].apply(count_chars)
    df["Capitalized Words"] = df["Title"].apply(capitalized_words)

    # Guardar el nuevo archivo sin modificar el original
    df.to_excel(processed_file_path, index=False)
    print(f"Archivo procesado guardado correctamente en {processed_file_path}")
