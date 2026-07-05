import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Legend,
} from "recharts";
import { api } from "../api";
import { CAT_COLORS } from "../components/badges";

const STATUT_COLORS = { "Résolu": "#059669", "En cours": "#d97706", "Nouveau": "#1e3a5f" };

function Kpi({ label, value, trend, trendClass, color }) {
  return (
    <div className={`kpi ${color || ""}`}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {trend && <div className={`kpi-trend ${trendClass || ""}`}>{trend}</div>}
    </div>
  );
}

export default function Dashboard() {
  const [ov, setOv] = useState(null);
  const [cats, setCats] = useState([]);
  const [statuts, setStatuts] = useState([]);
  const [mois, setMois] = useState([]);
  const [quartiers, setQuartiers] = useState([]);

  useEffect(() => {
    api.overview().then(setOv);
    api.parCategorie().then(setCats);
    api.parStatut().then(setStatuts);
    api.parMois().then(setMois);
    api.parQuartier().then(setQuartiers);
  }, []);

  if (!ov) return <div className="spinner" />;

  const maxScore = Math.max(...quartiers.map((q) => q.score_priorite), 1);

  return (
    <>
      <div className="page-header">
        <h1>Vue d'ensemble</h1>
        <p>Suivi en temps réel des signalements citoyens</p>
      </div>

      <div className="kpi-grid">
        <Kpi label="Total signalements" value={ov.total.toLocaleString("fr-FR")}
          trend="Tous statuts confondus" />
        <Kpi label="Résolus" value={ov.resolus} color="green"
          trend={`${ov.taux_resolution}% de résolution`} trendClass="up" />
        <Kpi label="En cours" value={ov.en_cours} color="amber"
          trend="En traitement" />
        <Kpi label="Suspects (IA)" value={ov.suspects} color="red"
          trend="À vérifier" trendClass="down" />
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-title">
            Signalements par catégorie
            <span className="sub">classification automatique</span>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={cats} layout="vertical"
              margin={{ left: 8, right: 16 }}>
              <CartesianGrid horizontal={false} stroke="#e6e4dd" />
              <XAxis type="number" tick={{ fontSize: 12, fill: "#8b8f98" }} />
              <YAxis type="category" dataKey="categorie" width={90}
                tick={{ fontSize: 12, fill: "#4b5563" }} />
              <Tooltip cursor={{ fill: "#f4f3ef" }} />
              <Bar dataKey="total" radius={[0, 4, 4, 0]} barSize={22}>
                {cats.map((c, i) => (
                  <Cell key={i} fill={CAT_COLORS[c.categorie] || "#1e3a5f"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-title">Répartition par statut</div>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={statuts} dataKey="total" nameKey="statut"
                cx="50%" cy="50%" innerRadius={55} outerRadius={90}
                paddingAngle={2}>
                {statuts.map((s, i) => (
                  <Cell key={i} fill={STATUT_COLORS[s.statut] || "#8b8f98"} />
                ))}
              </Pie>
              <Tooltip />
              <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-title">
            Évolution mensuelle
            <span className="sub">volume de signalements</span>
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={mois} margin={{ left: 0, right: 16 }}>
              <CartesianGrid stroke="#e6e4dd" vertical={false} />
              <XAxis dataKey="mois" tick={{ fontSize: 11, fill: "#8b8f98" }} />
              <YAxis tick={{ fontSize: 11, fill: "#8b8f98" }} />
              <Tooltip />
              <Line type="monotone" dataKey="total" stroke="#1e3a5f"
                strokeWidth={2.5} dot={{ r: 3, fill: "#d97706" }}
                activeDot={{ r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-title">
            Quartiers prioritaires
            <span className="sub">score de priorité</span>
          </div>
          <div style={{ marginTop: 4 }}>
            {quartiers.slice(0, 6).map((q) => (
              <div key={q.quartier}
                style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
                <span style={{ fontSize: 13, color: "#4b5563", width: 110 }}>
                  {q.quartier}
                </span>
                <div className="priority-bar" style={{ flex: 1 }}>
                  <div style={{ width: `${(q.score_priorite / maxScore) * 100}%` }} />
                </div>
                <span style={{ fontSize: 13, fontWeight: 600, color: "#1a1f29", width: 36, textAlign: "right" }}>
                  {q.score_priorite}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
