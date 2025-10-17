#  Cargador Masivo Excel - Documentación Completa

##  Descripción

Aplicación web moderna que permite subir archivos Excel (.xls o .xlsx), procesarlos en el backend con FastAPI, guardar los datos en PostgreSQL usando SQLAlchemy, y mostrar en el frontend una barra de progreso en tiempo real (de 0 a 100%) usando WebSockets.

##  Arquitectura

```
habit_tracker/
├── app/
│   ├── main.py                # Aplicación principal FastAPI
│   ├── database/
│   │   └── config.py          # Configuración de base de datos
│   ├── models/
│   │   └── models.py          # Modelos SQLAlchemy (incluye ExcelData)
│   └── routers/
│       └── excel_routes.py    # Endpoints y WebSocket para Excel
├── frontend_excel/
│   └── index.html             # Frontend con TailwindCSS
├── uploads/                   # Carpeta para archivos temporales
├── requirements.txt           # Dependencias Python
└── ejemplo_excel.py           # Script para generar Excel de prueba
```

##  Instalación y Configuración

### 1. Instalar Dependencias

```bash
# Activar el entorno virtual (si no está activado)
source venv/bin/activate  # En Linux/Mac
# o
.\venv\Scripts\activate   # En Windows

# Instalar las nuevas dependencias
pip install pandas openpyxl aiomysql websockets
```

### 2. Configurar Base de Datos

El proyecto ya está configurado para usar PostgreSQL. Asegúrarse de que el archivo `.env` tenga las variables correctas:

```env
DB_USER=habit_user
DB_PASSWORD=123456
DB_NAME=habit_tracker_db
```

### 3. Crear las Tablas

Las tablas se crean automáticamente al iniciar la aplicación. El modelo `ExcelData` se agregó a `models.py`:

```python
class ExcelData(Base):
    __tablename__ = "excel_data"
    
    id = Column(Integer, primary_key=True, index=True)
    column1 = Column(String(255), nullable=True)
    column2 = Column(String(255), nullable=True)
    column3 = Column(String(255), nullable=True)
    column4 = Column(String(255), nullable=True)
    column5 = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    file_name = Column(String(255), nullable=True)
```

**Nota:** Se Puede personalizar los nombres de las columnas según el tipo de Excel.

##  Uso de la Aplicación

### 1. Iniciar el Servidor

