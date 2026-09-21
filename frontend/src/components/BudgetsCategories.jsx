import { useEffect, useState } from "react";
import { Plus, X } from "lucide-react";
import { getBudgetsCategories, definirBudgetCategorie, supprimerBudgetCategorie, getCategories } from "../api";
import { IconeCategorie } from "../iconesCategories";

export default function BudgetsCategories() {
  const [enveloppes, setEnveloppes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [formOuvert, setFormOuvert] = useState(false);
  const [categorieId, setCategorieId] = useState("");
  const [montant, setMontant] = useState("");

  const charger = async () => {
    const [enveloppesRes, categoriesRes] = await Promise.all([getBudgetsCategories(), getCategories()]);
    setEnveloppes(enveloppesRes.data);
    setCategories(categoriesRes.data);
  };

  useEffect(() => {
    charger();
  }, []);

  const categoriesDisponibles = categories.filter(
    (c) => !enveloppes.some((e) => e.categorie_id === c.id)
  );

  const handleCreer = async (e) => {
    e.preventDefault();
    if (!categorieId || !montant) return;
    await definirBudgetCategorie(Number(categorieId), parseFloat(montant));
    setCategorieId("");
    setMontant("");
    setFormOuvert(false);
    await charger();
  };

  const handleSupprimer = async (categorieId) => {
    await supprimerBudgetCategorie(categorieId);
    await charger();
  };

  if (enveloppes.length === 0 && categories.length === 0) return null;

  return (
    <div className="dashboard enveloppes">
      <h3>Budgets par catégorie</h3>
      <p className="cle-repartition-intro">
        Des enveloppes en plus du budget global — utile pour surveiller un poste en particulier
        (ex : 300 € max pour les courses).
      </p>

      {enveloppes.length > 0 && (
        <ul className="enveloppes-liste">
          {enveloppes.map((env) => {
            const pourcentage = env.montant > 0 ? Math.min(100, (env.depense_actuelle / env.montant) * 100) : 0;
            const depassee = env.reste < 0;
            return (
              <li key={env.categorie_id}>
                <div className="objectif-entete">
                  <span className="ligne-categorie">
                    <IconeCategorie nom={env.categorie_nom} />
                    {env.categorie_nom}
                  </span>
                  <button
                    type="button"
                    className="tableau-supprimer"
                    onClick={() => handleSupprimer(env.categorie_id)}
                    aria-label="Supprimer cette enveloppe"
                  >
                    <X size={14} strokeWidth={2} />
                  </button>
                </div>
                <div className="objectif-barre">
                  <div
                    className={`objectif-barre-remplie${depassee ? " enveloppe-barre-depassee" : ""}`}
                    style={{ width: `${pourcentage}%` }}
                  />
                </div>
                <div className="objectif-details">
                  <span>
                    {env.depense_actuelle.toFixed(2)} € / {env.montant.toFixed(2)} €
                  </span>
                  <span className={depassee ? "reste-negatif" : "reste-positif"}>
                    {depassee
                      ? `Dépassée de ${Math.abs(env.reste).toFixed(2)} €`
                      : `Reste ${env.reste.toFixed(2)} €`}
                  </span>
                </div>
              </li>
            );
          })}
        </ul>
      )}

      {categoriesDisponibles.length > 0 &&
        (formOuvert ? (
          <form onSubmit={handleCreer} className="objectif-form">
            <label>
              Catégorie
              <select value={categorieId} onChange={(e) => setCategorieId(e.target.value)} required>
                <option value="">Choisir...</option>
                {categoriesDisponibles.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.nom}
                  </option>
                ))}
              </select>
            </label>
            <input
              type="number"
              step="0.01"
              placeholder="Montant de l'enveloppe (€)"
              value={montant}
              onChange={(e) => setMontant(e.target.value)}
              required
            />
            <button type="submit">Créer l'enveloppe</button>
          </form>
        ) : (
          <button type="button" className="lien" onClick={() => setFormOuvert(true)}>
            <Plus size={14} strokeWidth={2} style={{ verticalAlign: -2, marginRight: 4 }} />
            Nouvelle enveloppe
          </button>
        ))}
    </div>
  );
}
