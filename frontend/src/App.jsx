
import {
  Search,
  Bell,
  CalendarDays,
  TrendingUp,
  AlertTriangle,
  ChevronDown,
  ArrowUpRight,
  MoreHorizontal,
  CircleDollarSign,
  ShoppingBag,
  ChartNoAxesColumn,
  Package,
} from "lucide-react";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { useState } from "react";
import Sidebar from "./components/Sidebar";
import StatCard from "./components/StatCard";
import "./App.css";


const salesDataByPeriod = {
  "7 días": [
    { day: "Lun", sales: 75000 },
    { day: "Mar", sales: 170000 },
    { day: "Mié", sales: 135000 },
    { day: "Jue", sales: 250000 },
    { day: "Vie", sales: 175000 },
    { day: "Sáb", sales: 335000 },
    { day: "Dom", sales: 205000 },
  ],

  "30 días": [
    { day: "Sem. 1", sales: 850000 },
    { day: "Sem. 2", sales: 1200000 },
    { day: "Sem. 3", sales: 980000 },
    { day: "Sem. 4", sales: 1500000 },
  ],

  "90 días": [
    { day: "Mes 1", sales: 4200000 },
    { day: "Mes 2", sales: 5100000 },
    { day: "Mes 3", sales: 4800000 },
  ],
};


const topProducts = [
  { name: "Gaseosa 500 ml", category: "Bebidas", quantity: 120, color: "pink" },
  { name: "Pan tajado", category: "Panadería", quantity: 95, color: "orange" },
  { name: "Arroz 1 kg", category: "Abarrotes", quantity: 78, color: "blue" },
  { name: "Huevos x 30", category: "Lácteos", quantity: 65, color: "green" },
];

const recentSales = [
  { id: "000154", customer: "Cliente general", date: "Hoy, 11:24", total: "$42.500" },
  { id: "000153", customer: "Cliente general", date: "Hoy, 10:18", total: "$18.900" },
  { id: "000152", customer: "Cliente general", date: "Hoy, 09:03", total: "$67.300" },
];

const currency = (value) =>
  `$${new Intl.NumberFormat("es-CO").format(value)}`;

