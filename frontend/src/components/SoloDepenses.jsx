import { useEffect, useState } from "react";
import { Download, Printer } from "lucide-react";
import {
  getSoloDashboard,
  getCategories,
  creerDepense,
  supprimerDepense,
  getSoloBudgetCourant,
  definirSoloBudget,
  getSoloAnneesDisponibles,
  getSoloHistoriqueAnnee,
  getSoloHistoriqueMoisCategories,
  exporterDepensesSoloCsv,
} from "../api";
import Historique from "./Historique";
import TableauDepenses from "./TableauDepenses";
import { IconeCategorie } from "../iconesCategories";

function getUtilisateurStocke() {
  const raw = localStorage.getItem("utilisateur");
  return raw ? JSON.parse(raw) : null;
}

export default function SoloDepenses() {
  const utilisateur = getUtilisateurStocke();
  const [data, setData] = useState(null);
  const [categories, setCategories] = useState([]);
  const [montant, setMontant] = useState("");
  const [note, setNote] = useState("");
  const [categorieId, setCategorieId] = useState("");
  const [editionBudget, setEditionBudget] = useState(false);
  const [montantBudget, setMontantBudget] = useState("");
  const [refreshHistorique, setRefreshHistorique] = useState(0);

  const charger = async () => {
    const [dashboardRes, categoriesRes] = await Promise.all([
      getSoloDashboard(),
      getCategories(),
    ]);
    setData(dashboardRes.data);
    setCategories(categoriesRes.data);
    if (categoriesRes.data.length > 0 && !categorieId) {
      setCategorieId(categoriesRes.data[0].id);
    }
  };

  useEffect(() => {
    charger();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!montant || !categorieId) return;
    await creerDepense({
      montant: parseFloat(montant),
      date: new Date().toISOString().slice(0, 10),
      note,
      categorie_id: categorieId,
      payeur_id: utilisateur.id,
      partagee: false,
    });
    setMontant("");
    setNote("");
    await charger();
    setRefreshHistorique((k) => k + 1);
  };

  const handleDefinirBudget = async (e) => {
    e.preventDefault();
    if (!montantBudget) return;
    await definirSoloBudget(parseFloat(montantBudget));
    setMontantBudget("");
    setEditionBudget(false);
    await charger();
    setRefreshHistorique((k) => k + 1);
  };

  const handleSupprimer = async (id) => {
    await supprimerDepense(id);
    await charger();
    setRefreshHistorique((k) => k + 1);
  };

  if (!data) return null;

  const moisEnCours = new Date().toLocaleDateString("fr-FR", {
    month: "long",
    year: "numeric",
  });

  const categoriesParId = Object.fromEntries(categories.map((c) => [c.id, c.nom]));

  return (
    <>
      <div className="dashboard solo">
        <p className="solo-intro">
          Tes dépenses personnelles, à part des comptes communs — elles ne comptent
          ni dans le budget, ni dans la répartition avec ton/ta partenaire.
        </p>

        <span className="dashboard-total">
          <strong>Dépensé en perso en {moisEnCours}</strong>
          {data.total_mois.toFixed(2)} €
        </span>

        <div className="budget-bloc">
          {data.budget_mois == null ? (
            editionBudget ? (
              <form onSubmit={handleDefinirBudget} className="budget-form">
                <input
                  type="number"
                  step="0.01"
                  placeholder="Budget perso du mois (€)"
                  value={montantBudget}
                  onChange={(e) => setMontantBudget(e.target.value)}
                  autoFocus
                  required
                />
                <button type="submit">Valider</button>
              </form>
            ) : (
              <button type="button" className="lien" onClick={() => setEditionBudget(true)}>
                Définir un budget perso pour ce mois
              </button>
            )
          ) : (
            <>
              <div className="reste-a-vivre">
                <span>Reste à vivre (perso)</span>
                <span className={data.reste_a_vivre < 0 ? "reste-negatif" : "reste-positif"}>
                  {data.reste_a_vivre.toFixed(2)} €
                </span>
              </div>
              <p className="budget-souscription">
                Budget perso du mois : {data.budget_mois.toFixed(2)} €{" — "}
                {editionBudget ? (
                  <form onSubmit={handleDefinirBudget} className="budget-form budget-form-inline">
                    <input
                      type="number"
                      step="0.01"
                      placeholder="Nouveau montant"
                      value={montantBudget}
                      onChange={(e) => setMontantBudget(e.target.value)}
                      autoFocus
                      required
                    />
                    <button type="submit">Valider</button>
                  </form>
                ) : (
                  <button type="button" className="lien" onClick={() => setEditionBudget(true)}>
                    modifier
                  </button>
                )}
              </p>
            </>
          )}
        </div>

        {Object.keys(data.par_categorie).length > 0 && (
          <>
            <h3>Par catégorie</h3>
            <ul>
              {Object.entries(data.par_categorie).map(([cat, montant]) => (
                <li key={cat}>
                  <span className="ligne-categorie">
                    <IconeCategorie nom={cat} />
                    {cat}
                  </span>
                  <span>{montant.toFixed(2)} €</span>
                </li>
              ))}
            </ul>
          </>
        )}

        <form onSubmit={handleSubmit} className="depense-form solo-form">
          <h3>Ajouter une dépense perso</h3>
          <input
            type="number"
            step="0.01"
            placeholder="Montant (€)"
            value={montant}
            onChange={(e) => setMontant(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Note (optionnel)"
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
          <label>
            Catégorie
            <select value={categorieId} onChange={(e) => setCategorieId(Number(e.target.value))}>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.nom}
                </option>
              ))}
            </select>
          </label>
          <button type="submit">Ajouter</button>
        </form>

        {data.depenses.length > 0 && (
          <>
            <div className="liste-depenses-entete">
              <h3>Détail du mois</h3>
              <div className="liste-depenses-export">
                <button type="button" className="lien" onClick={exporterDepensesSoloCsv}>
                  <Download size={14} strokeWidth={2} style={{ verticalAlign: -2, marginRight: 4 }} />
                  CSV
                </button>
                <button type="button" className="lien" onClick={() => window.print()}>
                  <Printer size={14} strokeWidth={2} style={{ verticalAlign: -2, marginRight: 4 }} />
                  Imprimer / PDF
                </button>
              </div>
            </div>
            <TableauDepenses
              depenses={data.depenses}
              categoriesParId={categoriesParId}
              afficherPayeur={false}
              onSupprimer={handleSupprimer}
            />
          </>
        )}
      </div>

      <Historique
        key={refreshHistorique}
        getAnnees={getSoloAnneesDisponibles}
        getAnnee={getSoloHistoriqueAnnee}
        getMoisCategories={getSoloHistoriqueMoisCategories}
      />
    </>
  );
}
