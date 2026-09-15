import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({ baseURL: API_URL });

// FOYER_ID en dur pour le MVP perso — à remplacer par l'auth plus tard
export const FOYER_ID = 1;

export const getDashboard = () =>
  api.get("/dashboard/", { params: { foyer_id: FOYER_ID } });

export const getDepenses = () =>
  api.get("/depenses/", { params: { foyer_id: FOYER_ID } });

export const creerDepense = (depense) =>
  api.post("/depenses/", depense, { params: { foyer_id: FOYER_ID } });

export const supprimerDepense = (id) => api.delete(`/depenses/${id}`);

export const getBalance = () =>
  api.get("/repartition/balance", { params: { foyer_id: FOYER_ID } });

export default api;
