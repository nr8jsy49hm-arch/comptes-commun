import { IconeCategorie } from "../iconesCategories";

const MEDAILLES = ["🥇", "🥈", "🥉"];

export default function ClassementCategories({ parCategorie, tailleIcone = 15 }) {
  const entrees = Object.entries(parCategorie).sort((a, b) => b[1] - a[1]);
  const total = entrees.reduce((acc, [, montant]) => acc + montant, 0);

  if (entrees.length === 0) return null;

  return (
    <ul className="classement-categories">
      {entrees.map(([cat, montant], i) => {
        const pourcentage = total > 0 ? (montant / total) * 100 : 0;
        return (
          <li key={cat}>
            <div className="classement-ligne">
              <span className="ligne-categorie">
                <span className="classement-rang">{MEDAILLES[i] || `${i + 1}.`}</span>
                <IconeCategorie nom={cat} size={tailleIcone} />
                {cat}
              </span>
              <span className="classement-montant">
                {montant.toFixed(2)} € <span className="classement-pct">({pourcentage.toFixed(0)}%)</span>
              </span>
            </div>
            <div className="classement-barre">
              <div className="classement-barre-remplie" style={{ width: `${pourcentage}%` }} />
            </div>
          </li>
        );
      })}
    </ul>
  );
}