function App() {
  const [periodo, setPeriodo] = useState("7 días");
  const salesData = salesDataByPeriod[periodo];
  const [vistaActual, setVistaActual] = useState("resumen");
  console.log("Pantalla seleccionada:", vistaActual);
  return (
    <div className="app-layout">
      <Sidebar
        vistaActual={vistaActual}
        onCambiarVista={setVistaActual}
      />
      <main className="main-content">
        <header className="topbar">
          <div className="mobile-brand">Nexo</div>

          <div className="topbar-spacer" />

          <label className="search-box">
            <Search size={18} />
            <input type="search" placeholder="Buscar..." />
          </label>

          <button className="icon-button" aria-label="Notificaciones">
            <Bell size={20} />
            <span className="notification-dot" />
          </button>

          <button className="profile-button">
            <span className="avatar">A</span>
            <span>Administrador</span>
            <ChevronDown size={16} />
          </button>
        </header>

        <section className="page-heading">
          <div>
            <p className="eyebrow">PANEL DE CONTROL</p>
            <h1>Resumen general</h1>
            <p className="page-subtitle">
              Aquí tienes lo que sucede en tu negocio hoy.
            </p>
          </div>

          <button className="date-button">
            <CalendarDays size={17} />
            Últimos 7 días
            <ChevronDown size={15} />
          </button>
        </section>

        <section className="stats-grid">
          <StatCard
            title="Ventas de hoy"
            value="$1.284.500"
            description={<><TrendingUp size={14} /> +12,8% <span>vs. ayer</span></>}
            icon={CircleDollarSign}
            color="teal"
          />

          <StatCard
            title="Ventas del mes"
            value="$18.420.000"
            description={<><TrendingUp size={14} /> +8,2% <span>vs. mes anterior</span></>}
            icon={ShoppingBag}
            color="blue"
          />

          <StatCard
            title="Transacciones"
            value="48"
            description={<><TrendingUp size={14} /> +6,4% <span>vs. ayer</span></>}
            icon={ChartNoAxesColumn}
            color="purple"
          />

          <StatCard
            title="Productos con stock bajo"
            value="7"
            description={<><AlertTriangle size={14} /> Requieren atención</>}
            icon={Package}
            color="red"
            alert
          />
        </section>

        <section className="analytics-grid">
          <article className="panel sales-panel">
            <div className="panel-heading">
              <div>
                <h2>Rendimiento de ventas</h2>
                <p>Ingresos durante los últimos {periodo}</p>
              </div>  
                  <select
                    className="subtle-button"
                    value={periodo}
                    onChange={(event) => setPeriodo(event.target.value)}
                  >
                    <option value="7 días">Últimos 7 días</option>
                    <option value="30 días">Últimos 30 días</option>
                    <option value="90 días">Últimos 90 días</option>
                  </select>
              </div>

            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={salesData}
                  margin={{ top: 12, right: 8, left: 0, bottom: 0 }}
                >
                  <defs>
                    <linearGradient id="salesFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#0dbaa0" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#0dbaa0" stopOpacity={0.01} />
                    </linearGradient>
                  </defs>

                  <CartesianGrid stroke="#edf0f5" vertical={false} />
                  <XAxis
                    dataKey="day"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: "#8490a5", fontSize: 12 }}
                    dy={10}
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: "#8490a5", fontSize: 11 }}
                    tickFormatter={(value) => `${value / 1000}k`}
                    width={43}
                  />
                  <Tooltip
                    formatter={(value) => [currency(value), "Ventas"]}
                    contentStyle={{
                      borderRadius: 10,
                      border: "1px solid #e8edf3",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="sales"
                    stroke="#0dbaa0"
                    strokeWidth={3}
                    fill="url(#salesFill)"
                    dot={{ r: 3, fill: "#ffffff", stroke: "#0dbaa0", strokeWidth: 2 }}
                    activeDot={{ r: 5 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="panel products-panel">
            <div className="panel-heading">
              <div>
                <h2>Productos más vendidos</h2>
                <p>Unidades vendidas esta semana</p>
              </div>
              <button className="text-button">
                Ver todos <ArrowUpRight size={16} />
              </button>
            </div>

            <div className="product-list">
              {topProducts.map((product) => (
                <div className="product-row" key={product.name}>
                  <div className={`product-symbol ${product.color}`}>
                    <Package size={20} />
                  </div>

                  <div className="product-info">
                    <strong>{product.name}</strong>
                    <span>{product.category}</span>
                  </div>

                  <div className="product-quantity">
                    <strong>{product.quantity}</strong>
                    <span>unidades</span>
                  </div>
                </div>
              ))}
            </div>
          </article>
        </section>

        <section className="panel recent-panel">
          <div className="panel-heading">
            <div>
              <h2>Ventas recientes</h2>
              <p>Últimas operaciones registradas</p>
            </div>
            <button className="text-button">
              Ver todas <ArrowUpRight size={16} />
            </button>
          </div>

          <div className="table-wrapper">
            <table className="sales-table">
              <thead>
                <tr>
                  <th>N.º de venta</th>
                  <th>Cliente</th>
                  <th>Fecha</th>
                  <th>Total</th>
                  <th>Estado</th>
                  <th />
                </tr>
              </thead>

              <tbody>
                {recentSales.map((sale) => (
                  <tr key={sale.id}>
                    <td className="sale-id">#{sale.id}</td>
                    <td>{sale.customer}</td>
                    <td>{sale.date}</td>
                    <td className="sale-total">{sale.total}</td>
                    <td>
                      <span className="status-badge">Completada</span>
                    </td>
                    <td>
                      <button className="row-action" aria-label={`Opciones de venta ${sale.id}`}>
                        <MoreHorizontal size={19} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <footer className="page-footer">
          Nexo · Gestión sencilla para tu negocio
        </footer>
      </main>
    </div>
  );
}

export default App;


