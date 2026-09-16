import { useEffect, useState } from "react";
import { creerDepense, getCategories, creerCategorie, getMembresFoyer } from "../api";

function getUtilisateurStocke() {
  const raw = localStorage.getItem("utilisateur");
  return raw ? JSON.parse(raw) : null;
}

export default function DepenseForm({ onDepenseCreee }) {
  const utilisateur = getUtilisateurStocke();

  const [montant, setMontant] = useState("");
  const [note, setNote] = useState("");
  const [categories, setCategories] = useState([]);
  const [membres, setMembres] = useState([]);
  const [categorieId, setCategorieId] = useState("");
  const [payeurId, setPayeurId] = useState(utilisateur?.id || "");
  const [nouvelleCategorie, setNouvelleCategorie] = useState("");

  const chargerCategories = async () => {
    const res = await getCategories();
    setCategories(res.data);
    // Sélectionne la première catégorie par défaut si aucune n'est choisie
    if (res.data.length > 0 && !categorieId) {
      setCategorieId(res.data[0].id);
    }
  };

  useEffect(() => {
    chargerCategories();
    getMembresFoyer().then((res) => setMembres(res.data));
  }, []);

  const handleAjouterCategorie = async () => {
    if (!nouvelleCategorie.trim()) return;
    const res = await creerCategorie({ nom: nouvelleCategorie.trim() });
    setNouvelleCategorie("");
    await chargerCategories();
    setCategorieId(res.data.id);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!categorieId || !payeurId) return;
    await creerDepense({
      montant: parseFloat(montant),
      date: new Date().toISOString().slice(0, 10),
      note,
      categorie_id: categorieId,
      payeur_id: payeurId,
    });
    setMontant("");
    setNote("");
    onDepenseCreee?.();
  };

  return (
    <form onSubmit={handleSubmit} className="depense-form">
      <h3>Ajouter une dépense</h3>

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

      {/* Ajout rapide d'une nouvelle catégorie sans quitter le formulaire */}
      <div className="ajout-categorie">
        <input
          type="text"
          placeholder="Nouvelle catégorie..."
          value={nouvelleCategorie}
          onChange={(e) => setNouvelleCategorie(e.target.value)}
        />
        <button type="button" className="lien" onClick={handleAjouterCategorie}>
          + Ajouter catégorie
        </button>
      </div>

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

      <button type="submit">Ajouter</button>
    </form>
  );
}
