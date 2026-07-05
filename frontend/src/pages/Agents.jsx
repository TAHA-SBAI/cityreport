import { useEffect, useState } from "react";
import { api } from "../api";
import { formatDate } from "../components/badges";

export default function Agents() {
  const [agents, setAgents] = useState([]);

  useEffect(() => { api.agents().then(setAgents); }, []);

  return (
    <>
      <div className="page-header">
        <h1>Agents municipaux</h1>
        <p>Équipes de terrain et répartition par secteur</p>
      </div>

      <div className="toolbar">
        <span style={{ fontSize: 13, color: "#8b8f98" }}>
          {agents.length} agents · {agents.reduce((a, g) => a + g.nb_signalements_geres, 0)} interventions gérées
        </span>
        <a className="btn" href={api.exportUrl("agents")} style={{ marginLeft: "auto" }}>
          ↓ Exporter CSV
        </a>
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
        gap: 16,
      }}>
        {agents.map((a) => (
          <div key={a.id} className="card">
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 14 }}>
              <div style={{
                width: 46, height: 46, borderRadius: "50%",
                background: "#1e3a5f", color: "#fff",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontWeight: 600, fontFamily: "var(--font-display)", fontSize: 16,
              }}>
                {a.prenom[0]}{a.nom[0]}
              </div>
              <div>
                <div style={{ fontWeight: 600, color: "#1a1f29" }}>
                  {a.prenom} {a.nom}
                </div>
                <div style={{ fontSize: 12, color: "#8b8f98" }}>{a.email}</div>
              </div>
            </div>

            <div style={{ display: "grid", gap: 8, fontSize: 13, color: "#4b5563" }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span>Secteur</span>
                <span style={{ fontWeight: 500, color: "#1e3a5f" }}>{a.secteur}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span>Interventions gérées</span>
                <span style={{ fontWeight: 600 }}>{a.nb_signalements_geres}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span>En fonction depuis</span>
                <span>{formatDate(a.date_prise_fonction)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
