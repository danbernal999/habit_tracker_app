from fastapi import FastAPI
from app.routers import user_routes, habit_routes, record_routes
from app.database.config import engine, Base
from app.models import models

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Habit Tracker API", version="1.0")

# Incluir routers
app.include_router(user_routes.router)
app.include_router(habit_routes.router)
app.include_router(record_routes.router)

@app.get("/")
def root():
    return {"message": "🚀 Habit Tracker API funcionando correctamente"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}