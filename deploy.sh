#!/bin/bash

# Configuración del proyecto en Google Cloud
PROJECT_ID="mi-proyecto-cloudrun"
REGION="us-central1"
IMAGE_NAME="mi_scraper"
REPO_NAME="scraper-repo"
JOB_NAME="mi-scraper-job"

# 1️⃣ Verificar si el repositorio en Artifact Registry existe
echo "🔍 Verificando si el repositorio en Artifact Registry existe..."
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION > /dev/null 2>&1; then
  echo "⚠️  El repositorio $REPO_NAME no existe. Creándolo ahora..."
  gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Repositorio para imágenes Docker del scraper"
  echo "✅ Repositorio $REPO_NAME creado."
else
  echo "✅ Repositorio $REPO_NAME ya existe."
fi

# 2️⃣ Construcción de la imagen Docker
echo "🔨 Construyendo la imagen de Docker..."
docker build -t $IMAGE_NAME .

# 3️⃣ Autenticarse con Google Cloud y configurar Docker para Artifact Registry
echo "🔐 Configurando autenticación en Artifact Registry..."
gcloud auth configure-docker $REGION-docker.pkg.dev

# 4️⃣ Subir la imagen a Google Artifact Registry
echo "📤 Subiendo imagen a Artifact Registry..."
ARTIFACT_REGISTRY_PATH="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME"
docker tag $IMAGE_NAME $ARTIFACT_REGISTRY_PATH
docker push $ARTIFACT_REGISTRY_PATH

# 5️⃣ Desplegar el Job en Cloud Run con la variable de entorno correcta
echo "🚀 Desplegando en Cloud Run Job..."
gcloud run jobs deploy $JOB_NAME \
  --image $ARTIFACT_REGISTRY_PATH \
  --region $REGION \
  --task-timeout=900 \
  --memory 2048Mi \
  --set-env-vars=GOOGLE_APPLICATION_CREDENTIALS="/app/cloudrun_bigquery_service.json"

echo "✅ Despliegue completado. Para ejecutar el Job, usa:"
echo "gcloud run jobs execute $JOB_NAME --region $REGION"
