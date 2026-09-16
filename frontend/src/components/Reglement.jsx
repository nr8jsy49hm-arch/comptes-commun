import { useEffect, useState } from "react";
import { getMembresFoyer, creerReglement, getReglements } from "../api";

function getUtilisateurStocke() {
  const raw = localStorage.getItem("utilisateur");
  return raw ? JSON.parse(raw) : null;
}

export default function Reglement({ onReglementCree }) {
  const utilisateur = getUtilisateurStocke();
  const [autreMembre, setAutreMembre] = useState(null);
  const [montant, setMontant] = useState("");
  const [historique, setHistorique] = useState([]);
  const [chargement, setChargement] = useState(false);

  const charger = async () => {
    const [membresRes, reglementsRes] = await Promise.all([
      getMembresFoyer(),
      getReglements(),
    ]);
    const autre = membresRes.data.find((m) => m.id !== utilisateur.id);
    setAutreMembre(autre || null);
    setHistorique(reglementsRes.data);
  };

  useEffect(() => {
    charger();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!autreMembre || !montant) return;
    setChargement(true);
    try {
      await creerReglement({
        montant: parseFloat(montant),
        date: new Date().toISOString().slice(0, 10),
        de_utilisateur_id: utilisateur.id,
        vers_utilisateur_id: autreMembre.id,
      });
      setMontant("");
      await charger();
      onReglementCree?.();
    } finally {
      setChargement(false);
    }
  };

  if (!autreMembre) {
    return null; // pas de partenaire dans le foyer pour l'instant
  }

  return (
    <div className="reglement">
      <h3>Rembourser {autreMembre.nom}</h3>

      <form onSubmit={handleSubmit} className="reglement-form">
        <input
          type="number"
          step="0.01"
          placeholder="Montant (€)"
          value={montant}
          onChange={(e) => setMontant(e.target.value)}
          required
        />
        <button type="submit" disabled={chargement}>
          {chargement ? "Enregistrement..." : `Enregistrer le remboursement à ${autreMembre.nom}`}
        </button>
      </form>

      {historique.length > 0 && (
        <>
          <h4>Historique des règlements</h4>
          <ul>
            {historique.map((r) => (
              <li key={r.id}>
                {r.date} — {r.montant.toFixed(2)} €{" "}
                {r.de_utilisateur_id === utilisateur.id
                  ? `versés à ${autreMembre.nom}`
                  : `reçus de ${autreMembre.nom}`}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
