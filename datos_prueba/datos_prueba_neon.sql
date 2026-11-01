-- NEXO: datos de prueba para PostgreSQL / Neon SQL Editor.
-- Requiere migraciones aplicadas y un administrador existente.
-- Ejecutar EL ARCHIVO COMPLETO en una misma sesión.
-- Crea 50 productos y 3 ventas/día desde hace 3 meses hasta hoy (Colombia).
-- No elimina datos existentes. Una segunda ejecución completa omite la carga.

BEGIN;

DO $nexo$
DECLARE
    v_admin integer;
    v_category integer;
    v_product integer;
    v_sale integer;
    v_before integer;
    v_price numeric(12,2);
    v_total numeric(12,2);
    v_count integer;
    v_today date := (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::date;
    v_start date := ((CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::date - INTERVAL '3 months')::date;
    v_initial timestamptz;
    r record;
    line record;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtext('nexo-trim-neon-demo-v1'));

    SELECT count(*) INTO v_count FROM products WHERE code LIKE 'NEXO-TRIM-%';
    IF v_count > 0 THEN
        IF v_count = 50 AND EXISTS (
            SELECT 1 FROM sales s JOIN sale_details d ON d.sale_id = s.id
            JOIN products p ON p.id = d.product_id WHERE p.code LIKE 'NEXO-TRIM-%'
        ) THEN
            RAISE NOTICE 'Ya existen los 50 productos y ventas demo. No se duplicaron ni modificaron.';
            RETURN;
        END IF;
        RAISE EXCEPTION 'Ya hay productos NEXO-TRIM- de otra carga. No se modificó nada. Usa una base de pruebas sin ese prefijo.';
    END IF;

    SELECT u.id INTO v_admin FROM users u JOIN roles role_row ON role_row.id = u.role_id
    WHERE role_row.name = 'admin' ORDER BY u.id LIMIT 1;
    IF v_admin IS NULL THEN
        RAISE EXCEPTION 'Primero crea un administrador desde POST /auth/bootstrap-admin. Después ejecuta este archivo completo.';
    END IF;

    CREATE TEMP TABLE nexo_product_plan (
        n integer PRIMARY KEY, code text, name text, category_name text,
        price_cents integer, final_stock integer, min_stock integer
    ) ON COMMIT DROP;

    INSERT INTO nexo_product_plan VALUES
    (1, 'NEXO-TRIM-001', 'Arroz 1 kg', 'Abarrotes', 580000, 0, 8),
    (2, 'NEXO-TRIM-002', 'Pasta 500 g', 'Abarrotes', 420000, 0, 8),
    (3, 'NEXO-TRIM-003', 'Aceite vegetal 1 L', 'Abarrotes', 1250000, 0, 8),
    (4, 'NEXO-TRIM-004', 'Azúcar 1 kg', 'Abarrotes', 480000, 0, 8),
    (5, 'NEXO-TRIM-005', 'Sal 500 g', 'Abarrotes', 180000, 0, 8),
    (6, 'NEXO-TRIM-006', 'Lentejas 500 g', 'Abarrotes', 390000, 0, 8),
    (7, 'NEXO-TRIM-007', 'Frijol 500 g', 'Abarrotes', 620000, 0, 8),
    (8, 'NEXO-TRIM-008', 'Harina de trigo 1 kg', 'Abarrotes', 450000, 0, 8),
    (9, 'NEXO-TRIM-009', 'Avena 500 g', 'Abarrotes', 560000, 0, 8),
    (10, 'NEXO-TRIM-010', 'Atún en lata 160 g', 'Abarrotes', 890000, 0, 8),
    (11, 'NEXO-TRIM-011', 'Agua 600 ml', 'Bebidas', 250000, 3, 8),
    (12, 'NEXO-TRIM-012', 'Agua 1.5 L', 'Bebidas', 420000, 4, 8),
    (13, 'NEXO-TRIM-013', 'Gaseosa cola 1.5 L', 'Bebidas', 650000, 1, 8),
    (14, 'NEXO-TRIM-014', 'Jugo de naranja 1 L', 'Bebidas', 690000, 3, 8),
    (15, 'NEXO-TRIM-015', 'Té frío 500 ml', 'Bebidas', 380000, 4, 8),
    (16, 'NEXO-TRIM-016', 'Bebida isotónica 500 ml', 'Bebidas', 520000, 1, 8),
    (17, 'NEXO-TRIM-017', 'Café molido 250 g', 'Bebidas', 1450000, 1, 8),
    (18, 'NEXO-TRIM-018', 'Chocolate de mesa 250 g', 'Bebidas', 980000, 1, 8),
    (19, 'NEXO-TRIM-019', 'Leche entera 1 L', 'Bebidas', 470000, 1, 8),
    (20, 'NEXO-TRIM-020', 'Bebida de avena 1 L', 'Bebidas', 1250000, 2, 8),
    (21, 'NEXO-TRIM-021', 'Detergente en polvo 1 kg', 'Aseo del hogar', 1320000, 8, 8),
    (22, 'NEXO-TRIM-022', 'Jabón de ropa 300 g', 'Aseo del hogar', 390000, 8, 8),
    (23, 'NEXO-TRIM-023', 'Lavaloza 500 ml', 'Aseo del hogar', 650000, 8, 8),
    (24, 'NEXO-TRIM-024', 'Desinfectante 1 L', 'Aseo del hogar', 720000, 8, 8),
    (25, 'NEXO-TRIM-025', 'Blanqueador 1 L', 'Aseo del hogar', 450000, 8, 8),
    (26, 'NEXO-TRIM-026', 'Suavizante 1 L', 'Aseo del hogar', 1080000, 8, 8),
    (27, 'NEXO-TRIM-027', 'Limpiavidrios 500 ml', 'Aseo del hogar', 820000, 8, 8),
    (28, 'NEXO-TRIM-028', 'Esponja multiuso', 'Aseo del hogar', 220000, 8, 8),
    (29, 'NEXO-TRIM-029', 'Bolsas de basura paquete', 'Aseo del hogar', 680000, 8, 8),
    (30, 'NEXO-TRIM-030', 'Papel higiénico 4 rollos', 'Aseo del hogar', 1150000, 8, 8),
    (31, 'NEXO-TRIM-031', 'Champú 400 ml', 'Cuidado personal', 1890000, 47, 8),
    (32, 'NEXO-TRIM-032', 'Acondicionador 400 ml', 'Cuidado personal', 1950000, 41, 8),
    (33, 'NEXO-TRIM-033', 'Jabón corporal 125 g', 'Cuidado personal', 350000, 42, 8),
    (34, 'NEXO-TRIM-034', 'Crema dental 100 ml', 'Cuidado personal', 890000, 33, 8),
    (35, 'NEXO-TRIM-035', 'Cepillo dental', 'Cuidado personal', 650000, 49, 8),
    (36, 'NEXO-TRIM-036', 'Desodorante 150 ml', 'Cuidado personal', 1580000, 49, 8),
    (37, 'NEXO-TRIM-037', 'Toallas higiénicas paquete', 'Cuidado personal', 920000, 56, 8),
    (38, 'NEXO-TRIM-038', 'Gel antibacterial 250 ml', 'Cuidado personal', 780000, 36, 8),
    (39, 'NEXO-TRIM-039', 'Protector solar 120 ml', 'Cuidado personal', 3250000, 58, 8),
    (40, 'NEXO-TRIM-040', 'Crema de manos 100 ml', 'Cuidado personal', 1250000, 38, 8),
    (41, 'NEXO-TRIM-041', 'Galletas de chocolate 150 g', 'Snacks', 480000, 144, 8),
    (42, 'NEXO-TRIM-042', 'Papas fritas 100 g', 'Snacks', 520000, 139, 8),
    (43, 'NEXO-TRIM-043', 'Maní salado 100 g', 'Snacks', 390000, 122, 8),
    (44, 'NEXO-TRIM-044', 'Barra de cereal', 'Snacks', 250000, 174, 8),
    (45, 'NEXO-TRIM-045', 'Chocolate 80 g', 'Snacks', 650000, 120, 8),
    (46, 'NEXO-TRIM-046', 'Gomitas 100 g', 'Snacks', 420000, 140, 8),
    (47, 'NEXO-TRIM-047', 'Palomitas 90 g', 'Snacks', 350000, 122, 8),
    (48, 'NEXO-TRIM-048', 'Galletas saladas 200 g', 'Snacks', 450000, 173, 8),
    (49, 'NEXO-TRIM-049', 'Platanitos 100 g', 'Snacks', 480000, 110, 8),
    (50, 'NEXO-TRIM-050', 'Mezcla de frutos secos 150 g', 'Snacks', 1280000, 129, 8);

    CREATE TEMP TABLE nexo_sale_plan ON COMMIT DROP AS
    SELECT row_number() OVER (ORDER BY d.day_offset, op.n)::integer AS n,
        CASE WHEN v_start + d.day_offset = v_today THEN
            (v_today::timestamp +
             ((CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota') - v_today::timestamp)
             * (op.n + 1) / 4.0) AT TIME ZONE 'America/Bogota'
        ELSE
            ((v_start + d.day_offset)::timestamp + INTERVAL '9 hours' + op.n * INTERVAL '3 hours')
            AT TIME ZONE 'America/Bogota'
        END AS date
    FROM generate_series(0, v_today - v_start) AS d(day_offset)
    CROSS JOIN generate_series(0, 2) AS op(n);

    CREATE TEMP TABLE nexo_line_plan ON COMMIT DROP AS
    SELECT s.n AS sale_n, ((s.n * 7 + l.n * 11) % 50) + 1 AS product_n,
           ((s.n + l.n) % 4) + 1 AS quantity
    FROM nexo_sale_plan s
    CROSS JOIN LATERAL generate_series(0, s.n % 3) AS l(n);

    -- Cada producto empieza con el stock necesario para vender y conservar
    -- el saldo final deseado: agotado, bajo, mínimo, normal o abundante.
    v_initial := v_start::timestamp AT TIME ZONE 'America/Bogota';
    FOR r IN SELECT p.*, p.final_stock + COALESCE((
        SELECT sum(l.quantity) FROM nexo_line_plan l WHERE l.product_n = p.n
    ), 0)::integer AS initial_stock FROM nexo_product_plan p ORDER BY p.n LOOP
        SELECT id INTO v_category FROM categories
        WHERE lower(name) = lower(r.category_name) LIMIT 1;
        IF v_category IS NULL THEN
            INSERT INTO categories(name, is_active, created_at, updated_at)
            VALUES(r.category_name, true, v_initial, v_initial) RETURNING id INTO v_category;
        END IF;
        INSERT INTO products(name, code, category_id, description, price_cents,
                             stock, min_stock, is_active, created_at, updated_at)
        VALUES(r.name, r.code, v_category, 'Producto de prueba Nexo', r.price_cents,
               r.initial_stock, r.min_stock, true, v_initial, v_initial)
        RETURNING id INTO v_product;
        IF r.initial_stock > 0 THEN
            INSERT INTO inventory_movements(product_id, user_id, sale_id, type,
                       quantity, previous_stock, resulting_stock, date)
            VALUES(v_product, v_admin, NULL, 'entry', r.initial_stock, 0, r.initial_stock, v_initial);
        END IF;
    END LOOP;

    FOR r IN SELECT * FROM nexo_sale_plan ORDER BY n LOOP
        INSERT INTO sales(user_id, date, subtotal, total, status)
        VALUES(v_admin, r.date, 0, 0, 'completed') RETURNING id INTO v_sale;
        v_total := 0;
        FOR line IN SELECT l.quantity, p.code FROM nexo_line_plan l
                    JOIN nexo_product_plan p ON p.n = l.product_n
                    WHERE l.sale_n = r.n ORDER BY p.n LOOP
            SELECT id, stock, price_cents::numeric / 100 INTO v_product, v_before, v_price
            FROM products WHERE code = line.code FOR UPDATE;
            IF v_before < line.quantity THEN
                RAISE EXCEPTION 'Stock insuficiente para %. Se revierte toda la carga.', line.code;
            END IF;
            INSERT INTO sale_details(sale_id, product_id, quantity, unit_price, subtotal)
            VALUES(v_sale, v_product, line.quantity, v_price, v_price * line.quantity);
            UPDATE products SET stock = stock - line.quantity, updated_at = r.date WHERE id = v_product;
            INSERT INTO inventory_movements(product_id, user_id, sale_id, type,
                       quantity, previous_stock, resulting_stock, date)
            VALUES(v_product, v_admin, v_sale, 'sale', line.quantity, v_before, v_before - line.quantity, r.date);
            v_total := v_total + v_price * line.quantity;
        END LOOP;
        UPDATE sales SET subtotal = v_total, total = v_total WHERE id = v_sale;
    END LOOP;

    IF EXISTS (SELECT 1 FROM nexo_product_plan plan JOIN products p ON p.code = plan.code
               WHERE p.stock <> plan.final_stock) THEN
        RAISE EXCEPTION 'El saldo final no coincide. Se revierte toda la carga.';
    END IF;
    IF EXISTS (SELECT 1 FROM nexo_sale_plan WHERE date > CURRENT_TIMESTAMP) THEN
        RAISE EXCEPTION 'No se permiten ventas futuras. Se revierte toda la carga.';
    END IF;
    SELECT count(*) INTO v_count FROM nexo_sale_plan;
    RAISE NOTICE 'Carga completada: 50 productos, % ventas, detalles y movimientos. Periodo % a %.', v_count, v_start, v_today;
END;
$nexo$;

COMMIT;

-- Verificación: saldos finales de los 50 productos de esta carga.
SELECT code, name, stock, min_stock,
       CASE WHEN stock = 0 THEN 'Agotado'
            WHEN stock < min_stock THEN 'Bajo'
            WHEN stock = min_stock THEN 'En el mínimo'
            WHEN stock < 100 THEN 'Normal'
            ELSE 'Abundante' END AS nivel
FROM products WHERE code LIKE 'NEXO-TRIM-%' ORDER BY code;

-- Verificación: cantidad y total de las ventas asociadas al catálogo demo.
SELECT count(*) AS ventas, min(date) AS primera_venta, max(date) AS ultima_venta,
       sum(total) AS ingresos_cop
FROM sales s WHERE EXISTS (
    SELECT 1 FROM sale_details d JOIN products p ON p.id = d.product_id
    WHERE d.sale_id = s.id AND p.code LIKE 'NEXO-TRIM-%'
);
