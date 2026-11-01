"""Insert deterministic demo catalog and sales into the configured PostgreSQL DB.

Run from backend: python scripts/seed_demo_data.py
Requires an existing admin account. Demo records use the NEXO-DEMO code prefix.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from core.database import SessionLocal
from models.category import Category
from models.product import Product
from models.role import Role
from models.sales import InventoryMovement, Sale, SaleDetail
from models.user import User


def main() -> None:
    db: Session = SessionLocal()
    try:
        admin = db.query(User).join(Role).filter(Role.name == "admin").order_by(User.id).first()
        if admin is None:
            raise RuntimeError("Crea o conserva una cuenta admin antes de sembrar los datos.")

        category_names = ["Demo Abarrotes", "Demo Bebidas", "Demo Aseo"]
        categories = {}
        for name in category_names:
            category = db.query(Category).filter(Category.name == name).first()
            if category is None:
                category = Category(name=name)
                db.add(category)
                db.flush()
            categories[name] = category

        definitions = [
            ("Arroz demo 1kg", "NEXO-DEMO-ARROZ", "Demo Abarrotes", 5800, 70, 10),
            ("Pasta demo 500g", "NEXO-DEMO-PASTA", "Demo Abarrotes", 4200, 45, 8),
            ("Aceite demo 1L", "NEXO-DEMO-ACEITE", "Demo Abarrotes", 12500, 32, 6),
            ("Agua demo 600ml", "NEXO-DEMO-AGUA", "Demo Bebidas", 2500, 80, 15),
            ("Jugo demo 1L", "NEXO-DEMO-JUGO", "Demo Bebidas", 6900, 28, 7),
            ("Jabón demo", "NEXO-DEMO-JABON", "Demo Aseo", 3900, 25, 5),
        ]
        products = {}
        for name, code, category_name, cents, stock, minimum in definitions:
            product = db.query(Product).filter(Product.code == code).first()
            if product is None:
                product = Product(name=name, code=code, category=categories[category_name], price_cents=cents,
                                  stock=stock, min_stock=minimum, is_active=True)
                db.add(product)
                db.flush()
            products[code] = product
        db.commit()

        demo_ids = [product.id for product in products.values()]
        existing_demo_sales = db.query(Sale.id).join(SaleDetail).filter(SaleDetail.product_id.in_(demo_ids)).first()
        if existing_demo_sales:
            print("Catálogo demo disponible; ya existen ventas demo, no se duplicaron.")
            return

        patterns = [("NEXO-DEMO-ARROZ", 2), ("NEXO-DEMO-AGUA", 3), ("NEXO-DEMO-PASTA", 1),
                    ("NEXO-DEMO-JUGO", 2), ("NEXO-DEMO-ACEITE", 1), ("NEXO-DEMO-JABON", 2)]
        now = datetime.now(timezone.utc)
        for index in range(21):
            date = now - timedelta(days=20-index, hours=(index * 3) % 12)
            chosen = [patterns[index % len(patterns)]]
            if index % 3 == 0:
                chosen.append(patterns[(index + 2) % len(patterns)])
            lines = []
            amount = Decimal("0.00")
            for code, quantity in chosen:
                product = products[code]
                before = product.stock
                unit = Decimal(product.price_cents) / Decimal(100)
                line_total = unit * quantity
                product.stock -= quantity
                amount += line_total
                lines.append((product, quantity, unit, line_total, before))
            sale = Sale(user_id=admin.id, date=date, subtotal=amount, total=amount, status="completed")
            db.add(sale)
            db.flush()
            for product, quantity, unit, line_total, before in lines:
                db.add(SaleDetail(sale_id=sale.id, product_id=product.id, quantity=quantity, unit_price=unit, subtotal=line_total))
                db.add(InventoryMovement(product_id=product.id, user_id=admin.id, sale_id=sale.id, type="sale",
                                         quantity=quantity, previous_stock=before, resulting_stock=product.stock, date=date))
        db.commit()
        print("Datos demo insertados: categorías, productos, 21 ventas, detalles y movimientos.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
