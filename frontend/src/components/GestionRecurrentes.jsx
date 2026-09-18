import { useEffect, useState } from "react";
import { Repeat, Trash2, Plus } from "lucide-react";
import {
  getDepensesRecurrentes,
  creerDepenseRecurrente,
  modifierDepenseRecurrente,
  supprimerDepenseRecurrente,
  getCategories,
  getMembresFoyer,
} from "../api";

export default function GestionRecurrentes() {
  const [regles, setRegles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [membres, setMembres] = useState([]);
  const [formOuvert, setFormOuvert] = useState(false);
  const [nom, setNom] = useState("");
  const [montant, setMontant] = useState("");
  const [jourDuMois, setJourDuMois] = useState("1");
  const [categorieId, setCategorieId] = useState("");
  const [payeurId, setPayeurId] = useState("");

  const charger = async () => {
    const [reglesRes, categoriesRes, membresRes] = await Promise.all([
      getDepensesRecurrentes(),
      getCategories(),
      getMembresFoyer(),
    ]);
    setRegles(reglesRes.data);
    setCategories(categoriesRes.data);
    setMembres(membresRes.data);
    if (categoriesRes.data.length > 0 && !categorieId) setCategorieId(categoriesRes.data[0].id);
    if (membresRes.data.length > 0 && !payeurId) setPayeurId(membresRes.data[0].id);
  };

  useEffect(() => {
    charger();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCreer = async (e) => {
    e.preventDefault();
    if (!nom || !montant || !categorieId || !payeurId) return;
    await creerDepenseRecurrente({
      nom,
      montant: parseFloat(montant),
      jour_du_mois: parseInt(jourDuMois, 10),
      categorie_id: categorieId,
      payeur_id: payeurId,
    });
    setNom("");
    setMontant("");
    setJourDuMois("1");
    setFormOuvert(false);
    await charger();
  };

  const handleToggleActif = async (regle) => {
    await modifierDepenseRecurrente(regle.id, { actif: !regle.actif });
    await charger();
  };

  const handleSupprimer = async (id) => {
    await supprimerDepenseRecurrente(id);
    await charger();
  };

  return (
    <div className="dashboard recurrentes">
      <h3>Dépenses récurrentes</h3>
      <p className="cle-repartition-intro">
        Loyer, abonnements, factures fixes... elles se recréent automatiquement chaque mois, au
        jour indiqué.
      </p>

      {regles.length > 0 && (
        <ul className="recurrentes-liste">
          {regles.map((r) => (
            <li key={r.id} className={r.actif ? "" : "recurrente-inactive"}>
              <span className="ligne-categorie">
                <Repeat size={14} strokeWidth={1.75} />
                {r.nom}
              </span>
              <span className="recurrente-details">
                {r.montant.toFixed(2)} € — le {r.jour_du_mois}
              </span>
              <span className="categorie-actions">
                <button type="button" className="lien" onClick={() => handleToggleActif(r)}>
                  {r.actif ? "Suspendre" : "Réactiver"}
                </button>
                <button
                  type="button"
                  className="tableau-supprimer"
                  onClick={() => handleSupprimer(r.id)}
                  aria-label="Supprimer"
                >
                  <Trash2 size={14} strokeWidth={1.75} />
                </button>
              </span>
            </li>
          ))}
        </ul>
      )}

      {formOuvert ? (
        <form onSubmit={handleCreer} className="objectif-form">
          <input
            type="text"
            placeholder="Nom (ex : Loyer)"
            value={nom}
            onChange={(e) => setNom(e.target.value)}
            required
          />
          <input
            type="number"
            step="0.01"
            placeholder="Montant (€)"
            value={montant}
            onChange={(e) => setMontant(e.target.value)}
            required
          />
          <label>
            Jour du mois
            <input
              type="number"
              min="1"
              max="31"
              value={jourDuMois}
              onChange={(e) => setJourDuMois(e.target.value)}
            />
          </label>
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
          <label>
            Payé par
            <select value={payeurId} onChange={(e) => setPayeurId(Number(e.target.value))}>
              {membres.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.nom}
                </option>
              ))}
            </select>
          </label>
          <button type="submit">Créer la dépense récurrente</button>
        </form>
      ) : (
        <button type="button" className="lien" onClick={() => setFormOuvert(true)}>
          <Plus size={14} strokeWidth={2} style={{ verticalAlign: -2, marginRight: 4 }} />
          Nouvelle dépense récurrente
        </button>
      )}
    </div>
  );
}
