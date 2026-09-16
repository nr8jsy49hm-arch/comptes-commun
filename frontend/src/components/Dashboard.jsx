import { useEffect, useState } from "react";
import { getDashboard, definirBudget } from "../api";
import { IconeCategorie } from "../iconesCategories";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [editionBudget, setEditionBudget] = useState(false);
  const [montantBudget, setMontantBudget] = useState("");

  const charger = () => getDashboard().then((res) => setData(res.data));

  useEffect(() => {
    charger();
  }, []);

  if (!data) return null;

  const moisEnCours = new Date().toLocaleDateString("fr-FR", {
    month: "long",
    year: "numeric",
  });

  const handleDefinirBudget = async (e) => {
    e.preventDefault();
    if (!montantBudget) return;
    await definirBudget(parseFloat(montantBudget));
    setMontantBudget("");
    setEditionBudget(false);
    await charger();
  };

  return (
    <div className="dashboard">
      <span className="dashboard-total">
        <strong>Dépensé en {moisEnCours}</strong>
        {data.total_mois.toFixed(2)} €
      </span>

      <div className="budget-bloc">
        {data.budget_mois == null ? (
          editionBudget ? (
            <form onSubmit={handleDefinirBudget} className="budget-form">
              <input
                type="number"
                step="0.01"
                placeholder="Budget du mois (€)"
                value={montantBudget}
                onChange={(e) => setMontantBudget(e.target.value)}
                autoFocus
                required
              />
              <button type="submit">Valider</button>
            </form>
          ) : (
            <button type="button" className="lien" onClick={() => setEditionBudget(true)}>
              Définir un budget pour ce mois
            </button>
          )
        ) : (
          <>
            <div className="reste-a-vivre">
              <span>Reste à vivre</span>
              <span
                className={
                  data.reste_a_vivre < 0 ? "reste-negatif" : "reste-positif"
                }
              >
                {data.reste_a_vivre.toFixed(2)} €
              </span>
            </div>
            <p className="budget-souscription">
              Budget du mois : {data.budget_mois.toFixed(2)} €{" — "}
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

      {data.balances.length > 0 && (
        <>
          <h3>Balance</h3>
          <ul>
            {data.balances.map((b) => (
              <li key={b.utilisateur_id}>
                {b.solde > 0
                  ? `${b.nom} a payé ${b.solde.toFixed(2)} € de plus que sa part`
                  : b.solde < 0
                  ? `${b.nom} doit ${Math.abs(b.solde).toFixed(2)} €`
                  : `${b.nom} est à jour`}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
