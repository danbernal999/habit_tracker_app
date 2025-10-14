from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
import logging
from app.database.config import get_db
from app.models import models
from app.schemas import schemas

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/records", tags=["records"])

@router.post("/", response_model=schemas.Record, status_code=status.HTTP_201_CREATED)
def create_record(record: schemas.RecordCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo registro de hábito completado.
    
    - **habit_id**: ID del hábito
    - **date**: Fecha del registro
    - **completed**: Si se completó o no
    - **notes**: Notas adicionales (opcional)
    """
    try:
        logger.info(f"Intentando crear registro para hábito ID: {record.habit_id} en fecha: {record.date}")
        
        # Verificar que el hábito existe
        habit = db.query(models.Habit).filter(models.Habit.id == record.habit_id).first()
        if not habit:
            logger.warning(f"Hábito no encontrado: {record.habit_id}")
            raise HTTPException(status_code=404, detail="Habitos no funcional")
        
        # Verificar si ya existe un registro para esa fecha
        existing_record = db.query(models.Record).filter(
            models.Record.habit_id == record.habit_id,
            models.Record.date == record.date
        ).first()
        
        if existing_record:
            logger.warning(f"Ya existe un registro para el hábito {record.habit_id} en la fecha {record.date}")
            raise HTTPException(status_code=400, detail="Record exitente para esta fecha")
        
        # Crear el registro
        db_record = models.Record(**record.dict())
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        logger.info(f"Registro creado exitosamente (ID: {db_record.id})")
        return db_record
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear registro: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/habit/{habit_id}", response_model=List[schemas.Record])
def get_habit_records(habit_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtener todos los registros de un hábito específico.
    
    - **habit_id**: ID del hábito
    - **skip**: Número de registros a saltar
    - **limit**: Número máximo de registros a retornar
    """
    try:
        logger.info(f"Obteniendo registros del hábito ID: {habit_id}")
        
        # Verificar que el hábito existe
        habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
        if not habit:
            logger.warning(f"Hábito no encontrado: {habit_id}")
            raise HTTPException(status_code=404, detail="Habitos no funcional")
        
        records = db.query(models.Record).filter(
            models.Record.habit_id == habit_id
        ).order_by(models.Record.date.desc()).offset(skip).limit(limit).all()
        
        logger.info(f"Se encontraron {len(records)} registros")
        return records
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener registros: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/{record_id}", response_model=schemas.Record)
def get_record(record_id: int, db: Session = Depends(get_db)):
    """
    Obtener un registro por ID.
    
    - **record_id**: ID del registro
    """
    try:
        logger.info(f"Buscando registro con ID: {record_id}")
        
        record = db.query(models.Record).filter(models.Record.id == record_id).first()
        if record is None:
            logger.warning(f"Registro no encontrado: {record_id}")
            raise HTTPException(status_code=404, detail="Record no funcional")
        
        logger.info(f"Registro encontrado (ID: {record_id})")
        return record
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener registro: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/{record_id}", response_model=schemas.Record)
def update_record(record_id: int, completed: bool, notes: str = None, db: Session = Depends(get_db)):
    """
    Actualizar un registro existente.
    
    - **record_id**: ID del registro
    - **completed**: Estado de completado
    - **notes**: Notas adicionales
    """
    try:
        logger.info(f"Intentando actualizar registro ID: {record_id}")
        
        db_record = db.query(models.Record).filter(models.Record.id == record_id).first()
        if db_record is None:
            logger.warning(f"Registro no encontrado: {record_id}")
            raise HTTPException(status_code=404, detail="Record no funcional")
        
        # Actualizar campos
        db_record.completed = completed
        if notes:
            db_record.notes = notes
        
        db.commit()
        db.refresh(db_record)
        
        logger.info(f"Registro actualizado exitosamente (ID: {record_id})")
        return db_record
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar registro: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")