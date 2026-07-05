import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import { api } from "../api";

const FES = [34.0331, -5.0003];

const QUARTIERS = {
  "Fès Médina": [34.064, -4.977], "Agdal": [34.033, -5.0],
  "Saiss": [34.015, -4.99], "Narjiss": [34.042, -4.955],
  "Ville Nouvelle": [34.037, -5.004], "Zouagha": [34.055, -5.02],
  "Montfleuri": [34.029, -4.983],
};

function pillClass(statut) {
  return statut === "Résolu" ? "resolu" : statut === "En cours" ? "encours" : "nouveau";
}

export default function CitizenDashboard({ user, onHome, onLogout }) {
  const [signalements, setSignalements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [openTimeline, setOpenTimeline] = useState(null);

  function load() {
    setLoading(true);
    api.mesSignalements(user.id).then((d) => {
      setSignalements(d);
      setLoading(false);
    });
  }

  useEffect(() => { load(); }, [user.id]);

  return (
    <div className="citizen-root">
      <div className="citizen-bg" />

      <nav className="citizen-nav">
        <div className="brand" style={{ cursor: "pointer" }} onClick={onHome}>
          <div className="brand-logo">C</div>
          CityReport
        </div>
        <div className="citizen-nav-actions">
          <span className="who">{user.prenom} {user.nom}</span>
          <button className="gbtn solid" onClick={() => setShowModal(true)}>
            + Nouveau signalement
          </button>
          <button className="gbtn ghost" onClick={onLogout}>Déconnexion</button>
        </div>
      </nav>

      <div className="citizen-main">
        <h2>Mes signalements</h2>
        <p className="sub">
          {signalements.length > 0
            ? `Vous avez déposé ${signalements.length} signalement${signalements.length > 1 ? "s" : ""}`
            : "Suivez ici l'avancement de vos demandes"}
        </p>

        {loading ? (
          <div className="spinner-light" />
        ) : signalements.length === 0 ? (
          <div className="empty-state">
            <div className="big">📭</div>
            <p>Vous n'avez pas encore de signalement.</p>
            <button className="gbtn solid" style={{ marginTop: 20 }}
              onClick={() => setShowModal(true)}>
              Faire mon premier signalement
            </button>
          </div>
        ) : (
          signalements.map((s) => (
            <div key={s.id} className="report-card">
              {s.photo_url && <img className="report-thumb" src={s.photo_url} alt="" />}
              <div className="report-body">
                <h3>{s.titre}</h3>
                <div className="meta">
                  {s.quartier} · {new Date(s.date_creation).toLocaleDateString("fr-FR",
                    { day: "2-digit", month: "long", year: "numeric" })}
                </div>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 4 }}>
                  <span className={`pill ${pillClass(s.statut)}`}>{s.statut}</span>
                  <span className="pill cat">{s.categorie}</span>
                  {s.urgence && (
                    <span className="pill" style={{ background: "rgba(220,38,38,0.3)", color: "#fecaca" }}>
                      {s.urgence === "police" ? "🚓 Urgence 19" : "🚑 Urgence 15"}
                    </span>
                  )}
                  {s.anomalie && <span className="pill" style={{ background: "rgba(220,38,38,0.25)", color: "#fecaca" }}>⚠ En vérification</span>}
                </div>
                {s.description && (
                  <p style={{ color: "rgba(255,255,255,0.7)", fontSize: 14, margin: "8px 0" }}>
                    {s.description}
                  </p>
                )}
                <button
                  onClick={() => setOpenTimeline(openTimeline === s.id ? null : s.id)}
                  style={{ background: "none", border: "none", color: "#fbbf24",
                    fontWeight: 600, cursor: "pointer", fontSize: 13, padding: 0 }}>
                  {openTimeline === s.id ? "Masquer le suivi ▲" : "Voir le suivi ▼"}
                </button>
                {openTimeline === s.id && <Timeline sid={s.id} statut={s.statut} />}
              </div>
            </div>
          ))
        )}
      </div>

      {showModal && (
        <CreateModal
          user={user}
          onClose={() => setShowModal(false)}
          onCreated={() => { setShowModal(false); load(); }}
        />
      )}
    </div>
  );
}

