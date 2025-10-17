import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# NOTA: Ya no necesitamos cargar dotenv si confiamos en Docker Compose
# o si ejecutamos el script directamente con variables de entorno.

# Leemos la variable de entorno DATABASE_URL. 
# En Docker Compose, esta será la cadena de conexión de PostgreSQL.
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    # Esto ayuda a diagnosticar si la variable no se inyectó correctamente
    raise ValueError("DATABASE_URL no está configurada en el entorno.")

# Creamos el engine
# Para SQLite, usamos connect_args para evitar errores de threading
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Para PostgreSQL u otras bases de datos
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Creamos la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Declarativa (necesaria para definir tus modelos)
Base = declarative_base()

# Dependencia para obtener la sesión de la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()