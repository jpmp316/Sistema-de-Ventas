
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
          <h2>Nexo</h2>
          <span>Ventas e Inventario</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {menuItems.filter((item) => (role === "admin" && !item.sellerOnly) || (role === "vendedor" && ["Ventas", "Inventario", "Mi contraseña"].includes(item.label))).map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.label}
              type="button"
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
          <strong>Tienda Demo</strong>
          <span>Tu negocio</span>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;

