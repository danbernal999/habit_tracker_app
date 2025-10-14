# 🎯 Habit Tracker

Aplicación full-stack para seguimiento de hábitos con backend en FastAPI y frontend en Angular.

### Tecnologías

### Backend
- FastAPI
- SQLAlchemy
- SQLite
- Docker & Docker Compose
- Python 3.11

### Frontend
- Angular 19
- Tailwind CSS
- Dark Mode Design

### Instalación

### Backend

1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/habit-tracker.git
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

### Frontend

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
ng serve
```

La aplicación estará disponible en: `http://localhost:4200`

## 📁 Estructura del Proyecto
```
habit_tracker/
├── app/                      # Backend (FastAPI)
│   ├── models/              # Modelos de base de datos
│   ├── schemas/             # Schemas de Pydantic
│   ├── routers/             # Endpoints de la API
│   └── database/            # Configuración de BD
├── frontend/                # Frontend (Angular)
│   └── src/
│       └── app/
│           └── components/  # Componentes de Angular
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

## 🎨 Features

- ✅ CRUD completo de usuarios y hábitos
- ✅ Registro de completado diario
- ✅ Diseño Dark Mode
- ✅ API REST documentada
- ✅ Docker containerizado
- ✅ Manejo de errores y logging

## 📝 API Endpoints

- `POST /users/` - Crear usuario
- `GET /users/` - Listar usuarios
- `POST /habits/` - Crear hábito
- `GET /habits/` - Listar hábitos
- `POST /records/` - Registrar completado
- `GET /records/habit/{habit_id}` - Ver historial

## 🔒 Licencia

MIT