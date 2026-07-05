export function catClass(categorie) {
  const map = {
    "Voirie": "cat-voirie",
    "Éclairage": "cat-eclairage",
    "Propreté": "cat-proprete",
    "Espaces verts": "cat-espaces",
    "Sécurité": "cat-securite",
  };
  return map[categorie] || "cat-voirie";
}

export function statutClass(statut) {
  const map = {
    "Résolu": "st-resolu",
    "En cours": "st-encours",
    "Nouveau": "st-nouveau",
  };
  return map[statut] || "st-nouveau";
}

export const CAT_COLORS = {
  "Voirie": "#1e3a5f",
  "Éclairage": "#d97706",
  "Propreté": "#0891b2",
  "Espaces verts": "#059669",
  "Sécurité": "#dc2626",
};

export function formatDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function CategorieBadge({ categorie }) {
  return <span className={`badge ${catClass(categorie)}`}>{categorie}</span>;
}

export function StatutBadge({ statut }) {
  return <span className={`badge ${statutClass(statut)}`}>{statut}</span>;
}
