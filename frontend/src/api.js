// En développement local : "/api" (proxy Vite vers localhost:5000)
// En production (Vercel) : l'URL du backend Render, via VITE_API_URL
const BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : "/api";

async function req(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: "Erreur serveur" }));
    throw new Error(err.error || `Erreur ${res.status}`);
  }
  return res.json();
}

export const api = {
  login: (email, password) =>
    req("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  health: () => req("/health"),

  // Stats
  overview: () => req("/stats/overview"),
  parCategorie: () => req("/stats/par-categorie"),
  parStatut: () => req("/stats/par-statut"),
  parMois: () => req("/stats/par-mois"),
  parJour: () => req("/stats/par-jour"),
  parQuartier: () => req("/stats/par-quartier"),

  // Signalements
  signalements: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return req(`/signalements${q ? "?" + q : ""}`);
  },
  signalement: (id) => req(`/signalements/${id}`),
  creerSignalement: (data) =>
    req("/signalements", { method: "POST", body: JSON.stringify(data) }),
  modifierSignalement: (id, data) =>
    req(`/signalements/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  supprimerSignalement: (id) =>
    req(`/signalements/${id}`, { method: "DELETE" }),

  // Agents & citoyens
  agents: () => req("/agents"),
  agent: (id) => req(`/agents/${id}`),
  assignations: () => req("/agents/assignations"),
  citoyens: () => req("/citoyens"),

  // ML
  suspects: () => req("/ml/suspects"),
  classification: () => req("/ml/classification"),

  // Export
  exportUrl: (type) => `${BASE}/export/${type}.csv`,

  // Espace citoyen
  citoyenInscription: (data) =>
    req("/citoyen/inscription", { method: "POST", body: JSON.stringify(data) }),
  citoyenConnexion: (email, mot_de_passe) =>
    req("/citoyen/connexion", {
      method: "POST",
      body: JSON.stringify({ email, mot_de_passe }),
    }),
  mesSignalements: (cid) => req(`/citoyen/${cid}/signalements`),
  creerMonSignalement: (cid, data) =>
    req(`/citoyen/${cid}/signalements`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  timeline: (sid) => req(`/citoyen/signalement/${sid}/timeline`),

  // Assistant IA
  assistantSuggestions: () => req("/assistant/suggestions"),
  assistantMessage: (message) =>
    req("/assistant/message", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),
};
