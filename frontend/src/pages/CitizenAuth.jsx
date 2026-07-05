import { useState } from "react";
import { api } from "../api";

export default function CitizenAuth({ onAuth, onBack, defaultMode = "login" }) {
  const [mode, setMode] = useState(defaultMode);
  const [form, setForm] = useState({
    prenom: "", nom: "", email: "citoyen@cityreport.ma",
    telephone: "", mot_de_passe: "citoyen",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function set(k, v) { setForm((f) => ({ ...f, [k]: v })); }

  async function submit() {
    setError("");
    setLoading(true);
    try {
      if (mode === "login") {
        const res = await api.citoyenConnexion(form.email, form.mot_de_passe);
        onAuth(res.citoyen);
      } else {
        const res = await api.citoyenInscription(form);
        // Connexion automatique après inscription
        const conn = await api.citoyenConnexion(form.email, form.mot_de_passe);
        onAuth(conn.citoyen);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="citizen-root">
      <div className="citizen-bg" />

      <nav className="citizen-nav">
        <div className="brand" style={{ cursor: "pointer" }} onClick={onBack}>
          <div className="brand-logo">C</div>
          CityReport
        </div>
        <button className="gbtn ghost" onClick={onBack}>← Accueil</button>
      </nav>

      <div className="auth-wrap">
        <div className="glass-panel">
          <h2>{mode === "login" ? "Bon retour" : "Créer un compte"}</h2>
          <p className="sub">
            {mode === "login"
              ? "Connectez-vous pour suivre vos signalements"
              : "Rejoignez CityReport en quelques secondes"}
          </p>

          {error && <div className="gerror">{error}</div>}

          {mode === "register" && (
            <>
              <div style={{ display: "flex", gap: 12 }}>
                <div className="gfield" style={{ flex: 1 }}>
                  <label>Prénom</label>
                  <input value={form.prenom} onChange={(e) => set("prenom", e.target.value)}
                    placeholder="Taha" />
                </div>
                <div className="gfield" style={{ flex: 1 }}>
                  <label>Nom</label>
                  <input value={form.nom} onChange={(e) => set("nom", e.target.value)}
                    placeholder="Sbai" />
                </div>
              </div>
              <div className="gfield">
                <label>Téléphone (optionnel)</label>
                <input value={form.telephone} onChange={(e) => set("telephone", e.target.value)}
                  placeholder="0612345678" />
              </div>
            </>
          )}

          <div className="gfield">
            <label>Email</label>
            <input type="email" value={form.email}
              onChange={(e) => set("email", e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && submit()}
              placeholder="vous@email.ma" />
          </div>
          <div className="gfield">
            <label>Mot de passe</label>
            <input type="password" value={form.mot_de_passe}
              onChange={(e) => set("mot_de_passe", e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && submit()}
              placeholder="••••••" />
          </div>

          <button className="gbtn solid wide" onClick={submit} disabled={loading}
            style={{ marginTop: 8 }}>
            {loading ? "Un instant…" : mode === "login" ? "Se connecter" : "Créer mon compte"}
          </button>

          <div className="auth-switch">
            {mode === "login" ? (
              <>Pas encore de compte ?{" "}
                <button onClick={() => { setMode("register"); setError(""); }}>
                  Inscrivez-vous
                </button>
              </>
            ) : (
              <>Déjà inscrit ?{" "}
                <button onClick={() => { setMode("login"); setError(""); }}>
                  Connectez-vous
                </button>
              </>
            )}
          </div>

          {mode === "login" && (
            <div style={{ marginTop: 18, padding: 12, background: "rgba(255,255,255,0.08)",
              borderRadius: 10, fontSize: 12, color: "rgba(255,255,255,0.7)", textAlign: "center" }}>
              Démo — email <strong>citoyen@cityreport.ma</strong> · mot de passe <strong>citoyen</strong>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
