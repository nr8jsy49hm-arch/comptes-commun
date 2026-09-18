import { useEffect, useState } from "react";
import { Calculator } from "lucide-react";
import { getDashboard, getSoloDashboard } from "../api";

export default function SimulateurAchat() {
  const [contexte, setContexte] = useState("commun");
  const [donneesCommun, setDonneesCommun] = useState(null);
  const [donneesSolo, setDonneesSolo] = useState(null);
  const [montant, setMontant] = useState("");

  useEffect(() => {
    getDashboard().then((res) => setDonneesCommun(res.data));
    getSoloDashboard().then((res) => setDonneesSolo(res.data));
  }, []);

  const donnees = contexte === "commun" ? donneesCommun : donneesSolo;
  if (!donnees) return null;

  const montantSimule = parseFloat(montant) || 0;
  const nouveauTotal = donnees.total_mois + montantSimule;
  const budgetDefini = donnees.budget_mois != null;
  const nouveauReste = budgetDefini ? donnees.budget_mois - nouveauTotal : null;
  const depasserait = budgetDefini && nouveauReste < 0;

  return (
    <div className="dashboard simulateur">
      <h3>
        <Calculator size={16} strokeWidth={1.75} style={{ verticalAlign: -2, marginRight: 6 }} />
        Simulateur d'achat
      </h3>
      <p className="cle-repartition-intro">
        Teste l'impact d'une dépense avant de la valider — rien n'est enregistré.
      </p>

      <div className="simulateur-contexte">
        <button
          type="button"
          className={`onglet${contexte === "commun" ? " onglet-actif" : ""}`}
          onClick={() => setContexte("commun")}
        >
          Commun
        </button>
        <button
          type="button"
          className={`onglet${contexte === "solo" ? " onglet-actif" : ""}`}
          onClick={() => setContexte("solo")}
        >
          Perso
        </button>
      </div>

      <input
        type="number"
        step="0.01"
        placeholder="Montant envisagé (€)"
        value={montant}
        onChange={(e) => setMontant(e.target.value)}
        className="simulateur-input"
      />

      {montantSimule > 0 && (
        <div className="simulateur-resultat">
          <div className="comparaison-carte">
            <span className="comparaison-titre">Total {contexte === "commun" ? "commun" : "perso"} après cette dépense</span>
            <span className="comparaison-montant">{nouveauTotal.toFixed(2)} €</span>
            <span className="comparaison-reference">Actuellement : {donnees.total_mois.toFixed(2)} €</span>
          </div>

          {budgetDefini ? (
            <div className={`simulateur-alerte${depasserait ? " simulateur-alerte-danger" : " simulateur-alerte-ok"}`}>
              {depasserait
                ? `⚠️ Tu dépasserais ton budget de ${Math.abs(nouveauReste).toFixed(2)} €.`
                : `✓ Il te resterait ${nouveauReste.toFixed(2)} € ce mois-ci.`}
            </div>
          ) : (
            <p className="simulateur-sans-budget">
              Aucun budget défini pour évaluer la marge restante — définis-en un pour une
              simulation complète.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
