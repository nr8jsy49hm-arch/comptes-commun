import { useEffect, useState } from "react";
import { PiggyBank } from "lucide-react";
import { getCagnottePublique, contribuerCagnottePublique, extraireErreur } from "../api";

export default function CagnottePublique({ token }) {
  const [cagnotte, setCagnotte] = useState(null);
  const [erreurChargement, setErreurChargement] = useState(false);
  const [nom, setNom] = useState("");
  const [montant, setMontant] = useState("");
  const [message, setMessage] = useState("");
  const [erreur, setErreur] = useState("");
  const [envoi, setEnvoi] = useState(false);
  const [merci, setMerci] = useState(false);

  const charger = () =>
    getCagnottePublique(token)
      .then((res) => setCagnotte(res.data))
      .catch(() => setErreurChargement(true));

  useEffect(() => {
    charger();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErreur("");
    setEnvoi(true);
    try {
      const res = await contribuerCagnottePublique(token, {
        nom_contributeur: nom,
        montant: parseFloat(montant),
        message: message || undefined,
      });
      setCagnotte(res.data);
      setMontant("");
      setMessage("");
      setMerci(true);
      setTimeout(() => setMerci(false), 3000);
    } catch (err) {
      setErreur(extraireErreur(err, "Erreur, réessaie."));
    } finally {
      setEnvoi(false);
    }
  };

  if (erreurChargement) {
    return (
      <div className="app app-auth">
        <h1>Comptes Communs</h1>
        <p className="auth-erreur">Cette cagnotte n'existe pas ou plus.</p>
      </div>
    );
  }

  if (!cagnotte) return null;

  const progression = cagnotte.montant_cible
    ? Math.min(100, (cagnotte.montant_total / cagnotte.montant_cible) * 100)
    : null;

  return (
    <div className="app app-auth cagnotte-publique">
      <div className="cagnotte-publique-entete">
        <PiggyBank size={28} strokeWidth={1.5} />
        <h1>{cagnotte.nom}</h1>
      </div>
      {cagnotte.description && <p className="cagnotte-publique-description">{cagnotte.description}</p>}

      <div className="auth-form">
        <span className="dashboard-total">
          <strong>Cagnotte collectée</strong>
          {cagnotte.montant_total.toFixed(2)} €
        </span>
        {cagnotte.montant_cible && (
          <p className="compte-question-actuelle">sur {cagnotte.montant_cible.toFixed(2)} € visés</p>
        )}

        {progression !== null && (
          <div className="objectif-barre" style={{ marginBottom: 16 }}>
            <div className="objectif-barre-remplie" style={{ width: `${progression}%` }} />
          </div>
        )}

        {cagnotte.date_limite && (
          <p className="compte-question-actuelle">
            Échéance : {new Date(cagnotte.date_limite).toLocaleDateString("fr-FR")}
          </p>
        )}

        {cagnotte.cloturee ? (
          <p className="auth-erreur">Cette cagnotte est clôturée, elle n'accepte plus de contributions.</p>
        ) : (
          <form onSubmit={handleSubmit}>
            <h3>Participer</h3>
            {erreur && <p className="auth-erreur">{erreur}</p>}
            {merci && <p className="compte-message-ok">Merci pour ta participation !</p>}
            <input
              type="text"
              placeholder="Ton nom"
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
            <input
              type="text"
              placeholder="Un petit mot (optionnel)"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
            <button type="submit" disabled={envoi}>
              {envoi ? "Envoi..." : "Participer"}
            </button>
          </form>
        )}

        {cagnotte.contributions.length > 0 && (
          <>
            <h3 style={{ marginTop: 24 }}>Participants</h3>
            <ul className="cagnotte-participants">
              {cagnotte.contributions.map((c) => (
                <li key={c.id}>
                  <div className="cagnotte-participant-ligne">
                    <strong>{c.nom_contributeur}</strong>
                    <span>{c.montant.toFixed(2)} €</span>
                  </div>
                  {c.message && <p className="cagnotte-participant-message">{c.message}</p>}
                </li>
              ))}
            </ul>
          </>
        )}
      </div>

      <p className="cagnotte-publique-footer">
        Propulsé par <strong>Comptes Communs</strong>
      </p>
    </div>
  );
}
