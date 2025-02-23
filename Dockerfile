# Usar imagen base de Python
FROM python:3.12-slim

# Instalar dependencias del sistema y Chrome headless
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Configurar variables de entorno para Chrome y ChromeDriver
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . /app

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Configurar comando de ejecución
CMD ["python", "script_principal.py"]
