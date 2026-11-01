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

`VITE_API_BASE_URL` apunta a la API FastAPI. Inicia sesión en la pantalla de
acceso; el JWT se conserva en `sessionStorage` durante esa sesión del navegador.

El administrador accede a todos los módulos y crea cuentas de vendedores desde
Usuarios. El vendedor entra directamente a Ventas y solo ve Ventas e Inventario.
Puede consultar el catálogo para armar el carrito, registrar ventas, consultar
el historial y detalle de ventas del negocio, y revisar sus movimientos de
inventario. El historial continúa siendo compartido entre los usuarios del negocio.

Las contraseñas nuevas o modificadas deben tener entre 8 y 128 caracteres e
incluir mayúscula, minúscula, número y símbolo. La API valida esta regla al crear
usuarios, usar bootstrap-admin y cambiar contraseñas. El inicio de sesión admite
las contraseñas ya existentes y el almacenamiento sigue usando hash Argon2.

La API verifica el rol actual en PostgreSQL en cada solicitud autenticada. Solo
el administrador puede gestionar usuarios, productos y categorías o consultar
reportes. Las consultas del catálogo, las ventas y los movimientos requieren un
rol admin o vendedor. El bootstrap permite crear el primer administrador sin
sesión; cuando existen usuarios exige un administrador autenticado. Al cerrar
sesión se llama a `POST /auth/logout` y se borra la sesión local.

El detalle de venta muestra el responsable y los productos con su código,
cantidad, precio unitario, subtotal y total. Los importes se conservan desde la
venta; los nombres y códigos reflejan el catálogo actual. Esta actualización no
requiere una migración nueva; el logout requiere tener aplicada la migración
`0005_revoked_tokens` existente (`alembic upgrade head` desde `backend/`).

Al crear un producto con existencias, la API registra una entrada inicial desde
cero. Al editar sus existencias registra un ajuste por la diferencia, conservando
el usuario responsable, la fecha y los saldos anterior y posterior. Guardar el
mismo stock, cambiar otros campos o activar/desactivar no genera movimientos.
El stock y el movimiento se guardan en una misma transacción. En Inventario los
ajustes se distinguen como entrada o salida; en Estadísticas los ajustes suman el
volumen de unidades modificadas en ambos sentidos, no el balance neto.
Este registro aplica a operaciones nuevas realizadas mediante la API: no
reconstruye cambios antiguos ni captura modificaciones hechas directamente por SQL.

## Pruebas

Desde `backend/`:

```powershell
python -m pytest
```

Las pruebas usan SQLite en memoria, crean y eliminan un esquema aislado por
prueba y nunca reutilizan `DATABASE_URL`. `TEST_DATABASE_URL` solo acepta una
URL SQLite en memoria; si se configura una base PostgreSQL o un archivo SQLite,
la suite falla antes de importar la aplicación.

El Dashboard permite seleccionar Hoy, 7, 30 o 90 días. Los periodos y la
agrupación de ventas por día usan la hora de Colombia (UTC-5); Hoy empieza a
las 00:00 y termina en el momento de la consulta.

El vendedor dispone de Mi contraseña en el sidebar. El formulario requiere la
contraseña actual, una nueva contraseña válida y su confirmación. La API
`POST /auth/change-password` identifica la cuenta mediante el JWT y no acepta
un identificador de otro usuario. Cambiar la contraseña conserva la sesión
actual; los próximos inicios de sesión requieren la nueva contraseña.
