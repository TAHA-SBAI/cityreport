import { useEffect, useState } from "react";
import { api } from "../api";
import { CAT_COLORS, CategorieBadge } from "../components/badges";

const QUARTIERS = [
  "Fès Médina", "Agdal", "Saiss", "Narjiss",
  "Ville Nouvelle", "Zouagha", "Montfleuri",
];

export default function Parametres() {
  const [citoyens, setCitoyens] = useState([]);
  const [titre, setTitre] = useState("");
  const [description, setDescription] = useState("");
  const [quartier, setQuartier] = useState(QUARTIERS[0]);
  const [citoyenId, setCitoyenId] = useState("");
  const [resultat, setResultat] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.citoyens().then((c) => {
      setCitoyens(c);
      if (c.length) setCitoyenId(c[0].id);
    });
  }, []);

  async function creer() {
    if (!titre || !citoyenId) return;
    setSaving(true);
    setResultat(null);
    // Coordonnées approximatives selon le quartier choisi
    const coords = {
      "Fès Médina": [34.064, -4.977], "Agdal": [34.033, -5.0],
      "Saiss": [34.015, -4.99], "Narjiss": [34.042, -4.955],
      "Ville Nouvelle": [34.037, -5.004], "Zouagha": [34.055, -5.02],
      "Montfleuri": [34.029, -4.983],
    }[quartier];
    const r = await api.creerSignalement({
      titre, description, quartier,
      latitude: coords[0] + (Math.random() - 0.5) * 0.01,
      longitude: coords[1] + (Math.random() - 0.5) * 0.01,
      citoyen_id: Number(citoyenId),
    });
    setResultat(r);
    setTitre(""); setDescription("");
    setSaving(false);
  }

  return (
    <>
      <div className="page-header">
        <h1>Paramètres</h1>
        <p>Configuration et test du module de classification</p>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-title">Tester un signalement</div>
          <p style={{ fontSize: 13, color: "#8b8f98", marginBottom: 16 }}>
            Crée un signalement et observe la catégorie prédite en direct par le module IA.
          </p>

          <div className="field" style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 13, fontWeight: 500, color: "#4b5563", display: "block", marginBottom: 6 }}>Titre</label>
            <input className="input" style={{ width: "100%" }} value={titre}
              onChange={(e) => setTitre(e.target.value)}
              placeholder="Ex : Lampadaire en panne avenue Hassan II" />
          </div>

          <div className="field" style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 13, fontWeight: 500, color: "#4b5563", display: "block", marginBottom: 6 }}>Description</label>
            <textarea className="input" style={{ width: "100%", minHeight: 70, resize: "vertical" }}
              value={description} onChange={(e) => setDescription(e.target.value)}
              placeholder="Décrivez le problème…" />
          </div>

          <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
            <select className="select" value={quartier} onChange={(e) => setQuartier(e.target.value)} style={{ flex: 1 }}>
              {QUARTIERS.map((q) => <option key={q}>{q}</option>)}
            </select>
            <select className="select" value={citoyenId} onChange={(e) => setCitoyenId(e.target.value)} style={{ flex: 1 }}>
              {citoyens.map((c) => (
                <option key={c.id} value={c.id}>{c.prenom} {c.nom}</option>
              ))}
            </select>
          </div>

          <button className="btn gold" onClick={creer} disabled={saving || !titre}>
            {saving ? "Analyse en cours…" : "Créer et classifier"}
          </button>

          {resultat && (
            <div style={{
              marginTop: 18, padding: 16, background: "#f4f3ef",
              borderRadius: 10, border: "1px solid #e6e4dd",
            }}>
              <div style={{ fontSize: 12, color: "#8b8f98", marginBottom: 8 }}>
                Résultat de la classification automatique
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <CategorieBadge categorie={resultat.categorie} />
                <span style={{ fontSize: 13, color: "#4b5563" }}>
                  confiance {Math.round(resultat.score_confiance * 100)}%
                </span>
                {resultat.anomalie && (
                  <span className="badge alert">⚠ Marqué suspect</span>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-title">Catégories de la plateforme</div>
          <div style={{ display: "grid", gap: 10 }}>
            {Object.entries(CAT_COLORS).map(([cat, color]) => (
              <div key={cat} style={{
                display: "flex", alignItems: "center", gap: 12,
                padding: "10px 12px", background: "#f4f3ef", borderRadius: 8,
              }}>
                <span style={{ width: 12, height: 12, borderRadius: 3, background: color }} />
                <span style={{ fontSize: 14, fontWeight: 500 }}>{cat}</span>
              </div>
            ))}
          </div>

          <div className="card-title" style={{ marginTop: 24 }}>Exports de données</div>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <a className="btn" href={api.exportUrl("signalements")}>↓ Signalements</a>
            <a className="btn" href={api.exportUrl("citoyens")}>↓ Citoyens</a>
            <a className="btn" href={api.exportUrl("agents")}>↓ Agents</a>
          </div>
        </div>
      </div>
    </>
  );
}
