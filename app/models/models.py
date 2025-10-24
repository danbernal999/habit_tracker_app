from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.config import Base

# NOTA: Se ha añadido una longitud de 255 a todos los campos String. 
# Esto es crucial para la correcta creación de tablas en PostgreSQL.

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False) # Añadido nullable=False
    email = Column(String(255), unique=True, index=True, nullable=False)   # Añadido nullable=False
    # La longitud de 255 asegura que el hash de bcrypt (aprox. 60 caracteres) cabe sin problema
    hashed_password = Column(String(255), nullable=False)                 # Añadido nullable=False
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    habits = relationship("Habit", back_populates="owner")
    notifications = relationship("Notification", back_populates="user")

class Habit(Base):
    __tablename__ = "habits"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    description = Column(String(255))
    frequency = Column(String(50)) # daily, weekly, monthly
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    owner = relationship("User", back_populates="habits")
    records = relationship("Record", back_populates="habit")

class Record(Base):
    __tablename__ = "records"
    
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    date = Column(Date, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    notes = Column(String(255), nullable=True) # Se mantiene nullable=True y se añade longitud
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    habit = relationship("Habit", back_populates="records")



# Modelo para almacenar datos cargados desde Excel
class ExcelData(Base):
    __tablename__ = "excel_data"
    
    id = Column(Integer, primary_key=True, index=True)
    # Campos genéricos que pueden adaptarse según tu Excel
    # Ejemplo: si Excel tiene columnas como "nombre", "email", "edad", etc.
    column1 = Column(String(255), nullable=True)  
    column2 = Column(String(255), nullable=True)
    column3 = Column(String(255), nullable=True)
    column4 = Column(String(255), nullable=True)
    column5 = Column(String(255), nullable=True)
    # Metadatos del registro
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    file_name = Column(String(255), nullable=True)  # Nombre del archivo de origen


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    message = Column(String(255), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="notifications")
