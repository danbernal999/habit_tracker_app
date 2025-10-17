from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
from app.database.config import get_db
from app.models import models
from app.schemas import schemas
from passlib.context import CryptContext
from jose import JWTError, jwt

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users", 
    tags=["users"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    if len(password.encode("utf-8")) > 72:
        password = password[:72]
    elif len(password.encode("utf-8")) < 8:
        logger.warning(f"Contraseña demasiado corta: {password}")
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres")
    return pwd_context.hash(password)

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED, operation_id="create_user_v1")
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
            logger.warning(f"Correo ya registrado: {user.email}")
            raise HTTPException(status_code=400, detail="Correo Registrado")
        
        # Verificar si el username ya existe
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if db_user:
            logger.warning(f"Usuario ya registrado: {user.username}")
            raise HTTPException(status_code=400, detail="usuario Registrado")
        
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
        raise HTTPException(status_code=500, detail="Error interno del servidor")

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
        raise HTTPException(status_code=500, detail="Error interno del servidor")

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
            raise HTTPException(status_code=404, detail="Usuario no funcional")
        
        logger.info(f"Usuario encontrado: {user.username}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener usuario: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    

# Rutas para autenticación (login) - Ejemplo con JWT
from jose import JWTError, jwt

SECRET_KEY = "keysecreta"
ALGORITHM = "HS256"

@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Autenticar usuario y retornar un token JWT.
    
    - **email**: Correo electrónico del usuario
    - **password**: Contraseña del usuario
    """
    try:
        logger.info(f"Intentando autenticar usuario: {user.email}")
        
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if not db_user:
            logger.warning(f"Usuario no encontrado en BD: {user.email}")
            # Debug: mostrar todos los usuarios registrados
            all_users = db.query(models.User).all()
            logger.info(f"Usuarios en BD: {[u.email for u in all_users]}")
            raise HTTPException(status_code=400, detail="Credenciales inválidas")
        
        logger.info(f"Usuario encontrado: {db_user.email}")
        logger.info(f"Verificando contraseña...")
        password_valid = pwd_context.verify(user.password, db_user.hashed_password)
        logger.info(f"¿Contraseña válida? {password_valid}")
        
        if not password_valid:
            logger.warning(f"Contraseña incorrecta para usuario: {user.email}")
            raise HTTPException(status_code=400, detail="credenciales inválidas")
        
        # Crear token JWT
        token_data = {"sub": db_user.email}
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        logger.info(f"Usuario autenticado exitosamente: {user.email}")
        return {"access_token": token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al autenticar usuario: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")



""" 
El archivo define rutas para crear usuarios, obtener todos los usuarios y obtener un usuario por ID usando FastAPI y SQLAlchemy. Incluye validaciones para evitar duplicados, maneja errores y registra eventos importantes con logging. Las contraseñas se almacenan de forma segura usando hashing 

"""