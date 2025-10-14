from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
from app.database.config import get_db
from app.models import models
from app.schemas import schemas
from passlib.context import CryptContext

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo usuario.
    
    - **username**: Nombre de usuario único
    - **email**: Correo electrónico único
    - **password**: Contraseña del usuario
    """
    try:
        logger.info(f"Intentando crear usuario: {user.username}")
        
        # Verificar si el email ya existe
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            logger.warning(f"Email ya registrado: {user.email}")
            raise HTTPException(status_code=400, detail="Correo Registrado")
        
        # Verificar si el username ya existe
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if db_user:
            logger.warning(f"Username ya registrado: {user.username}")
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Crear el usuario
        hashed_password = get_password_hash(user.password)
        db_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"Usuario creado exitosamente: {user.username}")
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear usuario: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[schemas.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtener lista de usuarios.
    
    - **skip**: Número de registros a saltar
    - **limit**: Número máximo de registros a retornar
    """
    try:
        logger.info(f"Obteniendo usuarios (skip={skip}, limit={limit})")
        users = db.query(models.User).offset(skip).limit(limit).all()
        logger.info(f"Se encontraron {len(users)} usuarios")
        return users
    except Exception as e:
        logger.error(f"Error al obtener usuarios: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Obtener un usuario por ID.
    
    - **user_id**: ID del usuario
    """
    try:
        logger.info(f"Buscando usuario con ID: {user_id}")
        user = db.query(models.User).filter(models.User.id == user_id).first()
        
        if user is None:
            logger.warning(f"Usuario no encontrado: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"Usuario encontrado: {user.username}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener usuario: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

""" RESUMEN """

""" El archivo define rutas para crear usuarios, obtener todos los usuarios y obtener un usuario por ID usando FastAPI y SQLAlchemy. Incluye validaciones para evitar duplicados, maneja errores y registra eventos importantes con logging. Las contraseñas se almacenan de forma segura usando hashing """