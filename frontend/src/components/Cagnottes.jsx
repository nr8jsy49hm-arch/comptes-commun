import { useEffect, useState } from "react";
import { PiggyBank, Copy, Plus, Trash2, RefreshCw } from "lucide-react";
import {
  listerCagnottes,
  creerCagnotte,
  modifierCagnotte,
  supprimerCagnotte,
  regenererLienCagnotte,
  contribuerCagnotte,
} from "../api";

function CarteCagnotte({ cagnotte, onMaj, onSupprimer }) {
  const [ouverte, setOuverte] = useState(false);
  const [montantVersement, setMontantVersement] = useState("");
  const [lienCopie, setLienCopie] = useState(false);

  const lien = `${window.location.origin}/?cagnotte=${cagnotte.token_public}`;
  const progression = cagnotte.montant_cible
    ? Math.min(100, (cagnotte.montant_total / cagnotte.montant_cible) * 100)
    : null;

  const handleCopier = () => {
    navigator.clipboard.writeText(lien);
    setLienCopie(true);
    setTimeout(() => setLienCopie(false), 2000);
  };

  const handleVerser = async (e) => {
    e.preventDefault();
    if (!montantVersement) return;
    await contribuerCagnotte(cagnotte.id, { montant: parseFloat(montantVersement) });
    setMontantVersement("");
    onMaj();
  };

  const handleToggleCloture = async () => {
    await modifierCagnotte(cagnotte.id, { cloturee: !cagnotte.cloturee });
    onMaj();
  };

  const handleRegenererLien = async () => {
    await regenererLienCagnotte(cagnotte.id);
    onMaj();
  };

  return (
    <li className="objectif">
      <div className="objectif-entete">
        <span className="objectif-nom">
          <PiggyBank size={16} strokeWidth={1.75} style={{ verticalAlign: -3, marginRight: 6 }} />
          {cagnotte.nom}
          {cagnotte.cloturee && <span className="cagnotte-badge-cloturee">Clôturée</span>}
        </span>
        <button type="button" className="lien" onClick={() => onSupprimer(cagnotte.id)}>
          supprimer
        </button>
      </div>

      {progression !== null && (
        <div className="objectif-barre">
          <div className="objectif-barre-remplie" style={{ width: `${progression}%` }} />
        </div>
      )}

      <div className="objectif-details">
        <span>
          {cagnotte.montant_total.toFixed(2)} €
          {cagnotte.montant_cible ? ` / ${cagnotte.montant_cible.toFixed(2)} €` : ""} —{" "}
          {cagnotte.nb_contributions} participation{cagnotte.nb_contributions > 1 ? "s" : ""}
        </span>
      </div>

      <button type="button" className="lien" onClick={() => setOuverte((o) => !o)}>
        {ouverte ? "Réduire" : "Gérer / partager"}
      </button>

      {ouverte && (
        <div className="cagnotte-gestion">
          <div className="cagnotte-lien-partage">
            <input type="text" readOnly value={lien} />
            <button type="button" onClick={handleCopier}>
              <Copy size={14} strokeWidth={2} style={{ verticalAlign: -2, marginRight: 4 }} />
              {lienCopie ? "Copié !" : "Copier"}
            </button>
          </div>

          <form onSubmit={handleVerser} className="cagnotte-verser-form">
            <input
              type="number"
              step="0.01"
              placeholder="Ajouter un versement (€)"
              value={montantVersement}
              onChange={(e) => setMontantVersement(e.target.value)}
            />
            <button type="submit">Verser</button>
          </form>

          <div className="categorie-actions" style={{ marginTop: 12 }}>
            <button type="button" className="lien" onClick={handleRegenererLien}>
              <RefreshCw size={13} strokeWidth={2} style={{ verticalAlign: -2, marginRight: 4 }} />
              Régénérer le lien
            </button>
            <button type="button" className="lien" onClick={handleToggleCloture}>
              {cagnotte.cloturee ? "Réouvrir" : "Clôturer"}
            </button>
          </div>
        </div>
      )}
    </li>
  );
}

export default function Cagnottes() {
  const [cagnottes, setCagnottes] = useState([]);
  const [formOuvert, setFormOuvert] = useState(false);
  const [nom, setNom] = useState("");
  const [description, setDescription] = useState("");
  const [montantCible, setMontantCible] = useState("");
  const [dateLimite, setDateLimite] = useState("");

  const charger = () => listerCagnottes().then((res) => setCagnottes(res.data));

  useEffect(() => {
    charger();
  }, []);

  const handleCreer = async (e) => {
    e.preventDefault();
    if (!nom) return;
    await creerCagnotte({
      nom,
      description: description || undefined,
      montant_cible: montantCible ? parseFloat(montantCible) : undefined,
      date_limite: dateLimite || undefined,
    });
    setNom("");
    setDescription("");
    setMontantCible("");
    setDateLimite("");
    setFormOuvert(false);
    await charger();
  };

  const handleSupprimer = async (id) => {
    await supprimerCagnotte(id);
    await charger();
  };

  return (
    <div className="dashboard cagnottes">
      <h3>Cagnottes pour vos projets</h3>
      <p className="cle-repartition-intro">
        Voyage groupé, cadeau d'anniversaire, projet commun... partage un lien pour que tes
        proches participent (ils créent un compte en une minute s'ils n'en ont pas déjà un,
        histoire que chaque participation vienne d'une vraie personne). Purement déclaratif —
        aucun paiement réel n'est encaissé, chacun indique juste ce qu'il a mis.
      </p>

      {cagnottes.length === 0 && !formOuvert && (
        <p className="objectifs-vide">Aucune cagnotte pour l'instant.</p>
      )}

      {cagnottes.length > 0 && (
        <ul className="objectifs-liste">
          {cagnottes.map((c) => (
            <CarteCagnotte key={c.id} cagnotte={c} onMaj={charger} onSupprimer={handleSupprimer} />
          ))}
        </ul>
      )}

      {formOuvert ? (
        <form onSubmit={handleCreer} className="objectif-form">
          <input
            type="text"
            placeholder="Nom (ex : Voyage au Portugal)"
            value={nom}
            onChange={(e) => setNom(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Description (optionnel)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <input
            type="number"
            step="0.01"
            placeholder="Montant visé (optionnel)"
            value={montantCible}
            onChange={(e) => setMontantCible(e.target.value)}
          />
          <label>
            Échéance (optionnel)
            <input type="date" value={dateLimite} onChange={(e) => setDateLimite(e.target.value)} />
          </label>
          <button type="submit">Créer la cagnotte</button>
        </form>
      ) : (
        <button type="button" className="lien" onClick={() => setFormOuvert(true)}>
          <Plus size={14} strokeWidth={2} style={{ verticalAlign: -2, marginRight: 4 }} />
          Nouvelle cagnotte
        </button>
      )}
    </div>
  );
}
