import { useEffect, useState } from "react";
import { Pencil, Trash2, Check, X } from "lucide-react";
import { getCategories, renommerCategorie, supprimerCategorie } from "../api";
import { IconeCategorie } from "../iconesCategories";

export default function GestionCategories() {
  const [categories, setCategories] = useState([]);
  const [enEdition, setEnEdition] = useState(null); // id de la catégorie éditée
  const [nomEdition, setNomEdition] = useState("");
  const [erreur, setErreur] = useState("");

  const charger = () => getCategories().then((res) => setCategories(res.data));

  useEffect(() => {
    charger();
  }, []);

  const commencerEdition = (cat) => {
    setEnEdition(cat.id);
    setNomEdition(cat.nom);
    setErreur("");
  };

  const validerEdition = async (id) => {
    if (!nomEdition.trim()) return;
    await renommerCategorie(id, nomEdition.trim());
    setEnEdition(null);
    await charger();
  };

  const handleSupprimer = async (id) => {
    setErreur("");
    try {
      await supprimerCategorie(id);
      await charger();
    } catch (err) {
      setErreur(err.response?.data?.detail || "Erreur lors de la suppression.");
    }
  };

  if (categories.length === 0) return null;

  return (
    <div className="dashboard gestion-categories">
      <h3>Catégories</h3>
      {erreur && <p className="auth-erreur">{erreur}</p>}
      <ul>
        {categories.map((cat) => (
          <li key={cat.id}>
            {enEdition === cat.id ? (
              <>
                <input
                  type="text"
                  value={nomEdition}
                  onChange={(e) => setNomEdition(e.target.value)}
                  autoFocus
                  className="categorie-edition-input"
                />
                <span className="categorie-actions">
                  <button
                    type="button"
                    className="tableau-supprimer"
                    onClick={() => validerEdition(cat.id)}
                    aria-label="Valider"
                  >
                    <Check size={15} strokeWidth={2} />
                  </button>
                  <button
                    type="button"
                    className="tableau-supprimer"
                    onClick={() => setEnEdition(null)}
                    aria-label="Annuler"
                  >
                    <X size={15} strokeWidth={2} />
                  </button>
                </span>
              </>
            ) : (
              <>
                <span className="ligne-categorie">
                  <IconeCategorie nom={cat.nom} />
                  {cat.nom}
                </span>
                <span className="categorie-actions">
                  <button
                    type="button"
                    className="tableau-supprimer"
                    onClick={() => commencerEdition(cat)}
                    aria-label="Renommer"
                  >
                    <Pencil size={14} strokeWidth={1.75} />
                  </button>
                  <button
                    type="button"
                    className="tableau-supprimer"
                    onClick={() => handleSupprimer(cat.id)}
                    aria-label="Supprimer"
                  >
                    <Trash2 size={14} strokeWidth={1.75} />
                  </button>
                </span>
              </>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
