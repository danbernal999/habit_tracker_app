from fastapi import APIRouter, Depends, HTTPException, status   # Importar APIRouter
from sqlalchemy.orm import Session                              # Importar Session para manejar la base de datos        
from typing import List                                         # Importar List para tipado
import logging                                                  # Importar logging para registrar eventos
from app.database.config import get_db                          # Importar función para obtener la sesión de la base de datos
from app.models import models                                   # Importar modelos de la base de datos
from app.schemas import schemas                                 # Importar esquemas Pydantic

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/habits", tags=["habits"])

@router.post("/", response_model=schemas.Habit, status_code=status.HTTP_201_CREATED)
def create_habit(habit: schemas.HabitCreate, user_id: int, db: Session = Depends(get_db)):
    """
    Crear un nuevo hábito.
    
    - **name**: Nombre del hábito
    - **description**: Descripción del hábito
    - **frequency**: Frecuencia (daily, weekly, monthly)
    - **user_id**: ID del usuario propietario
    """
    try:
        logger.info(f"Intentando crear hábito '{habit.name}' para usuario ID: {user_id}")
        
        # Verificar que el usuario existe
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            logger.warning(f"Usuario no encontrado: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        # Crear el hábito
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
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[schemas.Habit])
def get_habits(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtener lista de hábitos de un usuario.
    
    - **user_id**: ID del usuario
    - **skip**: Número de registros a saltar
    - **limit**: Número máximo de registros a retornar
    """
    try:
        logger.info(f"Obteniendo hábitos del usuario ID: {user_id}")
        
        habits = db.query(models.Habit).filter(
            models.Habit.user_id == user_id,
            models.Habit.is_active == True
        ).offset(skip).limit(limit).all()
        
        logger.info(f"Se encontraron {len(habits)} hábitos activos")
        return habits
        
    except Exception as e:
        logger.error(f"Error al obtener hábitos: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{habit_id}", response_model=schemas.Habit)
def get_habit(habit_id: int, db: Session = Depends(get_db)):
    """
    Obtener un hábito por ID.
    
    - **habit_id**: ID del hábito
    """
    try:
        logger.info(f"Buscando hábito con ID: {habit_id}")
        
        habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
        if habit is None:
            logger.warning(f"Hábito no encontrado: {habit_id}")
            raise HTTPException(status_code=404, detail="Habit not found")
        
        logger.info(f"Hábito encontrado: {habit.name}")
        return habit
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener hábito: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{habit_id}", response_model=schemas.Habit)
def update_habit(habit_id: int, habit: schemas.HabitCreate, db: Session = Depends(get_db)):
    """
    Actualizar un hábito existente.
    
    - **habit_id**: ID del hábito
    - **name**: Nuevo nombre del hábito
    - **description**: Nueva descripción
    - **frequency**: Nueva frecuencia
    """
    try:
        logger.info(f"Intentando actualizar hábito ID: {habit_id}")
        
        db_habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
        if db_habit is None:
            logger.warning(f"Hábito no encontrado: {habit_id}")
            raise HTTPException(status_code=404, detail="Habit not found")
        
        # Actualizar campos
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
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    """
    Desactivar un hábito (soft delete).
    
    - **habit_id**: ID del hábito a desactivar
    """
    try:
        logger.info(f"Intentando desactivar hábito ID: {habit_id}")
        
        db_habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
        if db_habit is None:
            logger.warning(f"Hábito no encontrado: {habit_id}")
            raise HTTPException(status_code=404, detail="Habit not found")
        
        # Soft delete
        db_habit.is_active = False
        db.commit()
        
        logger.info(f"Hábito desactivado exitosamente: {db_habit.name}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al desactivar hábito: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")