```bash
# Desde la raíz del proyecto
uvicorn app.main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

### 2. Acceder al Cargador de Excel

Abre tu navegador y ve a:

```
http://localhost:8000/static/index.html
```

### 3. Generar un Excel de Ejemplo

```bash
# Ejecutar el script para crear un archivo de prueba
python ejemplo_excel.py
```

Esto creará un archivo `datos_ejemplo.xlsx` con 10 filas de datos de prueba.

comando docker ->
docker compose exec backend python ejemplo_excel.py

### 4. Subir el Archivo

1. **Arrastra y suelta** el archivo Excel en la zona indicada, o haz clic en "Seleccionar Archivo"
2. Haz clic en el botón **"Subir Excel"**
3. Observa la **barra de progreso** que se actualiza en tiempo real
4. Cuando termine, verás un mensaje de éxito con el número de filas procesadas

##  Endpoints de la API

### POST `/excel/upload_excel`

Sube y procesa un archivo Excel.

**Request:**
- `Content-Type: multipart/form-data`
- `file`: Archivo Excel (.xls o .xlsx)

**Response (200 OK):**
```json
{
  "message": "Archivo procesado exitosamente",
  "filename": "datos_ejemplo.xlsx",
  "rows_processed": 10,
  "columns": ["Nombre", "Email", "Edad", "Ciudad", "Teléfono"]
}
```

**Response (400 Bad Request):**
```json
{
  "error": "El archivo debe ser .xls o .xlsx"
}
```

### WebSocket `/excel/ws/progress`

Conexión WebSocket para recibir actualizaciones de progreso en tiempo real.

**Mensaje recibido:**
```json
{
  "progress": 45.5,
  "status": "processing"
}
```

Cuando el progreso llega al 100%:
```json
{
  "progress": 100.0,
  "status": "completed"
}
```

### GET `/excel/progress`

Endpoint alternativo para obtener el progreso actual (sin WebSocket).

**Response:**
```json
{
  "progress": 75.0,
  "status": "processing"
}
```

### GET `/excel/data`

Obtiene los datos cargados desde Excel con paginación.

**Query Parameters:**
- `limit` (opcional): Número de registros a devolver (default: 100)
- `offset` (opcional): Número de registros a saltar (default: 0)

**Response:**
```json
{
  "total": 100,
  "limit": 10,
  "offset": 0,
  "data": [
    {
      "id": 1,
      "column1": "Juan Pérez",
      "column2": "juan@example.com",
      "column3": "25",
      "column4": "Madrid",
      "column5": "600111222",
      "file_name": "datos_ejemplo.xlsx",
      "uploaded_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### DELETE `/excel/data`

Elimina todos los datos cargados (útil para pruebas).

**Response:**
```json
{
  "message": "Datos eliminados exitosamente",
  "deleted_count": 100
}
```

##  Personalización

### Adaptar el Modelo a tu Excel

Si tu archivo Excel tiene columnas específicas, modifica el modelo `ExcelData` en `app/models/models.py`:

```python
class ExcelData(Base):
    __tablename__ = "excel_data"
    
    id = Column(Integer, primary_key=True, index=True)
    # Reemplaza estos campos con los nombres de tus columnas
    nombre = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    edad = Column(Integer, nullable=True)
    ciudad = Column(String(255), nullable=True)
    telefono = Column(String(50), nullable=True)
    # Metadatos
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    file_name = Column(String(255), nullable=True)
```

Luego, actualiza el código en `excel_routes.py` para mapear las columnas correctamente:

```python
# En lugar de usar row.iloc[0], usa el nombre de la columna
excel_record = ExcelData(
    nombre=str(row['Nombre']),
    email=str(row['Email']),
    edad=int(row['Edad']),
    ciudad=str(row['Ciudad']),
    telefono=str(row['Teléfono']),
    file_name=file.filename,
    uploaded_at=datetime.utcnow()
)
```

### Ajustar la Velocidad de Procesamiento

En `excel_routes.py`, puedes modificar la velocidad de procesamiento:

```python
# Hacer commit cada N filas
if rows_inserted % 10 == 0:  # Cambia 10 por el número que prefieras
    db.commit()
    await asyncio.sleep(0.1)  # Ajusta el tiempo de espera
```

### Cambiar el Puerto del Servidor

```bash
uvicorn app.main:app --reload --port 8080
```

No olvides actualizar las URLs en `index.html`:

```javascript
const response = await fetch('http://localhost:8080/excel/upload_excel', {
    method: 'POST',
    body: formData
});

websocket = new WebSocket('ws://localhost:8080/excel/ws/progress');
```

##  Pruebas

### Probar con cURL

```bash
# Subir un archivo
curl -X POST "http://localhost:8000/excel/upload_excel" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@datos_ejemplo.xlsx"

# Obtener el progreso
curl "http://localhost:8000/excel/progress"

# Obtener los datos cargados
curl "http://localhost:8000/excel/data?limit=5&offset=0"

# Eliminar todos los datos
curl -X DELETE "http://localhost:8000/excel/data"
```

### Probar el WebSocket con JavaScript

```javascript
const ws = new WebSocket('ws://localhost:8000/excel/ws/progress');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(`Progreso: ${data.progress}%`);
};
```

##  Flujo de Datos

```
1. Usuario selecciona archivo Excel
   ↓
2. Frontend envía archivo vía POST /excel/upload_excel
   ↓
3. Backend guarda archivo temporalmente
   ↓
4. Pandas lee el Excel y obtiene las filas
   ↓
5. Backend procesa fila por fila:
   - Inserta en base de datos
   - Actualiza variable de progreso
   - Hace commit cada N filas
   ↓
6. WebSocket envía progreso al frontend cada segundo
   ↓
7. Frontend actualiza barra de progreso en tiempo real
   ↓
8. Al terminar, muestra mensaje de éxito
```

##  Características del Frontend

-  **Drag & Drop**: Arrastra archivos directamente
-  **Validación**: Solo acepta archivos .xls y .xlsx
-  **Barra de progreso animada**: Con gradiente y transiciones suaves
-  **WebSocket en tiempo real**: Actualizaciones cada segundo
-  **Diseño responsive**: Se adapta a móviles y tablets
-  **Mensajes de estado**: Éxito, error y procesando
-  **TailwindCSS**: Diseño moderno y profesional

##  Consideraciones de Seguridad

1. **Validación de archivos**: Solo se aceptan archivos Excel
2. **Tamaño máximo**: Considera agregar un límite de tamaño
3. **Sanitización de datos**: Los datos se convierten a string antes de guardar
4. **Archivos temporales**: Se guardan en la carpeta `uploads/`
5. **CORS**: Configurado para localhost (ajusta en producción)

##  Despliegue en Producción

### Consideraciones

1. **Variables de entorno**: Usa variables de entorno para configuración sensible
2. **Base de datos**: Asegúrate de que PostgreSQL esté configurado correctamente
3. **WebSocket**: Algunos proxies pueden bloquear WebSockets (configura Nginx/Apache)
4. **Archivos estáticos**: Considera usar un CDN para TailwindCSS
5. **Múltiples workers**: Usa Redis para compartir el progreso entre workers

### Ejemplo con Gunicorn

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

##  Notas Adicionales

- El modelo `ExcelData` es genérico con 5 columnas. Personalízalo según tus necesidades.
- El progreso se almacena en memoria. Para múltiples workers, usa Redis.
- Los archivos se guardan temporalmente en `uploads/`. Considera limpiarlos periódicamente.
- El WebSocket se cierra automáticamente cuando el cliente se desconecta.

##  Solución de Problemas

### Error: "DATABASE_URL no está configurada"

Asegúrate de que tu archivo `.env` tenga la variable `DATABASE_URL` o las variables `DB_USER`, `DB_PASSWORD` y `DB_NAME`.

### Error: "No module named 'pandas'"

Instala las dependencias:
```bash
pip install pandas openpyxl
```

### El WebSocket no se conecta

Verifica que:
1. El servidor esté corriendo en el puerto correcto
2. No haya un firewall bloqueando WebSockets
3. La URL del WebSocket sea correcta (`ws://` no `http://`)

### La barra de progreso no se actualiza

1. Abre la consola del navegador (F12) y busca errores
2. Verifica que el WebSocket esté conectado
3. Asegúrate de que el archivo tenga suficientes filas para ver el progreso

##  Recursos

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

##  ¡Listo!

La aplicación de Cargador Masivo Excel está lista para usar. Disfruta procesando archivos Excel con progreso en tiempo real. 