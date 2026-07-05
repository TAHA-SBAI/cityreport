import { useState } from "react";
import { api } from "../api";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("admin@cityreport.ma");
  const [password, setPassword] = useState("admin");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit() {
    setError("");
    setLoading(true);
    try {
      const res = await api.login(email, password);
      onLogin(res.user);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-screen">
      <div className="login-card">
        <div className="brand-logo">C</div>
        <h1>CityReport</h1>
        <p className="muted">Console de gestion municipale</p>

        {error && <div className="error-msg">{error}</div>}

        <div className="field">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submit()}
            placeholder="admin@cityreport.ma"
          />
        </div>
        <div className="field">
          <label>Mot de passe</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submit()}
            placeholder="••••••"
          />
        </div>

        <button
          className="btn primary"
          style={{ width: "100%", justifyContent: "center", marginTop: 8 }}
          onClick={submit}
          disabled={loading}
        >
          {loading ? "Connexion…" : "Se connecter"}
        </button>

        <div className="login-hint">
          Démo — email <strong>admin@cityreport.ma</strong> · mot de passe{" "}
          <strong>admin</strong>
        </div>
      </div>
    </div>
  );
}
