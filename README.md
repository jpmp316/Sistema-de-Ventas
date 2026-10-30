# Sistema de Ventas

Backend de inventario construido con FastAPI, SQLAlchemy y PostgreSQL. El código
del backend está en `backend/`; la interfaz React existente está en `frontend/`.

## Requisitos

- Python 3.10 o posterior.
- PostgreSQL disponible localmente o en un servidor accesible.
- PowerShell en los ejemplos de Windows (adapta la activación del entorno para
  otros sistemas operativos).

## Instalación y configuración del backend

Desde la raíz del repositorio:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item ..\.env.example .env
```

Edita `backend/.env` con la URL real de PostgreSQL. Genera una clave JWT nueva:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Pega el resultado en `SECRET_KEY`. La aplicación no arranca si falta esa clave o
si tiene menos de 32 caracteres. No publiques `.env` ni reutilices la clave de
ejemplo.

## Base de datos y migraciones

Con PostgreSQL iniciado y la base de datos configurada en `DATABASE_URL`, aplica
el esquema inicial:

```powershell
alembic upgrade head
```

La revisión inicial crea `users` y `products`; la segunda crea `categories`,
agrega a productos el código, la relación `category_id`, el stock mínimo y el
estado activo, y rellena los productos existentes con valores compatibles. No
se ejecutaron migraciones sobre PostgreSQL durante la preparación de este
proyecto.

Las rutas autenticadas de categorías son `GET/POST /categories/`,
`PUT /categories/{id}` y `DELETE /categories/{id}`. Una categoría no se puede
eliminar mientras tenga productos asociados. La migración crea la categoría
inicial «Sin categoría» para los productos que ya existían.

Si la base de datos ya tiene el esquema anterior (`users` y `products`, antes
de añadir los campos de catálogo), compara sus columnas, índices y restricciones
con `backend/migrations/versions/0001_initial_schema.py` y haz un respaldo. Si
coincide y aún no tiene historial de Alembic, registra esa revisión existente y
aplica después la migración aditiva:

```powershell
alembic stamp 0001_initial_schema
alembic upgrade head
```

No uses `stamp head` en esa situación: omitiría la migración que añade los campos
del catálogo.

Para un cambio futuro de modelos, desde `backend/`:

```powershell
alembic revision --autogenerate -m "describe el cambio"
```

Revisa y ajusta el archivo generado, incluyendo `downgrade`, antes de aplicarlo
con `alembic upgrade head`. No apliques una migración a una base compartida sin
revisar su SQL y contar con un respaldo.

## Ejecutar el backend

Desde `backend/`, después de configurar la base de datos y aplicar migraciones:

```powershell
uvicorn main:app --reload
```

La documentación interactiva de la API estará en `http://127.0.0.1:8000/docs`.
Los orígenes CORS locales predeterminados son `http://localhost:5173` y
`http://127.0.0.1:5173`; configúralos en `CORS_ORIGINS` separados por comas.

## Conectar el frontend

En otra terminal, desde la raíz:

```powershell
Copy-Item frontend\.env.example frontend\.env.local
cd frontend
npm install
npm run dev
```

`VITE_API_BASE_URL` apunta a la API FastAPI. En el módulo Productos inicia sesión
con un usuario ya creado en el backend; el JWT se conserva en `sessionStorage`
durante esa sesión del navegador.

## Pruebas

Desde `backend/`:

```powershell
python -m pytest
```

Las pruebas usan SQLite en memoria, crean y eliminan un esquema aislado por
prueba y nunca reutilizan `DATABASE_URL`. `TEST_DATABASE_URL` solo acepta una
URL SQLite en memoria; si se configura una base PostgreSQL o un archivo SQLite,
la suite falla antes de importar la aplicación.
