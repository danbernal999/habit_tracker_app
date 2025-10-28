FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY backend-requirements.txt .

# Instalar dependencias base
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir bcrypt==4.1.2 && \
    pip install --no-cache-dir -r backend-requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Crear directorio para uploads si no existe
RUN mkdir -p /app/uploads

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