function Timeline({ sid, statut }) {
  const [entries, setEntries] = useState(null);
  const etapes = ["Nouveau", "En cours", "Résolu"];
  const courant = etapes.indexOf(statut);

  useEffect(() => {
    api.timeline(sid).then(setEntries).catch(() => setEntries([]));
  }, [sid]);

  if (entries === null) return <div className="spinner-light" style={{ margin: "20px auto" }} />;

  // On construit une timeline sur les 3 étapes, en associant les entrées réelles
  return (
    <div className="timeline">
      {etapes.map((etape, i) => {
        const entree = entries.find((e) => e.nouveau_statut === etape);
        const state = i < courant ? "done" : i === courant ? "current" : "todo";
        return (
          <div key={etape} className="tl-item">
            <div className={`tl-dot ${state}`}>
              {state === "done" ? "✓" : state === "current" ? "●" : ""}
            </div>
            <div className="tl-content">
              <div className="tl-status">{etape}</div>
              {entree ? (
                <>
                  <div className="tl-com">{entree.commentaire}</div>
                  <div className="tl-date">
                    {new Date(entree.date_changement).toLocaleDateString("fr-FR",
                      { day: "2-digit", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" })}
                  </div>
                </>
              ) : (
                <div className="tl-com" style={{ opacity: 0.5 }}>En attente</div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function LocationPicker({ position, setPosition }) {
  useMapEvents({
    click(e) {
      setPosition([e.latlng.lat, e.latlng.lng]);
    },
  });
  return position ? <Marker position={position} /> : null;
}

function CreateModal({ user, onClose, onCreated }) {
  const [titre, setTitre] = useState("");
  const [description, setDescription] = useState("");
  const [quartier, setQuartier] = useState("Fès Médina");
  const [position, setPosition] = useState(QUARTIERS["Fès Médina"]);
  const [photoUrl, setPhotoUrl] = useState("");
  const [photoData, setPhotoData] = useState("");   // photo prise/choisie (base64)
  const [urgence, setUrgence] = useState("");        // "", "police", "secours"
  const [saving, setSaving] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  function onPhotoChange(e) {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setPhotoData(reader.result);
    reader.readAsDataURL(file);
  }

  function changeQuartier(q) {
    setQuartier(q);
    setPosition(QUARTIERS[q]);
  }

  async function submit() {
    if (!titre) { setError("Donnez un titre à votre signalement"); return; }
    setError("");
    setSaving(true);
    try {
      const r = await api.creerMonSignalement(user.id, {
        titre, description, quartier, urgence,
        latitude: position[0], longitude: position[1],
        photo_url: photoData || photoUrl || `https://picsum.photos/seed/new${Date.now() % 9999}/400/300`,
      });
      setResult(r);
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        {!result ? (
          <>
            <h2>Nouveau signalement</h2>
            <p className="sub">Décrivez le problème et placez-le sur la carte</p>

            {error && <div className="gerror">{error}</div>}

            <div className="gfield">
              <label>Titre du problème</label>
              <input value={titre} onChange={(e) => setTitre(e.target.value)}
                placeholder="Ex : Lampadaire éteint devant le lycée" />
            </div>

            <div className="gfield">
              <label>Description</label>
              <textarea value={description} onChange={(e) => setDescription(e.target.value)}
                rows={3} placeholder="Donnez des détails utiles aux services municipaux…" />
            </div>

            <div className="gfield">
              <label>Quartier</label>
              <select value={quartier} onChange={(e) => changeQuartier(e.target.value)}>
                {Object.keys(QUARTIERS).map((q) => <option key={q}>{q}</option>)}
              </select>
            </div>

            <div className="gfield">
              <label>Photo</label>
              <label className="photo-btn">
                <input type="file" accept="image/*" capture="environment"
                  onChange={onPhotoChange} style={{ display: "none" }} />
                📷 Prendre / choisir une photo
              </label>
              {photoData && (
                <div className="photo-preview">
                  <img src={photoData} alt="aperçu" />
                  <button type="button" className="photo-remove"
                    onClick={() => setPhotoData("")}>✕</button>
                </div>
              )}
            </div>

            <div className="gfield">
              <label>Ce problème est-il une urgence ?</label>
              <div className="urgence-row">
                <button type="button"
                  className={"urg-opt" + (urgence === "" ? " active" : "")}
                  onClick={() => setUrgence("")}>
                  Non, signalement normal
                </button>
                <button type="button"
                  className={"urg-opt police" + (urgence === "police" ? " active" : "")}
                  onClick={() => setUrgence("police")}>
                  🚓 Police (19)
                </button>
                <button type="button"
                  className={"urg-opt secours" + (urgence === "secours" ? " active" : "")}
                  onClick={() => setUrgence("secours")}>
                  🚑 Secours (15)
                </button>
              </div>
              {urgence && (
                <div className="urg-note">
                  ⚠️ En cas de danger immédiat, appelez directement le{" "}
                  <strong>{urgence === "police" ? "19" : "15"}</strong>.
                  Un bouton d'appel apparaîtra après l'envoi.
                </div>
              )}
            </div>

            <label style={{ display: "block", fontSize: 13, fontWeight: 500,
              color: "rgba(255,255,255,0.85)", marginBottom: 7 }}>
              Emplacement précis
            </label>
            <div className="mini-map">
              <MapContainer center={position} zoom={13} style={{ height: "100%", width: "100%" }}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                <LocationPicker position={position} setPosition={setPosition} />
              </MapContainer>
            </div>
            <div className="map-hint">
              📍 Cliquez sur la carte pour placer précisément le problème
            </div>

            <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
              <button className="gbtn ghost" onClick={onClose} style={{ flex: 1, justifyContent: "center" }}>
                Annuler
              </button>
              <button className="gbtn solid" onClick={submit} disabled={saving}
                style={{ flex: 2, justifyContent: "center" }}>
                {saving ? "Analyse IA en cours…" : "Envoyer le signalement"}
              </button>
            </div>
          </>
        ) : (
          <>
            <h2>Signalement envoyé ✅</h2>
            <p className="sub">Votre demande a été enregistrée et analysée</p>

            <div className="ia-result">
              <span className="ia-ico">🤖</span>
              <span className="ia-txt">
                Notre IA a classé votre signalement dans la catégorie{" "}
                <strong>{result.categorie}</strong>{" "}
                (confiance {Math.round(result.score_confiance * 100)}%).
                {result.anomalie && " Il sera vérifié par un agent."}
              </span>
            </div>

            {urgence && (
              <div className="urg-call">
                <div className="urg-call-title">
                  ⚠️ Vous avez marqué ce signalement comme urgent
                </div>
                <p>
                  Pour une intervention immédiate, contactez directement{" "}
                  {urgence === "police" ? "la police" : "les secours"} :
                </p>
                <a className="urg-call-btn" href={urgence === "police" ? "tel:19" : "tel:15"}>
                  📞 Appeler le {urgence === "police" ? "19 (Police)" : "15 (SAMU)"}
                </a>
              </div>
            )}

            <button className="gbtn solid wide" onClick={onCreated} style={{ marginTop: 24 }}>
              Voir mes signalements
            </button>
          </>
        )}
      </div>
    </div>
  );
}
