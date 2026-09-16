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

// --- Dépenses / dashboard / répartition (foyer déduit du token, plus besoin de foyer_id) ---
export const getDashboard = () => api.get("/dashboard/");
export const getDepenses = () => api.get("/depenses/");
export const creerDepense = (depense) => api.post("/depenses/", depense);
export const supprimerDepense = (id) => api.delete(`/depenses/${id}`);
export const getBalance = () => api.get("/repartition/balance");
export const getReglements = () => api.get("/repartition/reglements");
export const creerReglement = (reglement) => api.post("/repartition/reglements", reglement);

// --- Catégories et membres du foyer ---
export const getCategories = () => api.get("/categories/");
export const creerCategorie = (categorie) => api.post("/categories/", categorie);
export const getMembresFoyer = () => api.get("/foyer/membres");

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

export default api;
