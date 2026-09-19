import { useEffect, useMemo, useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { getDepenses, getCategories, getMembresFoyer } from "../api";
import { IconeCategorie } from "../iconesCategories";

const JOURS_SEMAINE = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];
const NOMS_MOIS = [
  "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
  "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
];

function formatCle(annee, mois, jour) {
  return `${annee}-${String(mois).padStart(2, "0")}-${String(jour).padStart(2, "0")}`;
}

export default function CalendrierDepenses() {
  const aujourdhui = new Date();
  const [annee, setAnnee] = useState(aujourdhui.getFullYear());
  const [mois, setMois] = useState(aujourdhui.getMonth() + 1); // 1-12
  const [depenses, setDepenses] = useState([]);
  const [categoriesParId, setCategoriesParId] = useState({});
  const [payeursParId, setPayeursParId] = useState({});
  const [jourSelectionne, setJourSelectionne] = useState(null);

  useEffect(() => {
    Promise.all([getDepenses(), getCategories(), getMembresFoyer()]).then(
      ([depensesRes, categoriesRes, membresRes]) => {
        setDepenses(depensesRes.data.filter((d) => d.partagee));
        setCategoriesParId(Object.fromEntries(categoriesRes.data.map((c) => [c.id, c.nom])));
        setPayeursParId(Object.fromEntries(membresRes.data.map((m) => [m.id, m.nom])));
      }
    );
  }, []);

  const parJour = useMemo(() => {
    const carte = {};
    for (const d of depenses) {
      carte[d.date] = carte[d.date] || [];
      carte[d.date].push(d);
    }
    return carte;
  }, [depenses]);

  const premierJourMois = new Date(annee, mois - 1, 1);
  const nbJoursMois = new Date(annee, mois, 0).getDate();
  // Décalage pour commencer la grille un lundi (getDay() : 0=dimanche)
  const decalage = (premierJourMois.getDay() + 6) % 7;

  const cellules = [];
  for (let i = 0; i < decalage; i++) cellules.push(null);
  for (let jour = 1; jour <= nbJoursMois; jour++) cellules.push(jour);

  const changerMois = (delta) => {
    let nouveauMois = mois + delta;
    let nouvelleAnnee = annee;
    if (nouveauMois > 12) {
      nouveauMois = 1;
      nouvelleAnnee += 1;
    } else if (nouveauMois < 1) {
      nouveauMois = 12;
      nouvelleAnnee -= 1;
    }
    setMois(nouveauMois);
    setAnnee(nouvelleAnnee);
    setJourSelectionne(null);
  };

  const depensesDuJourSelectionne = jourSelectionne
    ? parJour[formatCle(annee, mois, jourSelectionne)] || []
    : [];

  return (
    <div className="dashboard calendrier">
      <div className="calendrier-entete">
        <button type="button" className="calendrier-nav" onClick={() => changerMois(-1)} aria-label="Mois précédent">
          <ChevronLeft size={18} strokeWidth={2} />
        </button>
        <h3>
          {NOMS_MOIS[mois - 1]} {annee}
        </h3>
        <button type="button" className="calendrier-nav" onClick={() => changerMois(1)} aria-label="Mois suivant">
          <ChevronRight size={18} strokeWidth={2} />
        </button>
      </div>

      <div className="calendrier-grille calendrier-entetes-jours">
        {JOURS_SEMAINE.map((j) => (
          <span key={j}>{j}</span>
        ))}
      </div>

      <div className="calendrier-grille">
        {cellules.map((jour, i) => {
          if (jour === null) return <span key={`vide-${i}`} className="calendrier-case calendrier-case-vide" />;
          const cle = formatCle(annee, mois, jour);
          const depensesJour = parJour[cle] || [];
          const total = depensesJour.reduce((acc, d) => acc + d.montant, 0);
          const estAujourdhui =
            annee === aujourdhui.getFullYear() && mois === aujourdhui.getMonth() + 1 && jour === aujourdhui.getDate();

          return (
            <button
              type="button"
              key={cle}
              className={`calendrier-case${total > 0 ? " calendrier-case-active" : ""}${estAujourdhui ? " calendrier-case-aujourdhui" : ""}${jourSelectionne === jour ? " calendrier-case-selectionnee" : ""}`}
              onClick={() => setJourSelectionne(jourSelectionne === jour ? null : jour)}
              disabled={total === 0}
            >
              <span className="calendrier-jour-numero">{jour}</span>
              {total > 0 && <span className="calendrier-jour-montant">{total.toFixed(0)} €</span>}
            </button>
          );
        })}
      </div>

      {jourSelectionne && depensesDuJourSelectionne.length > 0 && (
        <div className="calendrier-detail">
          <h4>
            {jourSelectionne} {NOMS_MOIS[mois - 1]}
          </h4>
          <ul>
            {depensesDuJourSelectionne.map((d) => (
              <li key={d.id}>
                <span className="ligne-categorie">
                  <IconeCategorie nom={categoriesParId[d.categorie_id] || "Autre"} size={14} />
                  {categoriesParId[d.categorie_id] || "Autre"}
                  {d.note && ` — ${d.note}`}
                  <span className="calendrier-detail-payeur">({payeursParId[d.payeur_id]})</span>
                </span>
                <span>{d.montant.toFixed(2)} €</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
