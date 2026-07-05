import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { api } from "../api";
import { CAT_COLORS } from "../components/badges";

export default function ML() {
  const [suspects, setSuspects] = useState([]);
  const [classif, setClassif] = useState([]);

  useEffect(() => {
    api.suspects().then(setSuspects);
    api.classification().then(setClassif);
  }, []);

  return (
    <>
      <div className="page-header">
        <h1>Détection par intelligence artificielle</h1>
        <p>Classification automatique et repérage des signalements suspects</p>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-title">
            Performance de classification
            <span className="sub">confiance moyenne par catégorie</span>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={classif} margin={{ left: 0, right: 16 }}>
              <CartesianGrid stroke="#e6e4dd" vertical={false} />
              <XAxis dataKey="categorie" tick={{ fontSize: 11, fill: "#8b8f98" }}
                interval={0} angle={-15} textAnchor="end" height={50} />
              <YAxis tick={{ fontSize: 11, fill: "#8b8f98" }} />
              <Tooltip cursor={{ fill: "#f4f3ef" }} />
              <Bar dataKey="total" radius={[4, 4, 0, 0]} barSize={40}>
                {classif.map((c, i) => (
                  <Cell key={i} fill={CAT_COLORS[c.categorie] || "#1e3a5f"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div style={{ marginTop: 12, display: "grid", gap: 6 }}>
            {classif.map((c) => (
              <div key={c.categorie} style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "#4b5563" }}>
                <span>{c.categorie}</span>
                <span style={{ fontWeight: 600 }}>{Math.round(c.confiance_moyenne * 100)}% confiance</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card" style={{ background: "#fff" }}>
          <div className="card-title">
            Comment fonctionne le module IA
          </div>
          <div style={{ fontSize: 13, color: "#4b5563", lineHeight: 1.7 }}>
            <p style={{ marginBottom: 12 }}>
              <strong style={{ color: "#1e3a5f" }}>1. Classification.</strong> À chaque
              nouveau signalement, le titre et la description sont analysés pour en
              déduire la catégorie la plus probable, avec un score de confiance.
            </p>
            <p style={{ marginBottom: 12 }}>
              <strong style={{ color: "#1e3a5f" }}>2. Détection d'anomalies.</strong> Un
              modèle <em>Isolation Forest</em> apprend la distribution normale des
              signalements (position, horaire, densité locale) et isole les cas
              atypiques.
            </p>
            <p>
              <strong style={{ color: "#dc2626" }}>3. Signalements suspects.</strong> Les
              rafales depuis une même position, les doublons probables et les
              coordonnées incohérentes sont remontés en priorité aux agents.
            </p>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-title">
          Top signalements suspects
          <span className="sub">triés par score d'anomalie</span>
        </div>
        {suspects.length === 0 ? (
          <p style={{ color: "#8b8f98", fontSize: 14, padding: "20px 0", textAlign: "center" }}>
            Aucun signalement suspect détecté pour le moment.
          </p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>#</th>
                <th>Titre</th>
                <th>Quartier</th>
                <th>Raison</th>
                <th>Localisation</th>
                <th>Fréquence</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {suspects.map((s) => (
                <tr key={s.signalement_id}>
                  <td style={{ color: "#8b8f98" }}>{s.signalement_id}</td>
                  <td style={{ fontWeight: 500, color: "#1a1f29" }}>{s.titre}</td>
                  <td>{s.quartier}</td>
                  <td style={{ fontSize: 12 }}>{s.raison_principale}</td>
                  <td>{s.anomalie_localisation ? "⚠" : "—"}</td>
                  <td>{s.anomalie_frequence ? "⚠" : "—"}</td>
                  <td>
                    <span style={{
                      fontWeight: 600,
                      color: s.score_anomalie > 0.7 ? "#dc2626" : "#d97706",
                    }}>
                      {s.score_anomalie}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
