import os
from dotenv import load_dotenv

# CRÍTICO: Cargar variables de entorno ANTES de cualquier otra importación
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import user_routes, habit_routes, record_routes, excel_routes
from app.database.config import engine, Base
from app.models import models

# Aquí importo todas las dependencias necesarias de FastAPI,
# mis rutas personalizadas (users, habits y records),
# y la configuración de la base de datos.

# Creo las tablas en la base de datos si aún no existen.
# 'Base' contiene todos los modelos y 'engine' es la conexión con la base de datos.
Base.metadata.create_all(bind=engine)

# Inicializo mi aplicación principal de FastAPI.
app = FastAPI(title="Habit Tracker API", version="1.0")

# Incluyo las rutas que he definido en otros archivos (users, habits, records y excel),
# para que estén disponibles en la API.
app.include_router(user_routes.router)
app.include_router(habit_routes.router)
app.include_router(record_routes.router)
app.include_router(excel_routes.router)

# Configuro CORS para permitir que mi frontend (por ejemplo, Angular en localhost:4200)
# pueda comunicarse con esta API sin bloqueos del navegador.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost", 
        "http://localhost:4200", 
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:8000"],  # aquí puedo cambiar los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],  # permito todos los métodos HTTP (GET, POST, PUT, DELETE...)
    allow_headers=["*"],  # permito todos los encabezados
)

# Creo la carpeta para archivos estáticos si no existe
os.makedirs("frontend_excel", exist_ok=True)

# Monto la carpeta de archivos estáticos para servir el HTML del cargador de Excel
app.mount("/static", StaticFiles(directory="frontend_excel"), name="static")

# Defino una ruta raíz (GET /) para comprobar fácilmente si el servidor está corriendo.
@app.get("/")
def root():
    return {"message": "Bienvenido a la Habit Tracker API funcionando correctamente"}

# Creo otra ruta (GET /health) que sirve como punto de verificación de salud del servicio.
@app.get("/health")
def health_check():
    return {"status": "healthy"}





""" 
Con este código inicializo mi aplicación FastAPI, creo las tablas de la base de datos, importo mis rutas principales (usuarios, hábitos y registros), configuro CORS para permitir que mi frontend se comunique con la API, y agrego dos endpoints básicos: uno para probar que el servidor está funcionando y otro para verificar el estado de salud del servicio

"""