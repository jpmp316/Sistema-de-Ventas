# Pruebas del backend

Desde backend y con el entorno virtual activado:

```powershell
python -m pytest -q
python -m pytest -q --durations=10
python -m pytest tests/test_sale_integrity.py -v
```

## Aislamiento

conftest.py exige SQLite en memoria y rechaza PostgreSQL y archivos SQLite.
Sobrescribe DATABASE_URL antes de importar la aplicación. Los tests de seguridad
de la configuración comprueban ese rechazo en procesos separados.
Cada prueba recibe su propio engine y esquema. Dispose libera toda la base al
terminar. No hace falta borrar usuarios o productos mediante endpoints.
Las claves foráneas están activadas para comprobar la integridad referencial.
Los roles se crean al preparar el esquema y get_db se sustituye durante cada test.

## Organización

- test_users y test_user_management cubren cuentas, roles y restricciones de borrado.
- test_auth_security cubre JWT, revocación, hash y protección del bootstrap.
- test_products cubre catálogo y categorías.
- test_stock_movements comprueba entradas iniciales y ajustes manuales.
- test_sales y test_sale_integrity cubren ventas, precisión monetaria y atomicidad.
- test_seller_permissions verifica las operaciones autorizadas por rol.
- test_queries_and_validation comprueba paginación, filtros y datos inválidos.
- test_password_validation y test_self_password_and_today cubren contraseñas y fechas.
- test_average_ticket comprueba importes, redondeo y ventas completadas por periodo.
- test_test_database_safety comprueba que pytest rechace bases no aisladas.

product_factory crea productos mediante la API y valida el resultado durante el
setup. Permite cambiar únicamente los datos relevantes de cada escenario.

Los tests de rollback provocan errores de escritura con eventos SQLAlchemy y
retiran los listeners mediante finally. Después comprueban la base con una sesión
nueva y verifican que una petición posterior pueda completarse.

## Límites

SQLite no reproduce los bloqueos SELECT FOR UPDATE de PostgreSQL. Las pruebas
comprueban rollback y atomicidad ante errores, pero la concurrencia de ventas
y las migraciones necesitan una base PostgreSQL de pruebas dedicada.
La configuración actual bloquea expresamente usar PostgreSQL desde esta suite.

Los filtros de inventario actuales interpretan los días en UTC. Los reportes
usan la zona horaria de Colombia. Los tests reflejan ambas implementaciones.

No se sustituyen los hashes por versiones rápidas de prueba. La autenticación
se ejecuta por HTTP con las dependencias reales, salvo la sesión de base de datos.
