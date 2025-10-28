# Guía de Deployment - Habit Tracker

## 📋 Resumen
- **Frontend (Angular)**: Netlify
- **Backend (FastAPI)**: Railway
- **Database (PostgreSQL)**: Neon

---

## 🚀 PASO 1: Desplegar el Frontend en Netlify

### 1.1 Conectar repositorio a Netlify
- Ve a [netlify.com](https://netlify.com)
- Haz clic en **"Connect to Git"**
- Selecciona GitHub y autoriza
- Selecciona tu repositorio `danbernal999/habit_tracker_app`

### 1.2 Configuración automática
Netlify debería detectar automáticamente:
- **Build command**: `cd frontend && npm install && npm run build`
- **Publish directory**: `frontend/dist/frontend`

### 1.3 Hacer deploy
- Haz clic en **"Deploy"**
- Espera a que termine (2-3 minutos)
- Tu frontend estará en: `https://tu-app.netlify.app`

**IMPORTANTE**: Guarda tu URL de Netlify para después

---

## 🚀 PASO 2: Desplegar el Backend en Railway

### 2.1 Conectar repositorio a Railway
- Ve a [railway.app](https://railway.app)
- Haz clic en **"Start a New Project"**
- Selecciona **"Deploy from GitHub"**
- Autoriza Railway a acceder a GitHub
- Selecciona tu repositorio `danbernal999/habit_tracker_app`

### 2.2 Railway detectará el Dockerfile automáticamente
- Comenzará a compilar la imagen
- Espera a que termine el primer deploy (5-10 minutos)

### 2.3 Configurar variables de entorno en Railway

Una vez desplegado, ve a la sección **"Variables"** en Railway y agrega:

#### Variable 1: `DATABASE_URL`
1. Ve a [console.neon.tech](https://console.neon.tech)
2. Selecciona tu proyecto de base de datos
3. Ve a **"Connection details"**
4. Copia la **Connection String** (debe empezar con `postgresql://`)
5. Pega en Railway como `DATABASE_URL`

Ejemplo:
```
postgresql://user:password@ep-xxxxx.us-east-1.neon.tech/dbname
```

#### Variable 2: `SECRET_KEY`
Genera una contraseña aleatoria y copia en Railway:
```
openssl rand -hex 32
```
(En Windows PowerShell, usa: `[convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($(Get-Random)))`
O simplemente pon un valor aleatorio largo: `abcd1234efgh5678ijkl9012mnop3456`)

### 2.4 Redeploy
- Después de agregar las variables, Railway se redesplegará automáticamente
- Espera a que termine
- Tu backend estará disponible en una URL como: `https://tu-proyecto-railway-xxxx.up.railway.app`

**IMPORTANTE**: Guarda tu URL de Railway para después

---

## 🔗 PASO 3: Conectar Frontend con Backend

### 3.1 Actualizar configuración del frontend

Edita `frontend/src/environments/environment.prod.ts`:

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://tu-proyecto-railway-xxxx.up.railway.app',  // ← Reemplaza con tu URL
};
```

### 3.2 Actualizar CORS del backend

Edita `app/main.py` y actualiza la lista de `allow_origins`:

```python
allow_origins=[
    "http://localhost",
    "http://localhost:4200",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "https://tu-app.netlify.app",  # ← Reemplaza con tu URL de Netlify
],
```

### 3.3 Hacer commit y push
```bash
git add .
git commit -m "Update deployment URLs"
git push origin main
```

Esto actualizará automáticamente:
- **Frontend** en Netlify (nuevo deploy)
- **Backend** en Railway (nuevo deploy)

---

## ✅ Verificación Final

### Frontend (Netlify)
- Abre `https://tu-app.netlify.app`
- Deberías ver tu aplicación Angular

### Backend (Railway)
- Abre `https://tu-proyecto-railway-xxxx.up.railway.app/health`
- Deberías ver: `{"status": "healthy"}`
- Abre `https://tu-proyecto-railway-xxxx.up.railway.app/docs`
- Deberías ver la documentación interactiva de FastAPI

### Conectividad
- En tu aplicación Angular, intenta crear un usuario o hábito
- Deberías ver que los datos se guardan en Neon

---

## 🐛 Troubleshooting

### Error en Railway: "DATABASE_URL no está configurada"
- Asegúrate de que la variable `DATABASE_URL` está en Railway
- Redeploy después de agregar la variable

### Error CORS: "Access-Control-Allow-Origin"
- Verifica que tu URL de Netlify está exacta en `app/main.py`
- Haz push y espera a que Railway redeploy

### El frontend no se conecta al backend
- Verifica la URL en `environment.prod.ts`
- Abre la consola del navegador (F12) y ve los errores de red
- Asegúrate que la URL de Railway no tiene `/` al final

---

## 📝 Notas importantes

- **Railway redeploy automático**: Cada vez que hagas push, Railway redeploy automáticamente
- **Netlify redeploy automático**: Igual que Railway
- **Base de datos**: Tu BD en Neon permanecerá intacta entre redeploy
- **Uploads**: Los archivos subidos se guardarán en Railway, pero se perderán si Railway reinicia. Para persistencia, necesitarías un storage como S3

---

¡Listo! Tu aplicación está lista para producción. 🎉