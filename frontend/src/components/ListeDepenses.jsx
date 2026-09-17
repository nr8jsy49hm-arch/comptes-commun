import { useEffect, useState } from "react";
import { Download, Printer } from "lucide-react";
import { getDepenses, getCategories, getMembresFoyer, supprimerDepense, exporterDepensesCsv } from "../api";
import TableauDepenses from "./TableauDepenses";

export default function ListeDepenses() {
  const [depenses, setDepenses] = useState([]);
  const [categoriesParId, setCategoriesParId] = useState({});
  const [payeursParId, setPayeursParId] = useState({});

  const charger = async () => {
    const [depensesRes, categoriesRes, membresRes] = await Promise.all([
      getDepenses(),
      getCategories(),
      getMembresFoyer(),
    ]);
    setDepenses(depensesRes.data.filter((d) => d.partagee));
    setCategoriesParId(Object.fromEntries(categoriesRes.data.map((c) => [c.id, c.nom])));
    setPayeursParId(Object.fromEntries(membresRes.data.map((m) => [m.id, m.nom])));
  };

  useEffect(() => {
    charger();
  }, []);

  const handleSupprimer = async (id) => {
    await supprimerDepense(id);
    await charger();
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
      <TableauDepenses
        depenses={depenses}
        categoriesParId={categoriesParId}
        payeursParId={payeursParId}
        onSupprimer={handleSupprimer}
      />
    </div>
  );
}
