import { useEffect, useState } from "react";
import {
  getAnneesDisponibles,
  getHistoriqueAnnee,
  getHistoriqueMoisCategories,
} from "../api";
import { IconeCategorie } from "../iconesCategories";

export default function Historique({
  getAnnees = getAnneesDisponibles,
  getAnnee = getHistoriqueAnnee,
  getMoisCategories = getHistoriqueMoisCategories,
}) {
  const [annees, setAnnees] = useState([]);
  const [anneeSelectionnee, setAnneeSelectionnee] = useState(null);
  const [mois, setMois] = useState([]);
  const [moisOuvert, setMoisOuvert] = useState(null);
  const [categoriesMoisOuvert, setCategoriesMoisOuvert] = useState(null);

  useEffect(() => {
    getAnnees().then((res) => {
      setAnnees(res.data);
      if (res.data.length > 0) setAnneeSelectionnee(res.data[0]);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (anneeSelectionnee == null) return;
    setMoisOuvert(null);
    getAnnee(anneeSelectionnee).then((res) => setMois(res.data));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [anneeSelectionnee]);

  const handleToggleMois = async (m) => {
    if (moisOuvert === m.mois) {
      setMoisOuvert(null);
      return;
    }
    setMoisOuvert(m.mois);
    if (m.nb_depenses > 0) {
      const res = await getMoisCategories(anneeSelectionnee, m.mois);
      setCategoriesMoisOuvert(res.data);
    } else {
      setCategoriesMoisOuvert({});
    }
  };

  const totalAnnee = mois.reduce((acc, m) => acc + m.total_depense, 0);

  return (
    <div className="dashboard historique">
      <div className="historique-header">
        <h3>Historique</h3>
        <select
          value={anneeSelectionnee ?? ""}
          onChange={(e) => setAnneeSelectionnee(Number(e.target.value))}
        >
          {annees.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
      </div>

      <p className="historique-total-annee">
        Total {anneeSelectionnee} : {totalAnnee.toFixed(2)} €
      </p>

      <ul className="historique-liste">
        {mois.map((m) => (
          <li key={m.mois} className="historique-mois">
            <button
              type="button"
              className="historique-mois-header"
              onClick={() => handleToggleMois(m)}
              disabled={m.nb_depenses === 0}
            >
              <span>{m.nom_mois}</span>
              <span className="historique-mois-montants">
                {m.nb_depenses > 0 ? (
                  <>
                    {m.total_depense.toFixed(2)} €
                    {m.reste_a_vivre != null && (
                      <span
                        className={
                          m.reste_a_vivre < 0
                            ? "reste-negatif"
                            : "reste-positif"
                        }
                      >
                        {" "}
                        ({m.reste_a_vivre >= 0 ? "reste " : "dépassé de "}
                        {Math.abs(m.reste_a_vivre).toFixed(2)} €)
                      </span>
                    )}
                  </>
                ) : (
                  <span className="historique-vide">—</span>
                )}
              </span>
            </button>

            {moisOuvert === m.mois && categoriesMoisOuvert && (
              <ul className="historique-categories">
                {Object.entries(categoriesMoisOuvert).map(([cat, montant]) => (
                  <li key={cat}>
                    <span className="ligne-categorie">
                      <IconeCategorie nom={cat} size={13} />
                      {cat}
                    </span>
                    <span>{montant.toFixed(2)} €</span>
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
