import { useState } from "react";
import { creerDepense } from "../api";

export default function DepenseForm({ onDepenseCreee }) {
  const [montant, setMontant] = useState("");
  const [note, setNote] = useState("");
  const [categorieId, setCategorieId] = useState(1);
  const [payeurId, setPayeurId] = useState(1);

  const handleSubmit = async (e) => {
    e.preventDefault();
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
      {/* Les selects catégorie/payeur seront branchés sur de vraies données une fois les endpoints associés créés */}
      <button type="submit">Ajouter</button>
    </form>
  );
}
