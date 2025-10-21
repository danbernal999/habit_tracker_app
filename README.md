# Habit Tracker

Aplicación full-stack para seguimiento de hábitos con backend en FastAPI y frontend en Angular.

### Tecnologías

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- uvicorn
- pyjwt
- python-dotenv
- requests
- pytest
- alembic
- Docker & Docker Compose
- Python 3.11

### Frontend
- Angular 16
- TypeScript
- Tailwind CSS

### Instalación

Para ejecutar este proyecto, necesitas tener instalados Docker y Docker Compose.

### Backend

1. Clonar el repositorio
```bash
git clone https://github.com/danbernal999/habit_tracker_app.git
cd habit-tracker
```

2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con los valores
```

3. Ejecutar con Docker
```bash
docker compose build --no-cache
docker-compose up -d
docker-compose -f


docker compose down -v
```

La API estará disponible en: `http://localhost:8000`
Documentación: `http://localhost:8000/docs`

### Frontend (Angular 16)

1. Ir a la carpeta frontend
```bash
cd frontend
```

2. Instalar dependencias
```bash
npm install
```

3. Ejecutar servidor de desarrollo
```bash
npm start
# O alternativa:
ng serve
```

La aplicación estará disponible en: `http://localhost:4200`

4. Build para producción
```bash
npm run build
# Genera archivos optimizados en: dist/frontend/browser/
```

## Estructura del Proyecto
```
habit_tracker/
├── app/                      # Backend (FastAPI)
│   ├── models/              # Modelos de base de datos
│   ├── schemas/             # Schemas de Pydantic
│   ├── routers/             # Endpoints de la API
│   └── database/            # Configuración de BD
├── frontend/                # Frontend (Angular + tailwind + CSS)
│   └── src/
│       └── app/
│           └── components/  # Componentes de Angular
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
└── .env.example
```

##  Features

- ✅ CRUD completo de usuarios y hábitos
- ✅ Registro de completado diario
- ✅ Diseño Dark Mode
- ✅ API REST documentada
- ✅ Docker containerizado
- ✅ Manejo de errores y logging

##  API Endpoints

- `POST /users/` - Crear usuario
- `GET /users/` - Listar usuarios
- `POST /habits/` - Crear hábito
- `GET /habits/` - Listar hábitos
- `POST /records/` - Registrar completado
- `GET /records/habit/{habit_id}` - Ver historial

## 🚀 Deployment

### Local con Docker Compose

```bash
# Full stack (Backend + Frontend + Database)
docker-compose up -d

# Frontend: http://localhost:4200
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### AWS S3 (Frontend estático)

```bash
# Generar build optimizado
cd frontend && npm run build

# Subir a S3 (requiere AWS CLI)
./deploy-s3.sh
```

### AWS EC2 (Full Stack)

```bash
# Deployment automático
./deploy-ec2.sh <IP_INSTANCIA>
```

**Ver [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) para instrucciones detalladas**

## ⚙️ Configuración

### Backend (.env)

```bash
# Copiar template
cp .env.example .env

# Editar con tus valores:
# - DATABASE_URL
# - SECRET_KEY
# - CORS settings
```

### Frontend

Las URLs del backend se configuran en:
- Desarrollo: `frontend/src/environments/environment.ts`
- Producción: `frontend/src/environments/environment.prod.ts`

##  Licencia

MIT