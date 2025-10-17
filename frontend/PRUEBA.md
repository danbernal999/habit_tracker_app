#  Guía Rápida - Habit Tracker

##  Resumen de Cambios

He realizado los siguientes cambios en mi proyecto:

###  NUEVO: Cargador Excel Integrado en Angular

**Antes:** El cargador estaba en una página HTML separada (`frontend_excel/index.html`)  
**Ahora:** Es un componente Angular completo accesible en `/excel-loader` después del login

###  Archivos Creados

1. **`frontend/src/app/services/excel.ts`**
   - Servicio para operaciones Excel
   - Maneja subida, progreso WebSocket, gestión de archivos

2. **`frontend/src/app/components/excel-loader/`**
   - `excel-loader.ts` - Componente TypeScript
   - `excel-loader.html` - Template con todas las funcionalidades
   - `excel-loader.css` - Estilos

###  Archivos Modificados

1. **`app/routers/user_routes.py`**
   -  Agregado: `from jose import JWTError, jwt`
   -  Corregido: Ahora el login funciona correctamente

2. **`frontend/src/app/app.routes.ts`**
   -  Agregada ruta: `/excel-loader`

3. **`frontend/src/app/components/navbar/navbar.html`**
   -  Agregado link: "Excel" en la navegación

---

##  Plan de Pruebas

### Paso 1: Iniciar Backend 

```powershell
# Terminal 1 - Backend
cd \wsl.localhost\Ubuntu\home\danbernal\habit_tracker

# Activar entorno virtual (si no lo está)
venv\Scripts\activate

# Ejecutar servidor FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Debe mostrar:**
```
Uvicorn running on http://0.0.0.0:8000
```

### Paso 2: Iniciar Frontend 

```powershell
# Terminal 2 - Frontend
cd \wsl.localhost\Ubuntu\home\danbernal\habit_tracker\frontend

# Ejecutar servidor Angular
ng serve
```

**Debe mostrar:**
```
✔ Compiled successfully.
Application bundle generated successfully.
```

### Paso 3: Probar Login 

1. **Abre:** http://localhost:4200
2. **Verás:** Pantalla de login
3. **Opción A - Registrar usuario nuevo:**
   ```
   Username: testuser
   Email: test@example.com
   Contraseña: Test1234!
   ```
   - Click en "Register"
   - Deberías ver éxito

4. **Opción B - Login:**
   ```
   Email: test@example.com
   Contraseña: Test1234!
   ```
   - Click en "Login"
   - **Deberías ser redirigido al Dashboard**

### Paso 4: Navegar a Excel Loader 

1. **En el Dashboard**, ve a la **Navbar** (parte superior)
2. **Click en "📊 Excel"**
3. **Deberías ver:**
   - Sección de carga (Drag & Drop)
   - Pestaña "Gestionar Archivos"
   - Interfaz completa con Tailwind CSS

### Paso 5: Probar Cargador Excel 

1. **Crear archivo Excel de prueba:**
   - Abre Excel o LibreOffice Calc
   - Crea una tabla con datos:
     ```
     | column1 | column2 | column3 |
     |---------|---------|---------|
     | Dato 1  | Dato 2  | Dato 3  |
     | Dato 4  | Dato 5  | Dato 6  |
     ```
   - Guarda como `prueba.xlsx`

2. **Subir archivo:**
   - Ve al componente Excel Loader
   - Arrastra `prueba.xlsx` o click "Seleccionar Archivo"
   - Click "Subir Excel"

3. **Ver progreso:**
   - Observa la **barra de progreso en tiempo real** (WebSocket)
   - Debe llegar al 100%

4. **Ver datos:**
   - Click en "Gestionar Archivos"
   - Verás la tabla con los datos cargados
   - Funciona paginación

---

## 🔍 Verificación Rápida

### Verificar que el JWT está funcionando

```bash
# Terminal 3 - Test de API
curl -X POST http://localhost:8000/users/ -H "Content-Type: application/json" -d '{"username":"test2","email":"test2@example.com","password":"Test1234!"}' 2>&1 | python -m json.tool

curl -X POST http://localhost:8000/users/login -H "Content-Type: application/json" -d '{"email":"test2@example.com","password":"Test1234!"}' 2>&1 | python -m json.tool
```

**Esperado:** Obtendre un `access_token`

### Verificar WebSocket (Progreso Excel)

En la consola del navegador (F12), cuando subas un archivo:
```javascript
// Debería ver mensajes como:
// {progress: 25, status: "processing"}
// {progress: 50, status: "processing"}
// {progress: 100, status: "completed"}
```

---

## 📋 Checklist Final

- [ ] Backend corriendo (puerto 8000)
- [ ] Frontend corriendo (puerto 4200)
- [ ] Puedes registrar un usuario
- [ ] Puedes hacer login
- [ ] Se abre el Dashboard después del login
- [ ] Aparece "Excel" en la navbar
- [ ] Puedes acceder a `/excel-loader`
- [ ] Puedes subir un archivo Excel
- [ ] Ves la barra de progreso (0-100%)
- [ ] Los datos aparecen en "Gestionar Archivos"
- [ ] Puedes descargar el archivo
- [ ] Puedes eliminar el archivo

---

##  Si Algo No Funciona

### Error 1: "ModuleNotFoundError: No module named 'jose'"
**Solución:**
```bash
pip install python-jose cryptography
```

### Error 2: "WebSocket connection failed"
**Solución:** Verificar que el backend está corriendo

### Error 3: "No es posible conectar con localhost:8000"
**Solución:** 
```bash
# Matar proceso en puerto 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Reiniciar backend
uvicorn app.main:app --reload
```

### Error 4: "Credenciales inválidas" en login
**Solución:** Verificar que:
- El usuario fue registrado correctamente
- Usas el email correcto
- La contraseña tiene al menos 8 caracteres

---

##  Estructura de Archivos (Cambios)

```
frontend/src/app/
├── components/
│   ├── excel-loader/                NUEVO
│   │   ├── excel-loader.ts
│   │   ├── excel-loader.html
│   │   └── excel-loader.css
│   └── navbar/
│       └── navbar.html              MODIFICADO (agregado link Excel)
├── services/
│   ├── excel.ts                     NUEVO
│   ├── auth.ts
│   └── ...
└── app.routes.ts                    MODIFICADO (agregada ruta)
```

---

##  Próximas Mejoras Sugeridas

1. **Protección de rutas:**
   - Crear guard que valide token JWT
   - Redirigir a login si no hay token

2. **Carga de usuario:**
   - Mostrar nombre del usuario en navbar
   - Información del perfil

3. **Validaciones adicionales:**
   - Validar tamaño máximo de archivo
   - Validar formato de Excel

4. **Base de datos:**
   - Usar PostgreSQL en producción (no SQLite)
   - Migraciones automáticas

---
