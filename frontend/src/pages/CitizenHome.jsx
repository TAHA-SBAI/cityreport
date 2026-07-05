import { useEffect, useState } from "react";
import { api } from "../api";
import ChatBot from "../components/ChatBot";

export default function CitizenHome({ onStart, onLogin, user, onDashboard, onLogout }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.overview().then(setStats).catch(() => {});
  }, []);

  return (
    <div className="citizen-root">
      <div className="citizen-bg" />

      <nav className="citizen-nav">
        <div className="brand">
          <div className="brand-logo">C</div>
          CityReport
        </div>
        <div className="citizen-nav-actions">
          {user ? (
            <>
              <span className="who">Bonjour, {user.prenom}</span>
              <button className="gbtn solid" onClick={onDashboard}>
                Mon espace
              </button>
              <button className="gbtn ghost" onClick={onLogout}>Déconnexion</button>
            </>
          ) : (
            <>
              <button className="gbtn ghost" onClick={onLogin}>Se connecter</button>
              <button className="gbtn solid" onClick={onStart}>Signaler</button>
            </>
          )}
        </div>
      </nav>

      <header className="hero">
        <h1>
          Votre ville vous écoute.<br />
          Signalez, <span className="accent">on s'occupe du reste.</span>
        </h1>
        <p>
          Un lampadaire en panne, un nid-de-poule, un dépôt sauvage ? Signalez-le en
          quelques secondes. Notre intelligence artificielle classe automatiquement
          votre demande et l'oriente vers le bon service municipal.
        </p>
        <div className="hero-cta">
          <button className="gbtn solid" onClick={user ? onDashboard : onStart}>
            📍 Faire un signalement
          </button>
          {!user && (
            <button className="gbtn ghost" onClick={onLogin}>
              J'ai déjà un compte
            </button>
          )}
        </div>
      </header>

      {stats && (
        <div className="glass-stats">
          <div className="glass-card">
            <div className="num">{stats.total.toLocaleString("fr-FR")}</div>
            <div className="lbl">Signalements traités</div>
          </div>
          <div className="glass-card">
            <div className="num">{stats.taux_resolution}%</div>
            <div className="lbl">Taux de résolution</div>
          </div>
          <div className="glass-card">
            <div className="num">{stats.nb_agents}</div>
            <div className="lbl">Agents mobilisés</div>
          </div>
          <div className="glass-card">
            <div className="num">5</div>
            <div className="lbl">Services couverts</div>
          </div>
        </div>
      )}

      <section className="steps">
        <div className="step">
          <div className="step-ico">📸</div>
          <h3>1. Décrivez</h3>
          <p>
            Prenez une photo, ajoutez une description et placez le point sur la
            carte. C'est tout.
          </p>
        </div>
        <div className="step">
          <div className="step-ico">🤖</div>
          <h3>2. L'IA classe</h3>
          <p>
            Notre modèle identifie automatiquement la catégorie du problème et
            détecte les doublons.
          </p>
        </div>
        <div className="step">
          <div className="step-ico">✅</div>
          <h3>3. Suivez</h3>
          <p>
            Suivez l'avancement de votre signalement en temps réel, du dépôt
            jusqu'à la résolution.
          </p>
        </div>
      </section>

      <ChatBot />
    </div>
  );
}
