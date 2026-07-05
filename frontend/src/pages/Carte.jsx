import { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { api } from "../api";
import { CAT_COLORS, CategorieBadge, StatutBadge } from "../components/badges";

const FES_CENTER = [34.0331, -5.0003];

export default function Carte() {
  const [items, setItems] = useState([]);
  const [filtreCat, setFiltreCat] = useState("");
  const [showSuspects, setShowSuspects] = useState(false);

  useEffect(() => {
    api.signalements({ limit: 200 }).then((r) => setItems(r.items));
  }, []);

  const filtres = items.filter((s) => {
    if (filtreCat && s.categorie !== filtreCat) return false;
    if (showSuspects && !s.anomalie) return false;
    return true;
  });

  return (
    <>
      <div className="page-header">
        <h1>Carte interactive</h1>
        <p>Localisation géographique des signalements</p>
      </div>

      <div className="toolbar">
        <select className="select" value={filtreCat}
          onChange={(e) => setFiltreCat(e.target.value)}>
          <option value="">Toutes les catégories</option>
          {Object.keys(CAT_COLORS).map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <button
          className={"btn" + (showSuspects ? " gold" : "")}
          onClick={() => setShowSuspects((v) => !v)}>
          {showSuspects ? "◉ Suspects uniquement" : "○ Afficher suspects"}
        </button>
        <span style={{ marginLeft: "auto", fontSize: 13, color: "#8b8f98" }}>
          {filtres.length} signalement{filtres.length > 1 ? "s" : ""} affiché
          {filtres.length > 1 ? "s" : ""}
        </span>
      </div>

      <div className="map-wrap">
        <MapContainer center={FES_CENTER} zoom={13} style={{ height: "100%", width: "100%" }}>
          <TileLayer
            attribution='&copy; OpenStreetMap'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {filtres.map((s) => (
            <CircleMarker
              key={s.id}
              center={[s.latitude, s.longitude]}
              radius={s.anomalie ? 9 : 6}
              pathOptions={{
                color: s.anomalie ? "#dc2626" : CAT_COLORS[s.categorie] || "#1e3a5f",
                fillColor: s.anomalie ? "#dc2626" : CAT_COLORS[s.categorie] || "#1e3a5f",
                fillOpacity: 0.7,
                weight: s.anomalie ? 2.5 : 1.5,
              }}
            >
              <Popup>
                <div style={{ minWidth: 180 }}>
                  <strong style={{ fontSize: 13 }}>{s.titre}</strong>
                  <div style={{ margin: "8px 0", display: "flex", gap: 6, flexWrap: "wrap" }}>
                    <CategorieBadge categorie={s.categorie} />
                    <StatutBadge statut={s.statut} />
                  </div>
                  <div style={{ fontSize: 12, color: "#4b5563" }}>{s.quartier}</div>
                  {s.anomalie && (
                    <div style={{ marginTop: 6, fontSize: 12, color: "#dc2626", fontWeight: 600 }}>
                      ⚠ Signalement suspect (score {s.score_anomalie})
                    </div>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      <div className="legend">
        {Object.entries(CAT_COLORS).map(([cat, color]) => (
          <span key={cat}>
            <span className="dot" style={{ background: color }} />
            {cat}
          </span>
        ))}
        <span>
          <span className="dot" style={{ background: "#dc2626", borderRadius: "50%" }} />
          Suspect (IA)
        </span>
      </div>
    </>
  );
}
