import { useEffect, useState, useCallback } from "react";
import { api } from "../api";
import { CategorieBadge, StatutBadge, CAT_COLORS, formatDate } from "../components/badges";

export default function Signalements() {
  const [data, setData] = useState({ items: [], total: 0 });
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("");
  const [statut, setStatut] = useState("");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState(null);
  const limit = 20;

  const load = useCallback(() => {
    const params = { page, limit };
    if (q) params.q = q;
    if (cat) params.categorie = cat;
    if (statut) params.statut = statut;
    api.signalements(params).then(setData);
  }, [q, cat, statut, page]);

  useEffect(() => { load(); }, [load]);

  const pages = Math.ceil(data.total / limit);

  return (
    <>
      <div className="page-header">
        <h1>Signalements</h1>
        <p>Historique complet et suivi des interventions</p>
      </div>

      <div className="toolbar">
        <input className="input search" placeholder="Rechercher un signalement…"
          value={q} onChange={(e) => { setPage(1); setQ(e.target.value); }} />
        <select className="select" value={cat}
          onChange={(e) => { setPage(1); setCat(e.target.value); }}>
          <option value="">Toutes catégories</option>
          {Object.keys(CAT_COLORS).map((c) => <option key={c}>{c}</option>)}
        </select>
        <select className="select" value={statut}
          onChange={(e) => { setPage(1); setStatut(e.target.value); }}>
          <option value="">Tous statuts</option>
          <option>Nouveau</option>
          <option>En cours</option>
          <option>Résolu</option>
        </select>
        <a className="btn" href={api.exportUrl("signalements")}>↓ Exporter CSV</a>
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table className="table">
          <thead>
            <tr>
              <th>#</th>
              <th>Titre</th>
              <th>Catégorie</th>
              <th>Quartier</th>
              <th>Date</th>
              <th>Statut</th>
              <th>IA</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((s) => (
              <tr key={s.id} style={{ cursor: "pointer" }} onClick={() => setSelected(s)}>
                <td style={{ color: "#8b8f98" }}>{s.id}</td>
                <td style={{ fontWeight: 500, color: "#1a1f29" }}>{s.titre}</td>
                <td><CategorieBadge categorie={s.categorie} /></td>
                <td>{s.quartier}</td>
                <td>{formatDate(s.date_creation)}</td>
                <td><StatutBadge statut={s.statut} /></td>
                <td>
                  {s.anomalie
                    ? <span className="badge alert">⚠ Suspect</span>
                    : <span style={{ color: "#059669", fontSize: 16 }}>✓</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {pages > 1 && (
        <div style={{ display: "flex", gap: 8, marginTop: 16, justifyContent: "center", alignItems: "center" }}>
          <button className="btn" disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}>← Précédent</button>
          <span style={{ fontSize: 13, color: "#4b5563" }}>
            Page {page} / {pages}
          </span>
          <button className="btn" disabled={page >= pages}
            onClick={() => setPage((p) => p + 1)}>Suivant →</button>
        </div>
      )}

      {selected && <DetailModal s={selected} onClose={() => setSelected(null)} onUpdate={load} />}
    </>
  );
}

function DetailModal({ s, onClose, onUpdate }) {
  const [statut, setStatut] = useState(s.statut);
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    await api.modifierSignalement(s.id, { statut });
    setSaving(false);
    onUpdate();
    onClose();
  }

  return (
    <div onClick={onClose} style={{
      position: "fixed", inset: 0, background: "rgba(21,41,63,0.45)",
      display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000,
    }}>
      <div onClick={(e) => e.stopPropagation()} style={{
        background: "#fff", borderRadius: 16, padding: 28, width: 460, maxWidth: "92vw",
        boxShadow: "0 20px 60px rgba(0,0,0,0.25)",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
          <h2 style={{ fontSize: 19 }}>{s.titre}</h2>
          <button onClick={onClose} style={{ background: "none", border: "none", fontSize: 22, color: "#8b8f98" }}>×</button>
        </div>

        <div style={{ display: "flex", gap: 8, margin: "12px 0" }}>
          <CategorieBadge categorie={s.categorie} />
          <StatutBadge statut={s.statut} />
          {s.anomalie && <span className="badge alert">⚠ Suspect IA</span>}
        </div>

        {s.photo_url && (
          <img src={s.photo_url} alt="" style={{ width: "100%", height: 180, objectFit: "cover", borderRadius: 10, marginBottom: 12 }} />
        )}

        <p style={{ fontSize: 14, color: "#4b5563", lineHeight: 1.6, marginBottom: 16 }}>
          {s.description}
        </p>

        <div style={{ fontSize: 13, color: "#4b5563", display: "grid", gap: 6, marginBottom: 16 }}>
          <div><strong>Quartier :</strong> {s.quartier}</div>
          <div><strong>Citoyen :</strong> {s.citoyen_nom}</div>
          <div><strong>Agent :</strong> {s.agent_nom || "Non assigné"}</div>
          <div><strong>Date :</strong> {formatDate(s.date_creation)}</div>
          <div><strong>Confiance classification :</strong> {Math.round(s.score_confiance * 100)}%</div>
        </div>

        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <select className="select" value={statut} onChange={(e) => setStatut(e.target.value)} style={{ flex: 1 }}>
            <option>Nouveau</option>
            <option>En cours</option>
            <option>Résolu</option>
          </select>
          <button className="btn primary" onClick={save} disabled={saving}>
            {saving ? "…" : "Enregistrer"}
          </button>
        </div>
      </div>
    </div>
  );
}
