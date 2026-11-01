import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createSale, getProducts, getSales, getSale, getCategories } from "../api";
import { useAuth } from "../auth/AuthContext";

const currency = (n) => `$${new Intl.NumberFormat("es-CO").format(n || 0)}`;
const saleStatus = (status) => ({ completed: "Completada", cancelled: "Anulada" }[status] ?? status);
const saleDate = (value) => new Date(value).toLocaleString("es-CO", { dateStyle: "medium", timeStyle: "short" });

async function loadCatalog(token) {
  const first = await getProducts(token, 1, 100);
  const items = [...first.items];
  for (let page = 2; page <= first.total_pages; page += 1) {
    const next = await getProducts(token, page, 100);
    items.push(...next.items);
  }
  return items;
}

function Sales() {
  const { token } = useAuth();
  const [products, setProducts] = useState([]); const [categories, setCategories] = useState([]); const [sales, setSales] = useState([]);
  const [page, setPage] = useState(1); const [salesPage, setSalesPage] = useState({ total: 0, total_pages: 0 });
  const [cart, setCart] = useState([]); const [categoryFilter,setCategoryFilter]=useState("all");const [productSearch,setProductSearch]=useState("");
  const [busy, setBusy] = useState(false); const [error, setError] = useState(""); const [message, setMessage] = useState(""); const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const detailHeading = useRef(null);
  useEffect(() => {
    if (detail) {
      detailHeading.current?.focus({ preventScroll: true });
      detailHeading.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [detail]);
  const load = useCallback(async () => { const [p, c, s] = await Promise.all([loadCatalog(token), getCategories(token), getSales(token, page, 10)]); setProducts(p.filter(x=>x.is_active)); setCategories(c.filter(x=>x.is_active)); setSales(s.items); setSalesPage(s); }, [token,page]);
  useEffect(() => { load().catch(e=>setError(e.message)).finally(()=>setLoading(false)); }, [load]);
  const total = useMemo(() => cart.reduce((sum, line) => sum + line.product.price_cents * line.quantity, 0), [cart]);
  const filteredProducts=products.filter(p=>(categoryFilter==="all"||String(p.category_id)===categoryFilter)&&`${p.name} ${p.code}`.toLowerCase().includes(productSearch.trim().toLowerCase()));
  function addProduct(product) { setCart(c=>{const found=c.find(x=>x.product.id===product.id); return found?c.map(x=>x.product.id===product.id?{...x,quantity:Math.min(x.quantity+1, product.stock)}:x):[...c,{product,quantity:1}];}); }
  async function checkout() { setBusy(true);setError("");setMessage("");try { const sale=await createSale(token,cart.map(x=>({product_id:x.product.id,quantity:x.quantity})));setCart([]);setMessage(`Venta #${sale.id} registrada.`);await load(); } catch(e){setError(e.message);}finally{setBusy(false);} }
  async function showDetail(id) {
    setDetailLoading(true); setError(""); setDetail(null);
    try { setDetail(await getSale(token, id)); }
    catch (e) { setError(e.message); }
    finally { setDetailLoading(false); }
  }
  return <><section className="page-heading"><div><p className="eyebrow">OPERACIÓN</p><h1>Ventas</h1><p className="page-subtitle">Agrega productos al carrito y confirma la operación.</p></div></section>{error&&<p role="alert" className="new-product-error">{error}</p>}{message&&<p role="status">{message}</p>}
    <section className="panel new-product-form"><div className="panel-heading"><div><h2>Nueva venta</h2><p>Filtra el catálogo, agrega artículos y completa el carrito.</p></div></div><div className="sales-workspace"><div className="sales-catalog"><div className="products-toolbar"><input className="sales-search" type="search" aria-label="Buscar producto o código" placeholder="Buscar producto o código" value={productSearch} onChange={e=>setProductSearch(e.target.value)}/><select className="filter-select" aria-label="Filtrar productos por categoría" value={categoryFilter} onChange={e=>setCategoryFilter(e.target.value)}><option value="all">Todas las categorías</option>{categories.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select></div><div className="table-wrapper"><table className="sales-table"><thead><tr><th>Producto</th><th>Precio</th><th>Existencias</th><th></th></tr></thead><tbody>{loading&&<tr><td colSpan="4">Cargando catálogo…</td></tr>}{filteredProducts.map(p=><tr key={p.id}><td><strong>{p.name}</strong><small className="catalog-code">{p.code} · {p.category?.name}</small></td><td>{currency(p.price_cents/100)}</td><td>{p.stock}</td><td><button className="subtle-button" type="button" disabled={busy||loading||p.stock<1||cart.some(line=>line.product.id===p.id&&line.quantity>=p.stock)} onClick={()=>addProduct(p)}>Agregar</button></td></tr>)}{!loading&&!filteredProducts.length&&<tr><td colSpan="4">No hay productos para esta búsqueda y categoría.</td></tr>}</tbody></table></div></div><aside className="sales-cart"><h3>Carrito <span>{cart.length} productos</span></h3>{cart.length===0?<p className="cart-empty">Agrega productos desde el catálogo.</p>:cart.map(line=><div className="cart-line" key={line.product.id}><div><strong>{line.product.name}</strong><small>{currency(line.product.price_cents/100)} por unidad</small></div><input aria-label={`Cantidad de ${line.product.name}`} disabled={busy} type="number" step="1" min="1" max={line.product.stock} value={line.quantity} onChange={e=>setCart(c=>c.map(x=>x.product.id===line.product.id?{...x,quantity:Number(e.target.value)}:x))}/><button className="text-button" type="button" disabled={busy} onClick={()=>setCart(c=>c.filter(x=>x.product.id!==line.product.id))}>Quitar</button></div>)}<div className="cart-total"><span>Total</span><strong>{currency(total/100)}</strong></div><button className="primary-button" type="button" disabled={busy||loading||!cart.length||cart.some(x=>!Number.isInteger(x.quantity)||x.quantity<1||x.quantity>x.product.stock)} onClick={checkout}>{busy?"Procesando…":"Confirmar venta"}</button></aside></div></section>
    <section className="panel recent-panel"><h2>Historial de ventas</h2><div className="table-wrapper"><table className="sales-table"><thead><tr><th>Venta</th><th>Fecha</th><th>Estado</th><th>Total</th><th>Detalle</th></tr></thead><tbody>{loading&&<tr><td colSpan="5">Cargando ventas…</td></tr>}{!loading&&!sales.length&&<tr><td colSpan="5">Aún no hay ventas registradas.</td></tr>}{!loading&&sales.map(s=><tr key={s.id}><td>#{s.id}</td><td>{saleDate(s.date)}</td><td><span className="sale-status">{saleStatus(s.status)}</span></td><td>{currency(Number(s.total))}</td><td><button className="text-button" disabled={detailLoading} onClick={()=>showDetail(s.id)}>Ver detalle</button></td></tr>)}</tbody></table></div><div className="pagination-bar"><span>{salesPage.total} ventas · página {(salesPage.page || 1)} de {Math.max(salesPage.total_pages,1)}</span><div><button className="subtle-button" disabled={loading||page<=1} onClick={()=>{setLoading(true);setPage(p=>p-1);}}>Anterior</button><button className="subtle-button" disabled={loading||page>=salesPage.total_pages} onClick={()=>{setLoading(true);setPage(p=>p+1);}}>Siguiente</button></div></div></section>
    {detailLoading && <p role="status">Cargando detalle de la venta…</p>}
    {detail && <section className="panel sale-detail" aria-labelledby="sale-detail-heading">
      <div className="sale-detail-header">
        <div><p className="eyebrow">COMPROBANTE DE OPERACIÓN</p><h2 id="sale-detail-heading" tabIndex="-1" ref={detailHeading}>Venta #{detail.id}</h2></div>
        <button className="subtle-button" type="button" onClick={()=>setDetail(null)}>Cerrar detalle</button>
      </div>
      <dl className="sale-detail-meta">
        <div><dt>Fecha y hora</dt><dd>{saleDate(detail.date)}</dd></div>
        <div><dt>Registrada por</dt><dd>{detail.username}</dd></div>
        <div><dt>Estado</dt><dd><span className="sale-status">{saleStatus(detail.status)}</span></dd></div>
        <div><dt>Unidades vendidas</dt><dd>{detail.details.reduce((sum, line)=>sum+line.quantity,0)}</dd></div>
      </dl>
      <div className="table-wrapper"><table className="sales-table sale-detail-table">
        <caption>Productos de la venta · valores en pesos colombianos (COP)</caption>
        <thead><tr><th scope="col">Producto</th><th scope="col">Cantidad</th><th scope="col">Precio unitario</th><th scope="col">Subtotal</th></tr></thead>
        <tbody>{detail.details.map(line=><tr key={line.id}><td><strong>{line.product_name}</strong><small className="catalog-code">{line.product_code}</small></td><td>{line.quantity}</td><td>{currency(Number(line.unit_price))}</td><td>{currency(Number(line.subtotal))}</td></tr>)}</tbody>
      </table></div>
      <div className="sale-detail-total"><span>Total de la venta</span><strong>{currency(Number(detail.total))}</strong></div>
      <p className="sale-detail-note">Los precios y subtotales corresponden al momento de la venta. Los nombres y códigos muestran el catálogo actual.</p>
    </section>}
  </>;
}
export default Sales;
