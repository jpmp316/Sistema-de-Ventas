# Datos de prueba Nexo

Periodo: 1 de agosto a 1 de noviembre de 2026, hora de Colombia.
50 productos, 5 categorías y 233 ventas. Importes en centavos de COP.

- categorias.json: cuerpos para POST /categories/, uno por solicitud.
- productos_50.json: cuerpos para POST /products/, uno por solicitud. Los category_id 1..5 son referencias de referencias_categorias.json, NO IDs consultados en Render. Sustituirlos por los IDs devueltos al crear o consultar categorías.
- catalogo_importacion.json: mismo catálogo con nombres de categoría para un importador que resuelva los IDs reales.
- ventas_3_meses.json: datos para IMPORTACIÓN HISTÓRICA, NO cuerpos válidos para POST /sales/. Usa product_code para resolver IDs reales y reference para deduplicación. La API actual ignora date y no acepta product_code: no pegar estos objetos en Swagger esperando conservar fechas.
- comprobacion_stock.json: saldo inicial, unidades vendidas y saldo final esperado. Tras importar todas las ventas quedan 10 productos sin stock, 10 con stock bajo, 10 en el mínimo, 10 normales y 10 abundantes.

El stock de productos_50.json es el INICIAL, antes de descontar estas ventas. Para obtener la distribución final hay que importar las ventas completas, sus detalles y movimientos dentro de transacciones, usando un usuario real y sin generar stock negativo. Fechar las entradas iniciales antes de la primera venta. No se ejecutó ninguna inserción ni se modificó la API. Un importador histórico debe resolver categorías y productos por nombre/código, conservar las fechas y prevenir duplicados; el sistema actual no incluye importación de estos JSON.

Crear productos desde Swagger registra entradas con fecha actual. Para mantener una cronología histórica completa es preferible importar catálogo, entradas y ventas juntos. Los ajustes y ventas existentes de tu negocio no se incluyen ni se alteran en estos archivos.
