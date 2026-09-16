import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { getObjectifs, creerObjectif, supprimerObjectif, verserObjectif } from "../api";

function formatDate(d) {
  if (!d) return null;
  return new Date(d).toLocaleDateString("fr-FR", { month: "long", year: "numeric" });
}

export default function Objectifs() {
  const [objectifs, setObjectifs] = useState([]);
  const [versementsEnCours, setVersementsEnCours] = useState({});
  const [formOuvert, setFormOuvert] = useState(false);
  const [nom, setNom] = useState("");
  const [montantCible, setMontantCible] = useState("");
  const [dateCible, setDateCible] = useState("");

  const charger = () => getObjectifs().then((res) => setObjectifs(res.data));

  useEffect(() => {
    charger();
  }, []);

  const handleCreer = async (e) => {
    e.preventDefault();
    if (!nom || !montantCible) return;
    await creerObjectif({
      nom,
      montant_cible: parseFloat(montantCible),
      date_cible: dateCible || null,
    });
    setNom("");
    setMontantCible("");
    setDateCible("");
    setFormOuvert(false);
    await charger();
  };

  const handleSupprimer = async (id) => {
    await supprimerObjectif(id);
    await charger();
  };

  const handleVerser = async (id) => {
    const montant = parseFloat(versementsEnCours[id]);
    if (!montant) return;
    await verserObjectif(id, montant);
    setVersementsEnCours((v) => ({ ...v, [id]: "" }));
    await charger();
  };

  return (
    <div className="dashboard objectifs">
      <h3>Objectifs d'épargne</h3>

      {objectifs.length === 0 && !formOuvert && (
        <p className="objectifs-vide">Aucun objectif pour l'instant.</p>
      )}

      <ul className="objectifs-liste">
        {objectifs.map((o) => {
          const progression = Math.min(100, (o.montant_actuel / o.montant_cible) * 100);
          const atteint = o.montant_actuel >= o.montant_cible;
          return (
            <li key={o.id} className="objectif">
              <div className="objectif-entete">
                <span className="objectif-nom">{o.nom}</span>
                <button type="button" className="lien" onClick={() => handleSupprimer(o.id)}>
                  supprimer
                </button>
              </div>

              <div className="objectif-barre">
                <div
                  className="objectif-barre-remplie"
                  style={{ width: `${progression}%` }}
                />
              </div>

              <div className="objectif-details">
                <span>
                  {o.montant_actuel.toFixed(2)} € / {o.montant_cible.toFixed(2)} €
                  {atteint && " — atteint 🎉"}
                </span>
                {o.date_cible && <span>Échéance : {formatDate(o.date_cible)}</span>}
              </div>

              <div className="objectif-versement">
                <input
                  type="number"
                  step="0.01"
                  placeholder="Verser un montant (€)"
                  value={versementsEnCours[o.id] || ""}
                  onChange={(e) =>
                    setVersementsEnCours((v) => ({ ...v, [o.id]: e.target.value }))
                  }
                />
                <button type="button" onClick={() => handleVerser(o.id)}>
                  Verser
                </button>
              </div>
            </li>
          );
        })}
      </ul>

      {formOuvert ? (
        <form onSubmit={handleCreer} className="objectif-form">
          <input
            type="text"
            placeholder="Nom de l'objectif (ex : Vacances)"
            value={nom}
            onChange={(e) => setNom(e.target.value)}
            required
          />
          <input
            type="number"
            step="0.01"
            placeholder="Montant cible (€)"
            value={montantCible}
            onChange={(e) => setMontantCible(e.target.value)}
            required
          />
          <label>
            Échéance (optionnel)
            <input
              type="month"
              value={dateCible}
              onChange={(e) => setDateCible(e.target.value ? `${e.target.value}-01` : "")}
            />
          </label>
          <button type="submit">Créer l'objectif</button>
        </form>
      ) : (
        <button type="button" className="lien" onClick={() => setFormOuvert(true)}>
          <Plus size={14} strokeWidth={2} style={{ verticalAlign: -2, marginRight: 4 }} />
          Nouvel objectif
        </button>
      )}
    </div>
  );
}
