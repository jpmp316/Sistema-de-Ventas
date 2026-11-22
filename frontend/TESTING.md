# Pruebas de comportamiento del frontend

## Ejecución

Desde la carpeta frontend, con Node compatible con Vite (22.12 o superior):

```powershell
npm ci
npm test
npm run test:watch
npm run test:coverage
```

Para ejecutar un archivo o escenario concreto:

```powershell
npm test -- src/test/products.test.jsx
npm test -- -t "código duplicado"
```

La cobertura HTML queda en coverage/index.html. Vitest devuelve un código distinto
de cero si falla un escenario o la cobertura baja de los mínimos configurados.
Los mínimos iniciales son 75% de líneas y sentencias, 70% de ramas y funciones.
Son una protección contra regresiones, no una medida de calidad por sí solos.

## Qué prueba cada archivo

- auth.test.jsx cubre login, errores, pantalla inicial según rol, recuperación de
  sesión, navegación del vendedor y logout aunque falle la red.
- products.test.jsx cubre carga, búsqueda, creación, edición con código inmutable,
  errores de duplicados, estados, paginación, reintento y validaciones del formulario.
- modules.test.jsx cubre el carrito, cantidades, límites de stock, confirmación,
  bloqueo de doble envío, errores, detalle de venta, usuarios, contraseña,
  inventario y cambios de periodo en dashboard y estadísticas.
- api.test.js comprueba la interpretación de 422, 503 y respuestas 204.
- helpers.jsx reúne datos de prueba, renderizado con AuthProvider y StrictMode,
  y un sustituto de fetch con rutas conocidas.
- setup.js limpia DOM, sessionStorage y mocks entre escenarios. También adapta
  scrollIntoView y ResizeObserver, que jsdom no implementa como un navegador real.

## Cómo está diseñada la suite

Los componentes, hooks, api.js y AuthContext se ejecutan de verdad. Solo fetch
se sustituye por respuestas controladas. Cada prueba puede definir una respuesta
exitosa, un error HTTP, una desconexión o una promesa pendiente. La URL de prueba
es https://api.nexo.test y las pruebas no necesitan credenciales ni un backend.

Cada escenario sigue Dado / Cuando / Entonces:

1. Dado un catálogo y una sesión, renderizamos la pantalla.
2. Cuando la persona escribe o pulsa un botón, interactuamos con user-event.
3. Entonces comprobamos el mensaje, la fila, el total o el estado visible del botón.

getByRole y getByLabelText buscan elementos por el modo en que una persona los
identifica. findBy espera contenido que aparece después de una consulta.
queryBy permite comprobar ausencias. within limita una búsqueda a una tabla,
fila o zona concreta. waitFor espera una condición asincrónica.
Todas las interacciones de user-event se esperan con await.

Las comprobaciones de peticiones complementan el comportamiento visible cuando
importa el contrato, por ejemplo que editar un producto omita code.
No comprobamos nombres de estados, llamadas a setters ni clases CSS.

Los casos de precio y stock inválidos usan el formulario y la validación HTML
real de jsdom. Las reglas de seguridad también deben comprobarse en el backend
con su propia suite. Ocultar navegación solo verifica el comportamiento del frontend.

## Añadir un escenario

Usa un nombre que describa la acción y el resultado. Reutiliza renderAuthenticated
para una pantalla que necesita sesión. Configura api con la respuesta esperada y
espera el resultado visible. Para un estado pendiente, conserva la función resolve
de una promesa y resuélvela dentro del mismo test. Así se puede comprobar que un
botón queda deshabilitado sin depender de pausas artificiales.

Las rutas desconocidas y el fetch sin configurar fallan deliberadamente.
Al añadir un endpoint, agrega explícitamente su respuesta al escenario o al helper.
Los datos del helper representan respuestas HTTP de prueba y no se importan desde
la aplicación.

## Alcance

jsdom permite comprobar comportamiento del DOM. El diseño responsive, los colores,
las dimensiones y las interacciones gráficas de Recharts requieren pruebas en un
navegador real. Esta suite comprueba los indicadores y cambios de periodo.
Tampoco verifica persistencia PostgreSQL ni la autorización del servidor.

Se incluyen las fuentes JS/JSX de src en el informe, con exclusión del arranque
main.jsx y la infraestructura de pruebas. Revisa también los archivos sin cobertura
al ampliar la suite. El HTML permite localizar ramas pendientes.

## Documentación de referencia

- https://vitest.dev/guide/
- https://testing-library.com/docs/react-testing-library/setup/
- https://testing-library.com/docs/user-event/intro/
