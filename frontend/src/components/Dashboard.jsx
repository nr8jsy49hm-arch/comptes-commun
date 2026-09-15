import { useEffect, useState } from "react";
import { getDashboard } from "../api";

export default function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    getDashboard().then((res) => setData(res.data));
  }, []);

  if (!data) return <p>Chargement du tableau de bord...</p>;

  return (
    <div className="dashboard">
      <h2>Tableau de bord — {new Date().toLocaleDateString("fr-FR", { month: "long", year: "numeric" })}</h2>

      <div className="dashboard-total">
        <strong>Total du mois :</strong> {data.total_mois.toFixed(2)} €
      </div>

      <h3>Par catégorie</h3>
      <ul>
        {Object.entries(data.par_categorie).map(([cat, montant]) => (
          <li key={cat}>
            {cat} : {montant.toFixed(2)} €
          </li>
        ))}
      </ul>

      <h3>Balance</h3>
      <ul>
        {data.balances.map((b) => (
          <li key={b.utilisateur_id}>
            {b.nom} :{" "}
            {b.solde > 0
              ? `on lui doit ${b.solde.toFixed(2)} €`
              : `doit ${Math.abs(b.solde).toFixed(2)} €`}
          </li>
        ))}
      </ul>
    </div>
  );
}
