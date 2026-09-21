export const COULEURS_ACCENT = [
  { id: "laiton", nom: "Laiton", brass: "#b08549", brassDark: "#8c6a39" },
  { id: "ardoise", nom: "Bleu ardoise", brass: "#5c7a99", brassDark: "#47607a" },
  { id: "prune", nom: "Prune", brass: "#8a6a99", brassDark: "#6e5480" },
  { id: "canard", nom: "Bleu canard", brass: "#4a7a7a", brassDark: "#3a6161" },
  { id: "moutarde", nom: "Moutarde", brass: "#c9a227", brassDark: "#a3831f" },
];

export function appliquerCouleurAccent(id) {
  const couleur = COULEURS_ACCENT.find((c) => c.id === id) || COULEURS_ACCENT[0];
  document.documentElement.style.setProperty("--color-brass", couleur.brass);
  document.documentElement.style.setProperty("--color-brass-dark", couleur.brassDark);
}

export function getCouleurAccentInitiale() {
  return localStorage.getItem("couleur_accent") || "laiton";
}
