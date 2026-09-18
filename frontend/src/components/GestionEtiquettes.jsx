import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import { getEtiquettes, supprimerEtiquette } from "../api";

export default function GestionEtiquettes() {
  const [etiquettes, setEtiquettes] = useState([]);

  const charger = () => getEtiquettes().then((res) => setEtiquettes(res.data));

  useEffect(() => {
    charger();
  }, []);

  const handleSupprimer = async (id) => {
    await supprimerEtiquette(id);
    await charger();
  };

  if (etiquettes.length === 0) return null;

  return (
    <div className="dashboard gestion-etiquettes">
      <h3>Étiquettes</h3>
      <div className="etiquettes-choix">
        {etiquettes.map((et) => (
          <span key={et.id} className="etiquette-pastille etiquette-pastille-gestion">
            {et.nom}
            <button
              type="button"
              onClick={() => handleSupprimer(et.id)}
              aria-label={`Supprimer l'étiquette ${et.nom}`}
            >
              <Trash2 size={12} strokeWidth={2} />
            </button>
          </span>
        ))}
      </div>
    </div>
  );
}
