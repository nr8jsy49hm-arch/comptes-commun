import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { getHistoriqueAnnee } from "../api";

function calculerDelta(actuel, reference) {
  if (reference === 0) return actuel === 0 ? 0 : null; // pas de base de comparaison valable
  return ((actuel - reference) / reference) * 100;
}

function CarteComparaison({ titre, montantActuel, montantReference, libelleReference }) {
  const delta = calculerDelta(montantActuel, montantReference);

  return (
    <div className="comparaison-carte">
      <span className="comparaison-titre">{titre}</span>
      <span className="comparaison-montant">{montantActuel.toFixed(2)} €</span>
      <span className="comparaison-reference">{libelleReference} : {montantReference.toFixed(2)} €</span>
      {delta !== null && (
        <span className={`comparaison-delta ${delta > 0 ? "delta-hausse" : delta < 0 ? "delta-baisse" : ""}`}>
          {delta > 0 ? <TrendingUp size={14} strokeWidth={2} /> : delta < 0 ? <TrendingDown size={14} strokeWidth={2} /> : <Minus size={14} strokeWidth={2} />}
          {delta === 0 ? "Stable" : `${delta > 0 ? "+" : ""}${delta.toFixed(0)}%`}
        </span>
      )}
    </div>
  );
}

export default function ComparaisonPeriodes() {
  const [donnees, setDonnees] = useState(null);

  useEffect(() => {
    const aujourdhui = new Date();
    const anneeActuelle = aujourdhui.getFullYear();
    const moisActuel = aujourdhui.getMonth() + 1; // 1-12
    const moisPrecedentNum = moisActuel === 1 ? 12 : moisActuel - 1;
    const anneePourMoisPrecedent = moisActuel === 1 ? anneeActuelle - 1 : anneeActuelle;

    Promise.all([getHistoriqueAnnee(anneeActuelle), getHistoriqueAnnee(anneeActuelle - 1)]).then(
      ([resActuelle, resPrecedente]) => {
        const dataActuelle = resActuelle.data;
        const dataPrecedente = resPrecedente.data;

        const totalActuel = dataActuelle[moisActuel - 1]?.total_depense ?? 0;
        const totalMoisPrecedent =
          (anneePourMoisPrecedent === anneeActuelle ? dataActuelle : dataPrecedente)[moisPrecedentNum - 1]
            ?.total_depense ?? 0;
        const totalMemeMoisAnDernier = dataPrecedente[moisActuel - 1]?.total_depense ?? 0;
        const nomMoisPrecedent = dataActuelle[moisPrecedentNum - 1]?.nom_mois || "";
        const nomMoisActuel = dataActuelle[moisActuel - 1]?.nom_mois || "";

        setDonnees({
          totalActuel,
          totalMoisPrecedent,
          totalMemeMoisAnDernier,
          nomMoisPrecedent,
          nomMoisActuel,
          anneePrecedente: anneeActuelle - 1,
        });
      }
    );
  }, []);

  if (!donnees) return null;

  return (
    <div className="dashboard comparaison-periodes">
      <h3>Comparaison</h3>
      <div className="comparaison-grille">
        <CarteComparaison
          titre="Vs mois dernier"
          montantActuel={donnees.totalActuel}
          montantReference={donnees.totalMoisPrecedent}
          libelleReference={donnees.nomMoisPrecedent}
        />
        <CarteComparaison
          titre={`Vs ${donnees.nomMoisActuel} ${donnees.anneePrecedente}`}
          montantActuel={donnees.totalActuel}
          montantReference={donnees.totalMemeMoisAnDernier}
          libelleReference="l'an dernier"
        />
      </div>
    </div>
  );
}
