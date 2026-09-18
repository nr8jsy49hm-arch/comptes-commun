import { useEffect, useState } from "react";
import { Download, Printer } from "lucide-react";
import {
  getDepenses,
  getCategories,
  getMembresFoyer,
  getEtiquettes,
  supprimerDepense,
  exporterDepensesCsv,
} from "../api";
import TableauDepenses from "./TableauDepenses";

export default function ListeDepenses() {
  const [depenses, setDepenses] = useState([]);
  const [categoriesParId, setCategoriesParId] = useState({});
  const [payeursParId, setPayeursParId] = useState({});
  const [etiquettes, setEtiquettes] = useState([]);
  const [filtreEtiquette, setFiltreEtiquette] = useState("");

  const charger = async (etiquetteId) => {
    const [depensesRes, categoriesRes, membresRes, etiquettesRes] = await Promise.all([
      getDepenses(etiquetteId || undefined),
      getCategories(),
      getMembresFoyer(),
      getEtiquettes(),
    ]);
    setDepenses(depensesRes.data.filter((d) => d.partagee));
    setCategoriesParId(Object.fromEntries(categoriesRes.data.map((c) => [c.id, c.nom])));
    setPayeursParId(Object.fromEntries(membresRes.data.map((m) => [m.id, m.nom])));
    setEtiquettes(etiquettesRes.data);
  };

  useEffect(() => {
    charger(filtreEtiquette);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtreEtiquette]);

  const handleSupprimer = async (id) => {
    await supprimerDepense(id);
    await charger(filtreEtiquette);
  };

  return (
    <div className="dashboard liste-depenses">
      <div className="liste-depenses-entete">
        <h3>Toutes les dépenses communes</h3>
        <div className="liste-depenses-export">
          <button type="button" className="lien" onClick={exporterDepensesCsv}>
            <Download size={14} strokeWidth={2} style={{ verticalAlign: -2, marginRight: 4 }} />
            CSV
          </button>
          <button type="button" className="lien" onClick={() => window.print()}>
            <Printer size={14} strokeWidth={2} style={{ verticalAlign: -2, marginRight: 4 }} />
            Imprimer / PDF
          </button>
        </div>
      </div>

      {etiquettes.length > 0 && (
        <div className="liste-depenses-filtre">
          <label>
            Filtrer par étiquette
            <select value={filtreEtiquette} onChange={(e) => setFiltreEtiquette(e.target.value)}>
              <option value="">Toutes</option>
              {etiquettes.map((et) => (
                <option key={et.id} value={et.id}>
                  {et.nom}
                </option>
              ))}
            </select>
          </label>
        </div>
      )}

      <TableauDepenses
        depenses={depenses}
        categoriesParId={categoriesParId}
        payeursParId={payeursParId}
        onSupprimer={handleSupprimer}
      />
    </div>
  );
}
