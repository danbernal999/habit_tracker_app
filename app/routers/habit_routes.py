from fastapi import APIRouter, Depends, HTTPException, status   # Importo APIRouter y herramientas de FastAPI
from sqlalchemy.orm import Session                              # Importo Session para trabajar con la base de datos
from typing import List                                         # Importo List para definir tipos en respuestas
import logging                                                  # Uso logging para registrar eventos
from app.database.config import get_db                          # Importo la función que me da acceso a la DB
from app.models import models                                   # Importo los modelos (tablas)
from app.schemas import schemas                                 # Importo los esquemas de validación (Pydantic)

# Configuro el sistema de logs para registrar información útil de ejecución
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Creo un enrutador (router) con el prefijo /habits
# Esto significa que todas las rutas aquí empezarán con /habits
router = APIRouter(prefix="/habits", tags=["habits"])

# -------------------- CREAR HÁBITO --------------------
@router.post("/", response_model=schemas.Habit, status_code=status.HTTP_201_CREATED)
def create_habit(habit: schemas.HabitCreate, user_id: int, db: Session = Depends(get_db)):
    """
    Crear un nuevo hábito.
    """
    try:
        logger.info(f"Intentando crear hábito '{habit.name}' para usuario ID: {user_id}")
        
        # Primero verifico si el usuario existe
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            logger.warning(f"Usuario no encontrado: {user_id}")
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Creo el hábito y lo asocio al usuario
        db_habit = models.Habit(**habit.dict(), user_id=user_id)
        db.add(db_habit)
        db.commit()
        db.refresh(db_habit)
        
        logger.info(f"Hábito creado exitosamente: {habit.name} (ID: {db_habit.id})")
        return db_habit
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear hábito: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# -------------------- LISTAR HÁBITOS --------------------
@router.get("/", response_model=List[schemas.Habit])
def get_habits(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtener lista de hábitos de un usuario.
    """
    try:
        logger.info(f"Obteniendo hábitos del usuario ID: {user_id}")
        
        # Busco todos los hábitos activos del usuario
        habits = db.query(models.Habit).filter(
            models.Habit.user_id == user_id,
            models.Habit.is_active == True
        ).offset(skip).limit(limit).all()
        
        logger.info(f"Se encontraron {len(habits)} hábitos activos")
        return habits
        
    except Exception as e:
        logger.error(f"Error al obtener hábitos: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# -------------------- OBTENER HÁBITO POR ID --------------------
@router.get("/{habit_id}", response_model=schemas.Habit)
def get_habit(habit_id: int, db: Session = Depends(get_db)):
    """
    Obtener un hábito por ID.
    """
    try:
        logger.info(f"Buscando hábito con ID: {habit_id}")
        
        habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
        if habit is None:
            logger.warning(f"Hábito no encontrado: {habit_id}")
            raise HTTPException(status_code=404, detail="Habito no encontrado")
        
        logger.info(f"Hábito encontrado: {habit.name}")
        return habit
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener hábito: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# -------------------- ACTUALIZAR HÁBITO --------------------
@router.put("/{habit_id}", response_model=schemas.Habit)
def update_habit(habit_id: int, habit: schemas.HabitCreate, db: Session = Depends(get_db)):
    """
    Actualizar un hábito existente.
    """
    try:
        logger.info(f"Intentando actualizar hábito ID: {habit_id}")
        
        db_habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
        if db_habit is None:
            logger.warning(f"Hábito no encontrado: {habit_id}")
            raise HTTPException(status_code=404, detail="Habito no encontrado")
        
        # Recorro los campos del nuevo hábito y los asigno al existente
        for key, value in habit.dict().items():
            setattr(db_habit, key, value)
        
        db.commit()
        db.refresh(db_habit)
        
        logger.info(f"Hábito actualizado exitosamente: {db_habit.name}")
        return db_habit
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar hábito: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# -------------------- ELIMINAR (DESACTIVAR) HÁBITO --------------------
@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    """
    Desactivar un hábito (soft delete).
    """
    try:
        logger.info(f"Intentando desactivar hábito ID: {habit_id}")
        
        db_habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
        if db_habit is None:
            logger.warning(f"Hábito no encontrado: {habit_id}")
            raise HTTPException(status_code=404, detail="Habito no encontrado")
        
        # En lugar de borrar, solo lo marco como inactivo
        db_habit.is_active = False
        db.commit()
        
        logger.info(f"Hábito desactivado exitosamente: {db_habit.name}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al desactivar hábito: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    
""" 
“Con este archivo manejo toda la lógica CRUD (crear, leer, actualizar y eliminar) de los hábitos de los usuarios. Cada ruta tiene validaciones, manejo de errores y logs para saber qué ocurre en mi API. Además, uso soft delete para no eliminar los hábitos definitivamente, solo los desactivo.”

"""
