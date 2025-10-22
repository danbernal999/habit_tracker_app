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
    prefix="/users",  # Ya incluye /users
    tags=["users"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Constantes
SECRET_KEY = "keysecreta"  # CAMBIAR ESTO en producción
ALGORITHM = "HS256"
MAX_PASSWORD_LENGTH = 72


def get_password_hash(password: str):
    """Hashear contraseña con validación de longitud"""
    # Validar longitud mínima
    if len(password) < 8:
        logger.warning("Contraseña demasiado corta")
        raise HTTPException(
            status_code=400, 
            detail="La contraseña debe tener al menos 8 caracteres"
        )
    
    # Truncar a 72 bytes para bcrypt
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > MAX_PASSWORD_LENGTH:
        password = password_bytes[:MAX_PASSWORD_LENGTH].decode("utf-8", errors="ignore")
        logger.info("Contraseña truncada a 72 bytes")
    
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña con truncamiento consistente"""
    # Truncar de la misma forma que al hashear
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > MAX_PASSWORD_LENGTH:
        plain_password = password_bytes[:MAX_PASSWORD_LENGTH].decode("utf-8", errors="ignore")
    
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)  # Cambiado de "/users/" a "/"
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo usuario.
    - **username**: Nombre de usuario único
    - **email**: Correo electrónico único
    - **password**: Contraseña del usuario (mínimo 8 caracteres)
    """
    try:
        logger.info(f"Intentando crear usuario: {user.username} ({user.email})")
        
        # Verificar si el email ya existe
        existing_email = db.query(models.User).filter(models.User.email == user.email).first()
        if existing_email:
            logger.warning(f"Correo ya registrado: {user.email}")
            raise HTTPException(status_code=400, detail="Correo ya registrado")
        
        # Verificar si el username ya existe
        existing_username = db.query(models.User).filter(models.User.username == user.username).first()
        if existing_username:
            logger.warning(f"Usuario ya registrado: {user.username}")
            raise HTTPException(status_code=400, detail="Usuario ya registrado")
        
        # Crear el usuario 
        hashed_password = get_password_hash(user.password)  # La función ya maneja el truncamiento
        
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
        logger.error(f"❌ Error al crear usuario: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Autenticar usuario y retornar un token JWT.
    - **email**: Correo electrónico del usuario
    - **password**: Contraseña del usuario
    """
    try:
        logger.info(f"🔐 Intentando autenticar usuario: {user.email}")
        
        # Buscar usuario por email
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        
        if not db_user:
            logger.warning(f"Usuario no encontrado: {user.email}")
            raise HTTPException(status_code=401, detail="Credenciales inválidas")  #  Cambiado a 401
        
        logger.info(f"✓ Usuario encontrado: {db_user.email}")
        
        # Verificar contraseña con la función que trunca correctamente
        password_valid = verify_password(user.password, db_user.hashed_password)  # 👈 Usa verify_password
        
        if not password_valid:
            logger.warning(f"❌ Contraseña incorrecta para: {user.email}")
            raise HTTPException(status_code=401, detail="Credenciales inválidas")  # 👈 Cambiado a 401
        
        # Crear token JWT
        token_data = {
            "sub": db_user.email,
            "user_id": db_user.id,
            "username": db_user.username
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        logger.info(f"Usuario autenticado exitosamente: {user.email}")
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al autenticar usuario: {str(e)}")
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
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        logger.info(f"Usuario encontrado: {user.username}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener usuario: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    


    
""" 
El archivo define rutas para crear usuarios, obtener todos los usuarios y obtener un usuario por ID usando FastAPI y SQLAlchemy. Incluye validaciones para evitar duplicados, maneja errores y registra eventos importantes con logging. Las contraseñas se almacenan de forma segura usando hashing 

"""