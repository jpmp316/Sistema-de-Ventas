import { useEffect, useState } from "react";
import { Package, Pencil, Plus, Power, Search } from "lucide-react";
import { createCategory, createProduct, getCategories, getProducts, setProductActive, updateProduct } from "../api";
import { useAuth } from "../auth/AuthContext";

const emptyProduct = {
  name: "",
  code: "",
  category_id: "",
  price: "",
  stock: "",
  minStock: "",
};

const formatCurrency = (cents) =>
  `$${new Intl.NumberFormat("es-CO").format(cents / 100)}`;

function Products() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const { token, logout: contextLogout } = useAuth();
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [reloadVersion, setReloadVersion] = useState(0);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("Todas");
  const [statusFilter, setStatusFilter] = useState("Todos");
  const [showForm, setShowForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [form, setForm] = useState(emptyProduct);
  const [formError, setFormError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [showCategoryForm, setShowCategoryForm] = useState(false);
  const [categoryName, setCategoryName] = useState("");
  const [categoryError, setCategoryError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadProducts() {
      if (!token) {
        setProducts([]);
        setLoading(false);
        return;
      }

      setLoading(true);
      setLoadError("");
      try {
        const [response, categoryResponse] = await Promise.all([
          getProducts(token),
          getCategories(token),
        ]);
        if (!cancelled) {
          setProducts(response.items);
          setCategories(categoryResponse);
        }
      } catch (error) {
        if (cancelled) return;
        if (error.status === 401) {
          contextLogout();
        } else {
          setLoadError(error.message);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadProducts();
    return () => {
      cancelled = true;
    };
  }, [token, reloadVersion, contextLogout]);

  const filteredProducts = products.filter((product) => {
    const query = search.trim().toLowerCase();
    const matchesSearch =
      product.name.toLowerCase().includes(query) ||
      product.code.toLowerCase().includes(query);
    const matchesCategory =
      categoryFilter === "Todas" || String(product.category_id) === categoryFilter;
    const matchesStatus =
      statusFilter === "Todos" ||
      (statusFilter === "Activos" && product.is_active) ||
      (statusFilter === "Inactivos" && !product.is_active);

    return matchesSearch && matchesCategory && matchesStatus;
  });

  function closeForm() {
    setShowForm(false);
    setEditingProduct(null);
    setForm(emptyProduct);
    setFormError("");
  }

  function openCreateForm() {
    setEditingProduct(null);
    setForm(emptyProduct);
    setFormError("");
    setSuccessMessage("");
    setShowForm(true);
  }

  function openEditForm(product) {
    setEditingProduct(product);
    setForm({
      name: product.name,
      code: product.code,
      category_id: String(product.category_id),
      price: (product.price_cents / 100).toFixed(2),
      stock: String(product.stock),
      minStock: String(product.min_stock),
    });
    setFormError("");
    setSuccessMessage("");
    setShowForm(true);
  }

  function updateFormField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
    setFormError("");
  }

  async function submitProduct(event) {
    event.preventDefault();
    setFormError("");
    setSuccessMessage("");

    const name = form.name.trim();
    const code = form.code.trim();
    const categoryId = Number(form.category_id);
    const price = Number(form.price);
    const priceCents = Math.round(price * 100);
    const stock = Number(form.stock);
    const minStock = Number(form.minStock);

    if (!name || !code || !form.category_id || form.price === "" || form.stock === "" || form.minStock === "") {
      setFormError("Completa todos los campos.");
      return;
    }
    if (
      !Number.isFinite(price) ||
      price <= 0 ||
      Math.abs(price * 100 - priceCents) > 1e-7 ||
      priceCents <= 0
    ) {
      setFormError("El precio debe ser mayor que cero y tener máximo dos decimales.");
      return;
    }
    if (!Number.isInteger(stock) || stock < 0) {
      setFormError("Las existencias deben ser un entero no negativo.");
      return;
    }
    if (!Number.isInteger(minStock) || minStock < 0) {
      setFormError("El stock mínimo debe ser un entero no negativo.");
      return;
    }

    const payload = {
      name,
      code,
      category_id: categoryId,
      price_cents: priceCents,
      stock,
      min_stock: minStock,
    };

    setBusy(true);
    try {
      if (editingProduct) {
        const updated = await updateProduct(token, editingProduct.id, payload);
        setProducts((current) => current.map((product) => product.id === updated.id ? updated : product));
        setSuccessMessage("Producto actualizado.");
      } else {
        const created = await createProduct(token, payload);
        setProducts((current) => [...current, created]);
        setSuccessMessage("Producto creado.");
      }
      closeForm();
    } catch (error) {
      if (error.status === 401) {
        sessionStorage.removeItem("nexo_access_token");
        contextLogout();
      } else {
        setFormError(error.message);
      }
    } finally {
      setBusy(false);
    }
  }

  async function toggleProductStatus(product) {
    setBusy(true);
    setLoadError("");
    setSuccessMessage("");
    try {
      const updated = await setProductActive(token, product.id, !product.is_active);
      setProducts((current) => current.map((item) => item.id === updated.id ? updated : item));
      setSuccessMessage(updated.is_active ? "Producto reactivado." : "Producto desactivado.");
    } catch (error) {
      if (error.status === 401) {
        sessionStorage.removeItem("nexo_access_token");
        contextLogout();
      } else {
        setLoadError(error.message);
      }
    } finally {
      setBusy(false);
    }
  }

  async function submitCategory(event) {
    event?.preventDefault();
    const name = categoryName.trim();
    if (!name) { setCategoryError("Escribe el nombre de la categoría."); return; }
    setBusy(true); setCategoryError(""); setSuccessMessage("");
    try {
      const created = await createCategory(token, name);
      setCategories((current) => [...current, created].sort((a, b) => a.name.localeCompare(b.name)));
      setForm((current) => ({ ...current, category_id: String(created.id) }));
      setCategoryName(""); setShowCategoryForm(false); setSuccessMessage("Categoría creada.");
    } catch (error) { setCategoryError(error.message); }
    finally { setBusy(false); }
  }

  if (!token) return null;

  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">GESTIÓN DE INVENTARIO</p>
          <h1>Productos</h1>
          <p className="page-subtitle">Administra los productos de tu negocio.</p>
        </div>
        <div className="products-heading-actions">
          <button className="primary-button" type="button" onClick={openCreateForm} disabled={busy}>
            <Plus size={18} /> Nuevo producto
          </button>
        </div>
      </section>

      {successMessage && <p className="products-message success-message" role="status">{successMessage}</p>}
      {loadError && (
        <p className="products-message new-product-error" role="alert">
          {loadError}
          <button type="button" className="text-button" onClick={() => setReloadVersion((v) => v + 1)}>Reintentar</button>
        </p>
      )}

      {showForm && (
        <form className="panel new-product-form" onSubmit={submitProduct}>
          <div className="new-product-form-heading">
            <h2>{editingProduct ? "Editar producto" : "Registrar producto"}</h2>
            <p>El precio se ingresa en pesos; el servidor lo conserva en centavos.</p>
          </div>
          <div className="new-product-fields">
            <label className="new-product-field">
              <span>Nombre</span>
              <input name="name" value={form.name} onChange={updateFormField} maxLength={100} disabled={busy} required />
            </label>
            <label className="new-product-field">
              <span>Código</span>
              <input name="code" value={form.code} onChange={updateFormField} maxLength={50} disabled={busy} required />
            </label>
            <label className="new-product-field">
              <span>Categoría</span>
              <select name="category_id" value={form.category_id} onChange={updateFormField} disabled={busy || categories.length === 0} required>
                <option value="">Selecciona una categoría</option>
                {categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
              </select>
              <button className="text-button" type="button" onClick={() => { setShowCategoryForm((visible) => !visible); setCategoryError(""); }} disabled={busy}>
                {showCategoryForm ? "Cancelar categoría" : "+ Crear categoría"}
              </button>
              {showCategoryForm && <div className="category-create-form">
                <input aria-label="Nombre de categoría" placeholder="Nombre de categoría" maxLength={100} value={categoryName} onChange={(event) => setCategoryName(event.target.value)} disabled={busy} required />
                <button className="subtle-button" type="button" onClick={submitCategory} disabled={busy}>{busy ? "Guardando…" : "Guardar categoría"}</button>
                {categoryError && <span className="new-product-error" role="alert">{categoryError}</span>}
              </div>}
            </label>
            <label className="new-product-field">
              <span>Precio</span>
              <input name="price" type="number" value={form.price} onChange={updateFormField} min="0.01" step="0.01" inputMode="decimal" disabled={busy} required />
            </label>
            <label className="new-product-field">
              <span>Existencias</span>
              <input name="stock" type="number" value={form.stock} onChange={updateFormField} min="0" step="1" disabled={busy} required />
            </label>
            <label className="new-product-field">
              <span>Stock mínimo</span>
              <input name="minStock" type="number" value={form.minStock} onChange={updateFormField} min="0" step="1" disabled={busy} required />
            </label>
          </div>
          {formError && <p className="new-product-error" role="alert">{formError}</p>}
          <div className="new-product-form-actions">
            <button className="subtle-button" type="button" onClick={closeForm} disabled={busy}>Cancelar</button>
            <button className="primary-button" type="submit" disabled={busy}>
              {busy ? "Guardando..." : editingProduct ? "Guardar cambios" : "Crear producto"}
            </button>
          </div>
        </form>
      )}

      <section className="panel products-management">
        <div className="products-toolbar">
          <label className="search-box products-search">
            <Search size={18} />
            <input type="search" placeholder="Buscar por nombre o código..." value={search} onChange={(event) => setSearch(event.target.value)} />
          </label>
          <select className="subtle-button" value={categoryFilter} onChange={(event) => setCategoryFilter(event.target.value)}>
            <option value="Todas">Todas las categorías</option>
            {categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
          </select>
          <select className="subtle-button" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="Todos">Todos los estados</option>
            <option value="Activos">Activos</option>
            <option value="Inactivos">Inactivos</option>
          </select>
        </div>

        <div className="table-wrapper">
          <table className="sales-table products-table">
            <thead>
              <tr>
                <th>Producto</th><th>Categoría</th><th>Precio</th><th>Existencias</th><th>Estado</th><th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} className="empty-products">Cargando productos...</td></tr>
              ) : filteredProducts.map((product) => {
                const outOfStock = product.stock === 0;
                const lowStock = product.stock > 0 && product.stock <= product.min_stock;
                return (
                  <tr key={product.id}>
                    <td>
                      <div className="managed-product">
                        <div className="managed-product-icon"><Package size={19} /></div>
                        <div><strong>{product.name}</strong><span>{product.code}</span></div>
                      </div>
                    </td>
                    <td>{product.category.name}</td>
                    <td className="sale-total">{formatCurrency(product.price_cents)}</td>
                    <td>{product.stock} unidades</td>
                    <td className="product-state-cell">
                      <span className={`status-badge ${product.is_active ? "status-active" : "status-inactive"}`}>
                        {product.is_active ? "Activo" : "Inactivo"}
                      </span>
                      <span className={`status-badge ${outOfStock ? "status-out" : lowStock ? "status-low" : "status-ok"}`}>
                        {outOfStock ? "Agotado" : lowStock ? "Stock bajo" : "Disponible"}
                      </span>
                    </td>
                    <td>
                      <div className="product-actions">
                        <button className="row-action" type="button" aria-label={`Editar ${product.name}`} title="Editar" onClick={() => openEditForm(product)} disabled={busy}>
                          <Pencil size={17} />
                        </button>
                        <button className="row-action" type="button" aria-label={product.is_active ? `Desactivar ${product.name}` : `Reactivar ${product.name}`} title={product.is_active ? "Desactivar" : "Reactivar"} onClick={() => toggleProductStatus(product)} disabled={busy}>
                          <Power size={17} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
              {!loading && filteredProducts.length === 0 && (
                <tr><td colSpan={6} className="empty-products">{products.length ? "No hay productos que coincidan con los filtros." : "Aún no hay productos registrados."}</td></tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="products-footer">Mostrando {filteredProducts.length} de {products.length} productos</div>
      </section>
    </>
  );
}

export default Products;
