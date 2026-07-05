import { useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Carte from "./pages/Carte";
import Signalements from "./pages/Signalements";
import ML from "./pages/ML";
import Agents from "./pages/Agents";
import Parametres from "./pages/Parametres";
import CitizenHome from "./pages/CitizenHome";
import CitizenAuth from "./pages/CitizenAuth";
import CitizenDashboard from "./pages/CitizenDashboard";
import "./citizen.css";

// L'application a deux espaces :
//  - espace citoyen (public, moderne) : accueil, auth, mes signalements
//  - espace admin (console municipale) : dashboard, carte, ML, agents…
// On bascule vers l'admin via un lien discret en bas de l'accueil.

export default function App() {
  // "home" | "auth" | "citizen" | "admin"
  const [view, setView] = useState("home");
  const [authMode, setAuthMode] = useState("login");
  const [citoyen, setCitoyen] = useState(null);
  const [admin, setAdmin] = useState(null);

  // -------- Espace ADMIN --------
  if (view === "admin") {
    if (!admin) {
      return (
        <>
          <Login onLogin={setAdmin} />
          <button
            onClick={() => setView("home")}
            style={{
              position: "fixed", bottom: 20, left: "50%", transform: "translateX(-50%)",
              background: "rgba(255,255,255,0.15)", color: "#fff", border: "1px solid rgba(255,255,255,0.3)",
              padding: "8px 18px", borderRadius: 10, cursor: "pointer", backdropFilter: "blur(6px)",
              fontSize: 13, zIndex: 2000,
            }}
          >
            ← Retour à l'espace citoyen
          </button>
        </>
      );
    }
    return (
      <div className="app">
        <Sidebar onLogout={() => { setAdmin(null); setView("home"); }} user={admin} />
        <main className="main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/carte" element={<Carte />} />
            <Route path="/signalements" element={<Signalements />} />
            <Route path="/ml" element={<ML />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/parametres" element={<Parametres />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    );
  }

  // -------- Espace CITOYEN --------
  if (view === "auth") {
    return (
      <CitizenAuth
        defaultMode={authMode}
        onBack={() => setView("home")}
        onAuth={(c) => { setCitoyen(c); setView("citizen"); }}
      />
    );
  }

  if (view === "citizen" && citoyen) {
    return (
      <CitizenDashboard
        user={citoyen}
        onHome={() => setView("home")}
        onLogout={() => { setCitoyen(null); setView("home"); }}
      />
    );
  }

  // Accueil public
  return (
    <>
      <CitizenHome
        user={citoyen}
        onStart={() => { setAuthMode("register"); setView(citoyen ? "citizen" : "auth"); }}
        onLogin={() => { setAuthMode("login"); setView("auth"); }}
        onDashboard={() => setView("citizen")}
        onLogout={() => setCitoyen(null)}
      />
      <button
        onClick={() => setView("admin")}
        style={{
          position: "fixed", bottom: 18, right: 18,
          background: "rgba(21,41,63,0.6)", color: "rgba(255,255,255,0.9)",
          border: "1px solid rgba(255,255,255,0.25)", padding: "8px 16px",
          borderRadius: 10, cursor: "pointer", backdropFilter: "blur(8px)",
          fontSize: 13, zIndex: 2000,
        }}
      >
        🔒 Accès municipalité
      </button>
    </>
  );
}
