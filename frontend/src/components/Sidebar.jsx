import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  Boxes,
  Users,
  ChartNoAxesCombined,
  Store,
  KeyRound,
} from "lucide-react";

const menuItems = [
  { label: "Resumen", icon: LayoutDashboard },
  { label: "Ventas", icon: ShoppingCart },
  { label: "Productos", icon: Package },
  { label: "Inventario", icon: Boxes },
  { label: "Estadísticas", icon: ChartNoAxesCombined },
  { label: "Usuarios", icon: Users },
  { label: "Mi contraseña", icon: KeyRound, sellerOnly: true },
];

function Sidebar({ vistaActual, onCambiarVista, role }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">N</div>
        <div>
          <h2>
            Nexo<span className="brand-period">.</span>
          </h2>
          <span>Ventas e Inventario</span>
        </div>
      </div>

      <p className="nav-caption">ESPACIO DE TRABAJO</p>
      <nav className="sidebar-nav" aria-label="Navegación principal">
        {menuItems
          .filter(
            (item) =>
              (role === "admin" && !item.sellerOnly) ||
              (role === "vendedor" &&
                ["Ventas", "Inventario", "Mi contraseña"].includes(item.label)),
          )
          .map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.label}
                type="button"
                aria-current={
                  vistaActual === item.label.toLowerCase() ? "page" : undefined
                }
                className={`menu-item ${
                  vistaActual === item.label.toLowerCase() ? "active" : ""
                }`}
                onClick={() => onCambiarVista(item.label.toLowerCase())}
              >
                <Icon size={19} strokeWidth={1.8} />
                <span>{item.label}</span>
              </button>
            );
          })}
      </nav>

      <div className="sidebar-store">
        <Store size={21} />
        <div>
          <strong>Tu negocio, conectado</strong>
          <span>Ventas · Inventario · Equipo</span>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
