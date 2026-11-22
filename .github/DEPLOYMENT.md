# Despliegue de Nexo desde GitHub Actions

El workflow conserva los checks obligatorios `Backend tests` y `Frontend checks`.
Al actualizar main, ambos deben aprobar antes de ejecutar `Deploy Render` y
`Deploy Vercel`. Los dos despliegues se ejecutan en paralelo y pueden terminar
independientemente. Un fallo en uno no revierte el otro.

## 1. Crear el entorno de GitHub

En el repositorio, abre Settings > Environments > New environment y crea
`production`. En Deployment branches and tags selecciona Selected branches and
tags y permite la rama `main`.

Agrega estos cinco Environment secrets mediante Add environment secret:

| Nombre | Valor |
| --- | --- |
| RENDER_API_KEY | API key de Render con permisos para iniciar y consultar despliegues del servicio |
| RENDER_SERVICE_ID | ID del backend, con formato srv-... |
| VERCEL_TOKEN | Token de acceso de Vercel para el proyecto existente |
| VERCEL_ORG_ID | ID del equipo o cuenta propietaria del proyecto |
| VERCEL_PROJECT_ID | ID del proyecto frontend existente |

No pegues los valores en el YAML ni en un commit.

## 2. Obtener los datos de Render

En Render, abre Account Settings > API keys y crea una clave para el workspace
que contiene Nexo. Permite crear y consultar despliegues. El ID del servicio
aparece en la URL de su dashboard, como srv- seguido de su identificador.

Revisa que el servicio siga conectado a este repositorio y a main, con Root
Directory backend. Sus variables DATABASE_URL, SECRET_KEY y CORS_ORIGINS deben
seguir configuradas en Render.

En Settings del servicio cambia Auto-Deploy a Off, antes de fusionar este cambio.
Así Actions controla cuándo inicia el despliegue.

El script usa GITHUB_SHA para desplegar el commit probado y consulta Render hasta
que el despliegue está live, falla o supera 25 minutos. Si una petición inicial
expira, revisa Render antes de repetirla porque podría haber creado el despliegue.
El Dockerfile actual ejecuta Alembic al arrancar, por lo que el despliegue también
aplicará las migraciones pendientes de ese commit.

## 3. Obtener los datos de Vercel

Crea VERCEL_TOKEN en https://vercel.com/account/tokens para el equipo propietario.
El Project ID se consulta en Settings > General del proyecto. El ID del equipo
se consulta en sus ajustes. Si necesitas obtener ambos desde la CLI, ejecuta
`npx vercel link` desde C:\proyecto-inventario y selecciona el proyecto EXISTENTE.
Los campos orgId y projectId aparecen en .vercel/project.json.

En el proyecto verifica Root Directory = frontend, framework Vite, y la variable
VITE_API_BASE_URL de Production con la URL HTTPS real de FastAPI.
Guarda VITE_API_BASE_URL como tipo Config (Sensitive desactivado). Vercel no
permite recuperar valores Secret mediante pull y devuelve un marcador como
[SENSITIVE]. Vite incluiría ese marcador en el JavaScript público y el login
fallaría con 404. El workflow valida esta variable antes de construir.
El job descarga esa configuración antes de construir. La URL api.nexo.test del
job de pruebas es exclusiva de las pruebas.

En Settings > Git > Connected Git Repository pulsa Disconnect para dejar a
Actions a cargo del despliegue. Conserva el mismo proyecto, sus dominios y variables.
Este paso debe completarse antes del merge para evitar despliegues paralelos
que se adelanten a las pruebas.

Los comandos de Vercel se ejecutan desde la raíz del repositorio y utilizan el
Root Directory frontend del proyecto. No cambies el working-directory a frontend
mientras ese sea el Root Directory configurado.

## 4. Subir y verificar

Crea una rama, agrega el workflow, este documento, deploy_render.py y el cambio
de .gitignore. Haz commit, sube la rama y abre un PR hacia main.

En el PR se ejecutan las pruebas. Los despliegues quedan skipped. Conserva como
checks obligatorios únicamente Backend tests y Frontend checks.

Después del merge, Actions ejecuta las pruebas sobre main y muestra los trabajos
de despliegue. Render solo termina verde al llegar a live. Vercel espera el
despliegue prebuilt y publica la URL en sus logs. Comprueba login y una consulta
de productos en el dominio público al terminar la primera ejecución.

Si falta un secreto o un servicio falla, el trabajo queda rojo. Configura el dato
faltante y usa Re-run failed jobs en esa ejecución. Si ya existe un commit más
nuevo en producción, evita repetir un despliegue antiguo porque reemplaza esa versión.

## Referencias

- https://api-docs.render.com/reference/create-deploy
- https://api-docs.render.com/reference/retrieve-deploy
- https://render.com/docs/api
- https://render.com/docs/deploys
- https://vercel.com/kb/guide/how-can-i-use-github-actions-with-vercel
- https://vercel.com/docs/project-configuration/git-settings
