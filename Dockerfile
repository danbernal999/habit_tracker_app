# Imagen base
FROM python:3.11

# Directorio de trabajo
WORKDIR /app

# 1. INSTALAR HERRAMIENTAS DE COMPILACIÓN
# 'python-jose[cryptography]' requiere cabeceras de desarrollo y librerías de compilación (gcc, make)
# para compilar el módulo cryptography de manera eficiente.
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar el servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

