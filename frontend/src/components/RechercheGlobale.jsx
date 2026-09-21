import { useEffect, useMemo, useState } from "react";
import { X, Search } from "lucide-react";
import { getDepenses, getCategories, getMembresFoyer } from "../api";
import { IconeCategorie } from "../iconesCategories";

function normaliser(texte) {
  return (texte || "")
    .toString()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

export default function RechercheGlobale({ onFermer }) {
  const [requete, setRequete] = useState("");
  const [depenses, setDepenses] = useState([]);
  const [categoriesParId, setCategoriesParId] = useState({});
  const [payeursParId, setPayeursParId] = useState({});
  const [charge, setCharge] = useState(false);

  useEffect(() => {
    Promise.all([getDepenses(), getCategories(), getMembresFoyer()]).then(
      ([depensesRes, categoriesRes, membresRes]) => {
        setDepenses(depensesRes.data);
        setCategoriesParId(Object.fromEntries(categoriesRes.data.map((c) => [c.id, c.nom])));
        setPayeursParId(Object.fromEntries(membresRes.data.map((m) => [m.id, m.nom])));
        setCharge(true);
      }
    );
  }, []);

  const resultats = useMemo(() => {
    const q = normaliser(requete);
    if (!q) return [];
    return depenses
      .filter((d) => {
        const categorie = categoriesParId[d.categorie_id] || "";
        const payeur = payeursParId[d.payeur_id] || "";
        const etiquettes = (d.etiquettes || []).map((e) => e.nom).join(" ");
        const hayotte = normaliser(
          `${d.note || ""} ${categorie} ${payeur} ${etiquettes} ${d.montant} ${d.date}`
        );
        return hayotte.includes(q);
      })
      .sort((a, b) => (a.date < b.date ? 1 : -1))
      .slice(0, 50);
  }, [requete, depenses, categoriesParId, payeursParId]);

  return (
    <div className="legal-overlay" onClick={onFermer}>
      <div className="recherche-modal" onClick={(e) => e.stopPropagation()}>
        <div className="legal-header">
          <h3>Rechercher une dépense</h3>
          <button type="button" className="alerte-fermer" onClick={onFermer} aria-label="Fermer">
            <X size={18} strokeWidth={2} />
          </button>
        </div>

        <div className="recherche-champ">
          <Search size={16} strokeWidth={1.75} />
          <input
            type="text"
            placeholder="Note, catégorie, étiquette, montant, payeur..."
            value={requete}
            onChange={(e) => setRequete(e.target.value)}
            autoFocus
          />
        </div>

        {!charge && <p className="tableau-vide">Chargement...</p>}

        {charge && requete && (
          <p className="recherche-compteur">
            {resultats.length} résultat{resultats.length !== 1 ? "s" : ""}
            {resultats.length === 50 ? " (affichage limité aux 50 plus récents)" : ""}
          </p>
        )}

        {resultats.length > 0 && (
          <ul className="recherche-resultats">
            {resultats.map((d) => (
              <li key={d.id}>
                <span className="ligne-categorie">
                  <IconeCategorie nom={categoriesParId[d.categorie_id] || "Autre"} size={14} />
                  {categoriesParId[d.categorie_id] || "Autre"}
                  {d.note && ` — ${d.note}`}
                </span>
                <span className="recherche-resultat-details">
                  <span>{d.date}</span>
                  <span>{payeursParId[d.payeur_id]}</span>
                  <span className="tableau-montant">{d.montant.toFixed(2)} €</span>
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
