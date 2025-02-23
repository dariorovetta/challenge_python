
# 🚀 Web Scraper con Selenium, Docker y Google Cloud Run

## 📌 Descripción

Este proyecto implementa un **web scraper** que extrae noticias desde [Yogonet](https://www.yogonet.com/international/), realiza un post-procesamiento de datos y almacena los resultados en **Google BigQuery**.

* Se ejecuta tanto en **local** como en un **contenedor Docker**.
* Está desplegado como un **Cloud Run Job** en **Google Cloud**.
* Automatiza la ejecución de la extracción de datos y su almacenamiento en BigQuery.
* Se proporciona un **script de despliegue (`deploy.sh`)** para gestionar automáticamente la construcción y despliegue del contenedor en Google Cloud Run.

## 📁 **Estructura del Proyecto**

```
├── 05_challenge_we_are_pipol_python/
│   ├── script_principal.py      # Código principal del scraper
│   ├── requirements.txt         # Dependencias de Python
│   ├── Dockerfile               # Configuración para Docker
│   ├── deploy.sh                # Script de despliegue automatizado
│   ├── cloudrun_bigquery_service.json  # Credenciales para BigQuery (NO subir a GitHub)
│   ├── README.md                # Documentación del proyecto
```

---

## 🛠️ **Instalación y Ejecución en Local**

### **1️⃣ Clonar el repositorio**

```sh
git clone https://github.com/dariorovetta/challenge_python.git
cd challenge_python
```

### **2️⃣ Crear un entorno virtual y activarlo**

```sh
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### **3️⃣ Instalar dependencias**

```sh
pip install -r requirements.txt
```

### **4️⃣ Ejecutar el scraper en local**

```sh
python script_principal.py
```

---

## 🐳 **Ejecutar con Docker**

### **1️⃣ Construir la imagen de Docker**

```sh
docker build -t mi_scraper .
```

### **2️⃣ Ejecutar el contenedor con credenciales**

```sh
docker run --rm \
  -v "$(pwd)/cloudrun_bigquery_service.json:/app/cloudrun_bigquery_service.json" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/cloudrun_bigquery_service.json" \
  mi_scraper
```

📌 **Para Windows (CMD o PowerShell), usar ruta absoluta:**

```sh
docker run --rm -v "C:/ruta_absoluta/cloudrun_bigquery_service.json:/app/cloudrun_bigquery_service.json" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/cloudrun_bigquery_service.json" mi_scraper
```

---

## ☁️ **Despliegue Automatizado con `deploy.sh`**

### **1️⃣ Configuración previa**

Antes de ejecutar el script, asegúrate de haber iniciado sesión en Google Cloud y tener permisos suficientes:

```sh
gcloud auth login
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### **2️⃣ Ejecutar el script de despliegue**

El script `deploy.sh` se encarga de:
✅ Construir la imagen Docker.
✅ Subirla a **Google Artifact Registry**.
✅ Desplegar el Job en **Google Cloud Run**.

Para ejecutarlo, simplemente usa:

```sh
bash deploy.sh
```

Después del despliegue, verás el mensaje con el comando para ejecutar el Job en Cloud Run manualmente:

```sh
gcloud run jobs execute mi-scraper-job --region us-central1
```

Si deseas que el Job se ejecute automáticamente después del despliegue, puedes modificar `deploy.sh` agregando esta línea al final:

```sh
gcloud run jobs execute mi-scraper-job --region us-central1
```

---

## ☁️ **Despliegue manual en Google Cloud Run** (Alternativa a `deploy.sh`)

Si prefieres hacer el proceso manualmente, estos son los pasos:

### **1️⃣ Subir la imagen a Google Artifact Registry**

```sh
docker tag mi_scraper us-central1-docker.pkg.dev/mi-proyecto-cloudrun/scraper-repo/mi_scraper
docker push us-central1-docker.pkg.dev/mi-proyecto-cloudrun/scraper-repo/mi_scraper
```

### **2️⃣ Desplegar como Cloud Run Job**

```sh
gcloud run jobs deploy mi-scraper-job \
  --image us-central1-docker.pkg.dev/mi-proyecto-cloudrun/scraper-repo/mi_scraper \
  --region us-central1 \
  --task-timeout=900 \
  --memory 2048Mi \
  --set-env-vars=GOOGLE_APPLICATION_CREDENTIALS="/app/cloudrun_bigquery_service.json"
```

### **3️⃣ Ejecutar el Job en la nube**

```sh
gcloud run jobs execute mi-scraper-job --region us-central1
```

### **4️⃣ Ver logs en Google Cloud**

```sh
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=mi-scraper-job" --limit 50
```

🔗 O ver logs en: [Google Cloud Logs](https://console.cloud.google.com/logs)

---

## 📌 **Consideraciones Finales**

✔ **Cloud Run Job se ejecuta bajo demanda y finaliza automáticamente.**
✔ **Los datos son subidos a BigQuery tras cada ejecución.**
✔ **Se recomienda no subir las credenciales (`cloudrun_bigquery_service.json`) a GitHub.**
✔ **`deploy.sh` automatiza el proceso de despliegue, facilitando su ejecución.**
