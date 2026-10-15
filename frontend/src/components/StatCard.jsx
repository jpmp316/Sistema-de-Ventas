
function StatCard({
  title,
  value,
  description,
  icon: Icon,
  color = "teal",
  alert = false,
}) {
  return (
    <article className="stat-card">
      <div className={`stat-icon ${color}`}>
        <Icon size={22} strokeWidth={1.8} />
      </div>

      <div className="stat-content">
        <p className="stat-title">{title}</p>
        <h3 className="stat-value">{value}</h3>

        <p className={`stat-description ${alert ? "alert" : ""}`}>
          {description}
        </p>
      </div>
    </article>
  );
}

export default StatCard;
