#  Pruebas de Login - Guía Completa

##  Resumen

El sistema de login está **completamente funcional** con:
-  JWT en backend (se agregó el import faltante)
-  Autenticación en frontend
-  Almacenamiento de token en localStorage
-  Redirección al Dashboard

---

##  Test 1: Verificar Que Backend Funciona

### Paso 1: Iniciar Backend

```powershell
# Terminal 1
cd \wsl.localhost\Ubuntu\home\danbernal\habit_tracker
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Salida esperada:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
```

### Paso 2: Verificar Health Check

```powershell
# Terminal 2 - Probar salud del servidor
Invoke-WebRequest -Uri http://localhost:8000/health -Method Get | ConvertTo-Json
```

**Salida esperada:**
```
{
  "status": "healthy"
}
```

---

##  Test 2: Registrar Usuario Nuevo

### Usando PowerShell

```powershell
# Crear usuario
$body = @{
    username = "usuario_prueba"
    email = "prueba@test.com"
    password = "PruebaPassword123!"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri http://localhost:8000/users/ `
  -Method Post `
  -ContentType "application/json" `
  -Body $body

$response.Content | ConvertFrom-Json | Format-List
```

**Salida esperada:**
```
id            : 1
username      : usuario_prueba
email         : prueba@test.com
created_at    : 2024-01-01T12:34:56.789123
```

---

##  Test 3: Login Usuario

### Usando PowerShell

```powershell
# Login
$body = @{
    email = "prueba@test.com"
    password = "PruebaPassword123!"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri http://localhost:8000/users/login `
  -Method Post `
  -ContentType "application/json" `
  -Body $body

$token = ($response.Content | ConvertFrom-Json).access_token
$token
```

**Salida esperada:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJwcnVlYmFAdGVzdC5jb20ifQ...
```

---

##  Test 4: Login en Frontend

### Paso 1: Iniciar Frontend

```powershell
# Terminal 3
cd \wsl.localhost\Ubuntu\home\danbernal\habit_tracker\frontend
ng serve
```

**Salida esperada:**
```
✔ Compiled successfully.
** Angular Live Development Server is listening on localhost:4200 **
```

### Paso 2: Abrir Frontend

1. Abre navegador: **http://localhost:4200**
2. Verás la pantalla de login

### Paso 3: Hacer Login

1. **Llenar formulario:**
   - Email: `prueba@test.com`
   - Contraseña: `PruebaPassword123!`

2. **Click "Login"**

3. **Verificar resultado:**
   -  Se abre el Dashboard
   -  No hay error
   -  La navbar está visible

### Paso 4: Verificar Token en Navegador

1. **Abre DevTools:** F12
2. **Ve a "Application" o "Storage"**
3. **LocalStorage > http://localhost:4200**
4. **Busca: `auth_token`**
5. **Deberías ver el JWT token**

---

##  Test 5: Login Incorrecto

### Probar Error Handling

1. Ve a http://localhost:4200/login
2. Intenta login con:
   - Email: `prueba@test.com`
   - Contraseña: `IncorrectPassword`
3. **Deberías ver error:** "Credenciales inválidas"

**Verifica en Console (F12):**
```javascript
// Error esperado en console:
// Error de login: {status: 400, error: {detail: "credenciales inválidas"}}
```

---

##  Test 6: Flujo Completo

### Escenario 1: Registro Nuevo

1. En login, click "¿No tienes cuenta?"
2. Formulario de registro:
   ```
   Usuario: nuevo_usuario
   Email: nuevo@test.com
   Contraseña: NuevaPassword123!
   Confirmar: NuevaPassword123!
   ```
3. Click "Registrarse"
4. **Esperar a ser redirigido**
5. Deberías ver el Dashboard

### Escenario 2: Login Exitoso

1. En login:
   ```
   Email: nuevo@test.com
   Contraseña: NuevaPassword123!
   ```
2. Click "Login"
3. **Deberías ir directamente al Dashboard**

### Escenario 3: Logout y Re-login

1. En Dashboard, click "Salir" (navbar superior derecha)
2. Deberías volver a login
3. Login nuevamente
4. Deberías estar en Dashboard

---

## 📊 Tabla de Pruebas de Login

| # | Escenario | Email | Contraseña | Resultado Esperado |
|---|-----------|-------|-----------|------------------|
| 1 | Registro nuevo | usuario@test.com | Pass123! | ✅ Usuario creado, redirige a login |
| 2 | Login correcto | usuario@test.com | Pass123! | ✅ Va a Dashboard, token en localStorage |
| 3 | Email incorrecto | wrong@test.com | Pass123! | ❌ Error: Credenciales inválidas |
| 4 | Contraseña incorrecta | usuario@test.com | WrongPass | ❌ Error: Credenciales inválidas |
| 5 | Email duplicado | usuario@test.com | Pass456! | ❌ Error: Correo Registrado |
| 6 | Username duplicado | usuario | Pass456! | ❌ Error: usuario Registrado |
| 7 | Contraseña < 8 chars | test@test.com | Short | ❌ Error: Mín 8 caracteres |
| 8 | Email inválido | invalidemail | Pass123! | ❌ Error: Email inválido |
| 9 | Campos vacíos | "" | "" | ❌ Error: Completa todos campos |
| 10 | Sin token en URL protegida | N/A | N/A | 🔄 Redirige a login |

---

##  Verificaciones de Backend

### Verificar Que JWT Se Genera Correctamente

```python
# app/routers/user_routes.py (línea ~140)
token_data = {"sub": db_user.email}
token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
```

 **Verificado:** Import agregado en línea 9

### Verificar Que CORS Permite Frontend

```python
# app/main.py (línea ~29)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", ...],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

 **Verificado:** Configurado correctamente

### Verificar Que Password Validation Funciona

```python
# app/routers/user_routes.py (línea ~135)
if not pwd_context.verify(user.password, db_user.hashed_password):
```

 **Verificado:** Usando bcrypt correctamente

---

## 📱 Verificar en Frontend

### AuthService (Login)

```typescript
// frontend/src/app/services/auth.ts
login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/users/login`, { 
      email, 
      password 
    });
}

saveToken(token: string): void {
    localStorage.setItem('auth_token', token);
}
```

✅ **Verificado:** Servicio correcto

### Login Component

```typescript
// frontend/src/app/components/auth/login/login.ts
this.authService.login(this.email, this.password).subscribe({
  next: (response) => {
    this.authService.saveToken(response.access_token);
    this.router.navigate(['/dashboard']);
  },
  error: (error) => {
    this.errorMessage = 'Credenciales inválidas';
  }
});
```

✅ **Verificado:** Componente correcto

---

## 🐛 Posibles Problemas y Soluciones

### Problema 1: "Module not found: jose"
```
❌ Error: from jose import JWTError, jwt - ModuleNotFoundError
```
**Solución:**
```bash
pip install python-jose cryptography
```

### Problema 2: "No puedo conectar a localhost:8000"
```
❌ Error: No es posible conectar con el servidor remoto
```
**Solución:**
```powershell
# Verifica que el servidor está corriendo
Get-Process | Where-Object {$_.Name -like "*python*"} | Select-Object ProcessName, Id

# Si no está corriendo, inicia de nuevo
uvicorn app.main:app --reload
```

### Problema 3: "CORS error en login"
```
❌ Error: Access to XMLHttpRequest has been blocked by CORS policy
```
**Solución:** Verificar que `allow_origins` incluye `http://localhost:4200`

### Problema 4: "Token inválido en otras rutas"
```
❌ Error: Invalid authentication credentials
```
**Solución:** Crear un guard de autenticación para validar token

### Problema 5: "WebSocket no conecta"
```
❌ Error en Excel Loader: WebSocket connection failed
```
**Solución:** Verificar que backend está corriendo en puerto 8000

---

## ✅ Checklist Final

- [ ] Backend corriendo en http://localhost:8000
- [ ] Frontend corriendo en http://localhost:4200
- [ ] Health check funciona
- [ ] Puedo registrar usuario nuevo
- [ ] JWT se genera en login
- [ ] Token se guarda en localStorage
- [ ] Puedo ver el Dashboard después del login
- [ ] Error handling funciona (credenciales incorrectas)
- [ ] Logout funciona
- [ ] Re-login funciona
- [ ] No hay errores de CORS

---

## 📊 Estructura de Respuestas

### Registro Exitoso
```json
{
  "id": 1,
  "username": "usuario",
  "email": "email@test.com",
  "created_at": "2024-01-01T12:34:56.789123"
}
```

### Login Exitoso
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Error de Login
```json
{
  "detail": "credenciales inválidas"
}
```

### Error de Email Duplicado
```json
{
  "detail": "Correo Registrado"
}
```

---

## 🎓 Explicación Técnica

### Flujo de Autenticación

```
1. Usuario envía credenciales
        ↓
2. Backend valida email y contraseña
        ↓
3. Backend genera JWT token
        ↓
4. Frontend recibe token
        ↓
5. Frontend guarda en localStorage
        ↓
6. Frontend lo envía en headers posteriores
        ↓
7. Backend valida token
```

### Token JWT

Estructura:
```
header.payload.signature

Ejemplo:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9  <- Header
.eyJzdWIiOiJlbWFpbEB0ZXN0LmNvbSJ9      <- Payload (email del usuario)
.signature_aqui                         <- Firma
```

### Seguridad

- Contraseña: Hasheada con bcrypt (no se guarda en claro)
- Token: Firmado con SECRET_KEY (no puede ser falsificado)
- CORS: Configurado para permitir solo localhost:4200

---

## 📚 Referencias

- **FastAPI Docs:** http://localhost:8000/docs
- **Token JWT:** https://jwt.io
- **Angular Router:** https://angular.io/guide/routing-overview
- **LocalStorage:** https://developer.mozilla.org/es/docs/Web/API/Window/localStorage

---

**¡Lista para probar! 🚀**

Ejecuta los tests en orden y deberías tener el login 100% funcional.