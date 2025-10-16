"""
Router para el Cargador Masivo de Excel
Este módulo maneja la carga de archivos Excel, procesamiento con pandas,
inserción en base de datos y comunicación en tiempo real vía WebSocket.
"""

import os
import asyncio
from typing import Dict
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import pandas as pd

from app.database.config import get_db
from app.models.models import ExcelData

# Inicializo el router con un prefijo y etiqueta para organizar los endpoints
router = APIRouter(prefix="/excel", tags=["Excel Upload"])

# Directorio donde se guardarán temporalmente los archivos subidos
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Variable global para almacenar el progreso actual (0-100)
# En producción, considera usar Redis o una base de datos para múltiples workers
upload_progress: Dict[str, float] = {"current": 0.0}


@router.post("/upload_excel")
async def upload_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint POST para subir un archivo Excel (.xls o .xlsx).
    
    Flujo:
    1. Valida que el archivo sea Excel
    2. Guarda el archivo temporalmente
    3. Lee el Excel con pandas
    4. Procesa e inserta las filas en la base de datos
    5. Actualiza el progreso en tiempo real
    
    Args:
        file: Archivo Excel subido por el usuario
        db: Sesión de base de datos (inyectada por FastAPI)
    
    Returns:
        JSON con el resultado del proceso
    """
    
    # Reinicio el progreso al iniciar una nueva carga
    upload_progress["current"] = 0.0
    
    # Valido que el archivo sea Excel
    if not file.filename.endswith(('.xls', '.xlsx')):
        return JSONResponse(
            status_code=400,
            content={"error": "El archivo debe ser .xls o .xlsx"}
        )
    
    # Guardo el archivo temporalmente en el servidor
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # Leo el contenido del archivo y lo guardo
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Leo el Excel con pandas
        # pandas detecta automáticamente el formato (.xls o .xlsx)
        df = pd.read_excel(file_path)
        
        # Obtengo el número total de filas para calcular el progreso
        total_rows = len(df)
        
        if total_rows == 0:
            return JSONResponse(
                status_code=400,
                content={"error": "El archivo Excel está vacío"}
            )
        
        # Proceso cada fila del DataFrame
        rows_inserted = 0
        
        for index, row in df.iterrows():
            # Creo un nuevo registro en la base de datos
            # NOTA: Adapta los nombres de las columnas según tu Excel
            # Aquí asumo que el Excel tiene 5 columnas
            excel_record = ExcelData(
                column1=str(row.iloc[0]) if len(row) > 0 else None,
                column2=str(row.iloc[1]) if len(row) > 1 else None,
                column3=str(row.iloc[2]) if len(row) > 2 else None,
                column4=str(row.iloc[3]) if len(row) > 3 else None,
                column5=str(row.iloc[4]) if len(row) > 4 else None,
                file_name=file.filename,
                uploaded_at=datetime.utcnow()
            )
            
            # Agrego el registro a la sesión
            db.add(excel_record)
            rows_inserted += 1
            
            # Actualizo el progreso (porcentaje completado)
            upload_progress["current"] = (rows_inserted / total_rows) * 100
            
            # Hago commit cada 10 filas para mejorar el rendimiento
            # y permitir que el WebSocket envíe actualizaciones
            if rows_inserted % 10 == 0:
                db.commit()
                # Pequeña pausa para simular procesamiento y permitir actualizaciones
                await asyncio.sleep(0.1)
        
        # Commit final para las filas restantes
        db.commit()
        
        # Marco el progreso como completado
        upload_progress["current"] = 100.0
        
        # Elimino el archivo temporal (opcional)
        # os.remove(file_path)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Archivo procesado exitosamente",
                "filename": file.filename,
                "rows_processed": rows_inserted,
                "columns": list(df.columns)
            }
        )
    
    except Exception as e:
        # En caso de error, reinicio el progreso
        upload_progress["current"] = 0.0
        
        # Elimino el archivo si existe
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return JSONResponse(
            status_code=500,
            content={"error": f"Error al procesar el archivo: {str(e)}"}
        )


@router.websocket("/ws/progress")
async def websocket_progress(websocket: WebSocket):
    """
    WebSocket para enviar el progreso de carga en tiempo real.
    
    El cliente se conecta a este endpoint y recibe actualizaciones
    del progreso cada segundo mientras se procesa el archivo.
    
    Flujo:
    1. Cliente se conecta al WebSocket
    2. Servidor acepta la conexión
    3. Servidor envía el progreso actual cada segundo
    4. Cliente actualiza la barra de progreso en tiempo real
    """
    
    # Acepto la conexión del WebSocket
    await websocket.accept()
    
    try:
        # Bucle infinito para enviar actualizaciones
        while True:
            # Obtengo el progreso actual
            progress = upload_progress["current"]
            
            # Envío el progreso al cliente en formato JSON
            await websocket.send_json({
                "progress": round(progress, 2),
                "status": "processing" if progress < 100 else "completed"
            })
            
            # Si el progreso llegó al 100%, puedo cerrar la conexión
            # o mantenerla abierta para futuras cargas
            if progress >= 100:
                await asyncio.sleep(1)  # Espero 1 segundo antes de cerrar
                # Opcional: cerrar la conexión
                # break
            
            # Espero 1 segundo antes de enviar la siguiente actualización
            await asyncio.sleep(1)
    
    except WebSocketDisconnect:
        # El cliente cerró la conexión
        print("Cliente desconectado del WebSocket")
    
    except Exception as e:
        # Error en el WebSocket
        print(f"Error en WebSocket: {str(e)}")
        await websocket.close()


@router.get("/progress")
async def get_progress():
    """
    Endpoint GET alternativo para obtener el progreso actual.
    Útil para clientes que no soportan WebSockets.
    
    Returns:
        JSON con el progreso actual (0-100)
    """
    return {
        "progress": round(upload_progress["current"], 2),
        "status": "processing" if upload_progress["current"] < 100 else "completed"
    }


@router.get("/data")
async def get_excel_data(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Endpoint GET para obtener los datos cargados desde Excel.
    Soporta paginación con limit y offset.
    
    Args:
        limit: Número máximo de registros a devolver (default: 100)
        offset: Número de registros a saltar (default: 0)
        db: Sesión de base de datos
    
    Returns:
        JSON con los datos cargados
    """
    
    # Consulto los datos con paginación
    records = db.query(ExcelData)\
        .order_by(ExcelData.uploaded_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()
    
    # Cuento el total de registros
    total = db.query(ExcelData).count()
    
    # Convierto los registros a diccionarios
    data = []
    for record in records:
        data.append({
            "id": record.id,
            "column1": record.column1,
            "column2": record.column2,
            "column3": record.column3,
            "column4": record.column4,
            "column5": record.column5,
            "file_name": record.file_name,
            "uploaded_at": record.uploaded_at.isoformat() if record.uploaded_at else None
        })
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": data
    }


@router.delete("/data")
async def delete_all_data(db: Session = Depends(get_db)):
    """
    Endpoint DELETE para eliminar todos los datos cargados.
    Útil para limpiar la base de datos durante pruebas.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        JSON con el número de registros eliminados
    """
    
    try:
        # Cuento los registros antes de eliminar
        count = db.query(ExcelData).count()
        
        # Elimino todos los registros
        db.query(ExcelData).delete()
        db.commit()
        
        return {
            "message": "Datos eliminados exitosamente",
            "deleted_count": count
        }
    
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"error": f"Error al eliminar datos: {str(e)}"}
        )