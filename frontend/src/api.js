import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({ baseURL: API_URL });

// Ajoute automatiquement le token JWT (s'il existe) à chaque requête
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Déconnecte automatiquement si le token est invalide/expiré
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("utilisateur");
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

// --- Auth ---
export const login = (email, mot_de_passe) => {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", mot_de_passe);
  return api.post("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
};

export const register = (payload) => api.post("/auth/register", payload);

export const getMe = () => api.get("/auth/me");

// --- Gestion du compte ---
export const changerMotDePasse = (mot_de_passe_actuel, nouveau_mot_de_passe) =>
  api.post("/auth/mot-de-passe", { mot_de_passe_actuel, nouveau_mot_de_passe });

export const definirQuestionSecrete = (question, reponse) =>
  api.post("/auth/question-secrete", { question, reponse });

export const getMaQuestionSecrete = () => api.get("/auth/question-secrete");

export const supprimerCompte = (mot_de_passe) =>
  api.delete("/auth/compte", { data: { mot_de_passe } });

export const demanderQuestionSecrete = (email) =>
  api.post("/auth/mot-de-passe-oublie/question", { email });

export const reinitialiserMotDePasse = (email, reponse, nouveau_mot_de_passe) =>
  api.post("/auth/mot-de-passe-oublie/reinitialiser", { email, reponse, nouveau_mot_de_passe });

// --- Vérification d'email ---
export const verifierEmailToken = (token) => api.get(`/auth/verifier-email/${token}`);
export const renvoyerVerificationEmail = () => api.post("/auth/renvoyer-verification");

// --- Dépenses / dashboard / répartition (foyer déduit du token, plus besoin de foyer_id) ---
export const getDashboard = () => api.get("/dashboard/");
export const getDepenses = () => api.get("/depenses/");
export const creerDepense = (depense) => api.post("/depenses/", depense);
export const supprimerDepense = (id) => api.delete(`/depenses/${id}`);
export const getBalance = () => api.get("/repartition/balance");
export const getCleRepartition = () => api.get("/repartition/cle");
export const definirCleRepartition = (parts) => api.post("/repartition/cle", { parts });
export const reinitialiserCleRepartition = () => api.delete("/repartition/cle");
export const getReglements = () => api.get("/repartition/reglements");
export const creerReglement = (reglement) => api.post("/repartition/reglements", reglement);

// --- Catégories et membres du foyer ---
export const getCategories = () => api.get("/categories/");
export const creerCategorie = (categorie) => api.post("/categories/", categorie);
export const renommerCategorie = (id, nom) => api.patch(`/categories/${id}`, { nom });
export const supprimerCategorie = (id) => api.delete(`/categories/${id}`);
export const getMembresFoyer = () => api.get("/foyer/membres");

// --- Invitations (rejoindre un foyer) ---
export const creerInvitation = () => api.post("/foyer/invitations");
export const listerInvitations = () => api.get("/foyer/invitations");
export const revoquerInvitation = (id) => api.delete(`/foyer/invitations/${id}`);
export const verifierInvitation = (token) => api.get(`/auth/invitations/${token}`);

// --- Budget mensuel ---
export const getBudgetCourant = () => api.get("/budgets/mois-courant");
export const definirBudget = (montant) => api.post("/budgets/", { montant });

// --- Historique ---
export const getAnneesDisponibles = () => api.get("/historique/annees");
export const getHistoriqueAnnee = (annee) => api.get(`/historique/${annee}`);
export const getHistoriqueMoisCategories = (annee, mois) =>
  api.get(`/historique/${annee}/${mois}/categories`);

// --- Objectifs d'épargne ---
export const getObjectifs = () => api.get("/objectifs/");
export const creerObjectif = (objectif) => api.post("/objectifs/", objectif);
export const supprimerObjectif = (id) => api.delete(`/objectifs/${id}`);
export const verserObjectif = (id, montant) =>
  api.post(`/objectifs/${id}/versements`, { montant });

// --- Mode solo ---
export const getSoloDashboard = () => api.get("/solo/dashboard");
export const getSoloBudgetCourant = () => api.get("/solo/budgets/mois-courant");
export const definirSoloBudget = (montant) => api.post("/solo/budgets", { montant });
export const getSoloAnneesDisponibles = () => api.get("/solo/historique/annees");
export const getSoloHistoriqueAnnee = (annee) => api.get(`/solo/historique/${annee}`);
export const getSoloHistoriqueMoisCategories = (annee, mois) =>
  api.get(`/solo/historique/${annee}/${mois}/categories`);

// --- Export ---
async function telechargerFichier(url, nomFichier) {
  const res = await api.get(url, { responseType: "blob" });
  const lien = document.createElement("a");
  lien.href = window.URL.createObjectURL(res.data);
  lien.download = nomFichier;
  document.body.appendChild(lien);
  lien.click();
  lien.remove();
}

export const exporterDepensesCsv = () => telechargerFichier("/export/depenses.csv", "depenses-communes.csv");
export const exporterDepensesSoloCsv = () =>
  telechargerFichier("/solo/export/depenses.csv", "depenses-perso.csv");

// --- Alertes ---
export const getAlertes = () => api.get("/alertes/");

export default api;

// Extrait un message lisible d'une erreur API : gère à la fois les erreurs
// FastAPI simples (detail = texte) et les erreurs de validation Pydantic
// (detail = liste d'objets {msg, ...}).
export function extraireErreur(err, messageParDefaut) {
  const detail = err.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join(" ");
  return messageParDefaut;
}
