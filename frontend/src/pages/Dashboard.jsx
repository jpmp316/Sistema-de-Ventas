import { useEffect, useState } from "react";
import { AlertTriangle, ChartNoAxesColumn, CircleDollarSign, Package, ShoppingBag } from "lucide-react";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";
import StatCard from "../components/StatCard";
import { getReportSummary } from "../api";
import { useAuth } from "../auth/AuthContext";

const money = (value) => `$${new Intl.NumberFormat("es-CO").format(value || 0)}`;

function Dashboard() {
  const { token } = useAuth();
  const [days, setDays] = useState(7);
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let canceled = false;
    getReportSummary(token, days).then((data) => { if (!canceled) { setReport(data); setError(""); } }).catch((err) => { if (!canceled) setError(err.message); });
    return () => { canceled = true; };
  }, [token, days]);
  return <div>
    <section className="page-heading"><div><p className="eyebrow">PANEL DE CONTROL</p><h1>Resumen general</h1><p className="page-subtitle">Indicadores calculados desde las operaciones registradas.</p></div><select className="subtle-button" value={days} onChange={(e) => { setReport(null); setDays(Number(e.target.value)); }}><option value={1}>Hoy</option><option value={7}>Últimos 7 días</option><option value={30}>Últimos 30 días</option><option value={90}>Últimos 90 días</option></select></section>
    {error && <p className="new-product-error" role="alert">{error}</p>}
    {!report ? <p>Cargando estadísticas…</p> : <>
      <section className="stats-grid">
        <StatCard title="Ingresos del periodo" value={money(report.revenue)} description={days === 1 ? "Hoy · hora de Colombia" : `${days} días`} icon={CircleDollarSign} color="teal"/>
        <StatCard title="Operaciones" value={report.operations} description="Ventas completadas" icon={ShoppingBag} color="blue"/>
        <StatCard title="Movimientos de inventario" value={report.inventory_movements} description="En el periodo" icon={ChartNoAxesColumn} color="purple"/>
        <StatCard title="Productos con stock bajo" value={report.low_stock_products} description="Requieren atención" icon={AlertTriangle} color="red" alert/>
      </section>
      <section className="analytics-grid">
        <article className="panel sales-panel"><div className="panel-heading"><div><h2>Ingresos por día</h2><p>Ventas completadas en el periodo</p></div></div><div className="chart-container"><ResponsiveContainer width="100%" height="100%"><AreaChart data={report.sales_by_day}><CartesianGrid stroke="#edf0f5" vertical={false}/><XAxis dataKey="day"/><YAxis/><Tooltip formatter={(v) => [money(v), "Ingresos"]}/><Area dot={days === 1} dataKey="revenue" stroke="#0dbaa0" fill="#0dbaa033"/></AreaChart></ResponsiveContainer></div></article>
        <article className="panel products-panel"><div className="panel-heading"><div><h2>Más vendidos</h2><p>Unidades en el periodo</p></div></div>{report.top_products.map((item) => <div className="product-row" key={item.name}><Package size={18}/><strong>{item.name}</strong><span>{item.quantity} unidades</span></div>)}</article>
      </section>
    </>}
  </div>;
}
export default Dashboard;
