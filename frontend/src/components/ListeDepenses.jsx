import { useEffect, useState } from "react";
import { getDepenses, getCategories, getMembresFoyer, supprimerDepense } from "../api";
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
      <h3>Toutes les dépenses communes</h3>
      <TableauDepenses
        depenses={depenses}
        categoriesParId={categoriesParId}
        payeursParId={payeursParId}
        onSupprimer={handleSupprimer}
      />
    </div>
  );
}
