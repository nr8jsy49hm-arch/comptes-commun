import { useEffect, useState } from "react";
import { getMembresFoyer, creerReglement, getReglements } from "../api";

function getUtilisateurStocke() {
  const raw = localStorage.getItem("utilisateur");
  return raw ? JSON.parse(raw) : null;
}

export default function Reglement({ onReglementCree }) {
  const utilisateur = getUtilisateurStocke();
  const [autresMembres, setAutresMembres] = useState([]);
  const [destinataireId, setDestinataireId] = useState("");
  const [membresParId, setMembresParId] = useState({});
  const [montant, setMontant] = useState("");
  const [historique, setHistorique] = useState([]);
  const [chargement, setChargement] = useState(false);

  const charger = async () => {
    const [membresRes, reglementsRes] = await Promise.all([
      getMembresFoyer(),
      getReglements(),
    ]);
    const autres = membresRes.data.filter((m) => m.id !== utilisateur.id);
    setAutresMembres(autres);
    setMembresParId(Object.fromEntries(membresRes.data.map((m) => [m.id, m.nom])));
    if (autres.length > 0 && !destinataireId) {
      setDestinataireId(autres[0].id);
    }
    setHistorique(reglementsRes.data);
  };

  useEffect(() => {
    charger();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!destinataireId || !montant) return;
    setChargement(true);
    try {
      await creerReglement({
        montant: parseFloat(montant),
        date: new Date().toISOString().slice(0, 10),
        de_utilisateur_id: utilisateur.id,
        vers_utilisateur_id: Number(destinataireId),
      });
      setMontant("");
      await charger();
      onReglementCree?.();
    } finally {
      setChargement(false);
    }
  };

  if (autresMembres.length === 0) {
    return null; // seul dans le foyer pour l'instant
  }

  return (
    <div className="reglement">
      <h3>Rembourser un membre du foyer</h3>

      <form onSubmit={handleSubmit} className="reglement-form">
        {autresMembres.length > 1 ? (
          <label>
            À qui ?
            <select value={destinataireId} onChange={(e) => setDestinataireId(e.target.value)}>
              {autresMembres.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.nom}
                </option>
              ))}
            </select>
          </label>
        ) : (
          <p className="reglement-destinataire-unique">À {autresMembres[0].nom}</p>
        )}
        <input
          type="number"
          step="0.01"
          placeholder="Montant (€)"
          value={montant}
          onChange={(e) => setMontant(e.target.value)}
          required
        />
        <button type="submit" disabled={chargement}>
          {chargement ? "Enregistrement..." : "Enregistrer le remboursement"}
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
                  ? `versés à ${membresParId[r.vers_utilisateur_id] || "?"}`
                  : r.vers_utilisateur_id === utilisateur.id
                  ? `reçus de ${membresParId[r.de_utilisateur_id] || "?"}`
                  : `entre ${membresParId[r.de_utilisateur_id] || "?"} et ${membresParId[r.vers_utilisateur_id] || "?"}`}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
