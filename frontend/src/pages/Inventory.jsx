import { useEffect, useState } from "react";
import { getInventoryMovements } from "../api";
import { useAuth } from "../auth/AuthContext";

function movementLabel(movement) {
  if (movement.type === "adjustment") {
    return movement.resulting_stock > movement.previous_stock ? "Ajuste de entrada" : "Ajuste de salida";
  }
  return { sale: "Salida por venta", entry: "Entrada", purchase: "Entrada por compra" }[movement.type] ?? movement.type;
}

function Inventory() {
  const { token } = useAuth(); const [result,setResult]=useState({items:[],total:0,total_pages:0});const [from,setFrom]=useState("");const [to,setTo]=useState("");const [type,setType]=useState("");const [page,setPage]=useState(1);const [error,setError]=useState("");const [loading,setLoading]=useState(false);
  useEffect(()=>{let live=true;setLoading(true);getInventoryMovements(token,{date_from:from,date_to:to,type},page).then(data=>{if(live){setResult(data);setError("");}}).catch(e=>live&&setError(e.message)).finally(()=>live&&setLoading(false));return()=>{live=false};},[token,from,to,type,page]);
  function changeFilter(setter,value){setter(value);setPage(1);}
  return <><section className="page-heading"><div><p className="eyebrow">CONTROL DE EXISTENCIAS</p><h1>Inventario</h1><p className="page-subtitle">Movimientos recientes con filtros y páginas.</p></div></section>{error&&<p className="new-product-error" role="alert">{error}</p>}<section className="panel products-management"><div className="products-toolbar inventory-filters"><label className="date-filter">Desde<input type="date" value={from} onChange={e=>changeFilter(setFrom,e.target.value)}/></label><label className="date-filter">Hasta<input type="date" value={to} onChange={e=>changeFilter(setTo,e.target.value)}/></label><select className="filter-select" value={type} onChange={e=>changeFilter(setType,e.target.value)}><option value="">Todos los movimientos</option><option value="sale">Salida por venta</option><option value="adjustment">Ajustes de entrada o salida</option></select></div><div className="table-wrapper"><table className="sales-table"><thead><tr><th>Producto</th><th>Tipo</th><th>Cantidad</th><th>Stock anterior</th><th>Stock posterior</th><th>Fecha</th><th>Responsable</th></tr></thead><tbody>{loading?<tr><td colSpan="7">Cargando movimientos…</td></tr>:result.items.map(m=><tr key={m.id}><td>{m.product_name}</td><td>{movementLabel(m)}</td><td>{m.resulting_stock > m.previous_stock ? "+" : m.resulting_stock < m.previous_stock ? "−" : ""}{m.quantity}</td><td>{m.previous_stock}</td><td>{m.resulting_stock}</td><td>{new Date(m.date).toLocaleString("es-CO")}</td><td>{m.username}</td></tr>)}{!loading&&!result.items.length&&<tr><td colSpan="7">No hay movimientos con esos filtros.</td></tr>}</tbody></table></div><div className="pagination-bar"><span>{result.total} movimientos · página {result.page} de {Math.max(result.total_pages,1)}</span><div><button className="subtle-button" disabled={page<=1||loading} onClick={()=>setPage(p=>p-1)}>Anterior</button><button className="subtle-button" disabled={page>=result.total_pages||loading} onClick={()=>setPage(p=>p+1)}>Siguiente</button></div></div></section></>;
}
export default Inventory;
