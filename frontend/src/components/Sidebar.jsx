import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Vue d'ensemble", ico: "▦", end: true },
  { to: "/carte", label: "Carte interactive", ico: "◉" },
  { to: "/signalements", label: "Signalements", ico: "▤" },
  { to: "/ml", label: "Détection IA", ico: "◈" },
  { to: "/agents", label: "Agents", ico: "◐" },
  { to: "/parametres", label: "Paramètres", ico: "⚙" },
];

export default function Sidebar({ onLogout, user }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-logo">C</div>
        <div>
          <div className="brand-name">CityReport</div>
          <div className="brand-sub">Console municipale</div>
        </div>
      </div>

      <nav>
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.end}
            className={({ isActive }) =>
              "nav-item" + (isActive ? " active" : "")
            }
          >
            <span className="ico">{l.ico}</span>
            <span>{l.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div style={{ marginBottom: 8, color: "rgba(255,255,255,0.75)" }}>
          {user?.nom || "Administrateur"}
        </div>
        <button
          onClick={onLogout}
          className="nav-item"
          style={{
            width: "100%",
            background: "transparent",
            border: "1px solid rgba(255,255,255,0.15)",
            color: "rgba(255,255,255,0.7)",
          }}
        >
          <span className="ico">⏻</span>
          <span>Déconnexion</span>
        </button>
      </div>
    </aside>
  );
}
