import { useMemo, useState } from "react";
import { ChevronUp, ChevronDown, Trash2 } from "lucide-react";
import { IconeCategorie } from "../iconesCategories";

const COLONNES = [
  { id: "date", label: "Date" },
  { id: "categorie", label: "Catégorie" },
  { id: "payeur", label: "Payé par" }, // masquée si afficherPayeur=false
  { id: "note", label: "Note" },
  { id: "montant", label: "Montant" },
];

export default function TableauDepenses({
  depenses,
  categoriesParId = {},
  payeursParId = {},
  afficherPayeur = true,
  onSupprimer,
}) {
  const [tri, setTri] = useState({ colonne: "date", direction: "desc" });

  const lignes = useMemo(() => {
    return depenses.map((d) => ({
      id: d.id,
      date: d.date,
      categorie: categoriesParId[d.categorie_id] || "Autre",
      payeur: payeursParId[d.payeur_id] || "",
      note: d.note || "",
      montant: d.montant,
      etiquettes: d.etiquettes || [],
    }));
  }, [depenses, categoriesParId, payeursParId]);

  const lignesTriees = useMemo(() => {
    const copie = [...lignes];
    copie.sort((a, b) => {
      const va = a[tri.colonne];
      const vb = b[tri.colonne];
      let comparaison;
      if (typeof va === "number") {
        comparaison = va - vb;
      } else {
        comparaison = String(va).localeCompare(String(vb), "fr");
      }
      return tri.direction === "asc" ? comparaison : -comparaison;
    });
    return copie;
  }, [lignes, tri]);

  const handleTrier = (colonneId) => {
    setTri((t) =>
      t.colonne === colonneId
        ? { colonne: colonneId, direction: t.direction === "asc" ? "desc" : "asc" }
        : { colonne: colonneId, direction: "asc" }
    );
  };

  const colonnesAffichees = COLONNES.filter((c) => afficherPayeur || c.id !== "payeur");

  if (depenses.length === 0) {
    return <p className="tableau-vide">Aucune dépense pour l'instant.</p>;
  }

  return (
    <div className="tableau-depenses-wrapper">
      <table className="tableau-depenses">
        <thead>
          <tr>
            {colonnesAffichees.map((c) => (
              <th key={c.id}>
                <button type="button" className="tableau-tri" onClick={() => handleTrier(c.id)}>
                  {c.label}
                  {tri.colonne === c.id &&
                    (tri.direction === "asc" ? (
                      <ChevronUp size={13} strokeWidth={2} />
                    ) : (
                      <ChevronDown size={13} strokeWidth={2} />
                    ))}
                </button>
              </th>
            ))}
            {onSupprimer && <th aria-hidden="true"></th>}
          </tr>
        </thead>
        <tbody>
          {lignesTriees.map((l) => (
            <tr key={l.id}>
              <td>{l.date}</td>
              <td>
                <span className="ligne-categorie">
                  <IconeCategorie nom={l.categorie} size={14} />
                  {l.categorie}
                </span>
              </td>
              {afficherPayeur && <td>{l.payeur}</td>}
              <td className="tableau-note">
                {l.note}
                {l.etiquettes.length > 0 && (
                  <div className="tableau-etiquettes">
                    {l.etiquettes.map((et) => (
                      <span key={et.id} className="etiquette-pastille-mini">
                        {et.nom}
                      </span>
                    ))}
                  </div>
                )}
              </td>
              <td className="tableau-montant">{l.montant.toFixed(2)} €</td>
              {onSupprimer && (
                <td>
                  <button
                    type="button"
                    className="tableau-supprimer"
                    onClick={() => onSupprimer(l.id)}
                    aria-label="Supprimer cette dépense"
                  >
                    <Trash2 size={14} strokeWidth={1.75} />
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
