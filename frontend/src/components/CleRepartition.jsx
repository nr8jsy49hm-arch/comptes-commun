import { useEffect, useState } from "react";
import { getMembresFoyer, getCleRepartition, definirCleRepartition, reinitialiserCleRepartition } from "../api";

export default function CleRepartition() {
  const [membres, setMembres] = useState([]);
  const [type, setType] = useState("50_50");
  const [partU1, setPartU1] = useState(50);
  const [enregistre, setEnregistre] = useState(false);

  const charger = async () => {
    const [membresRes, cleRes] = await Promise.all([getMembresFoyer(), getCleRepartition()]);
    setMembres(membresRes.data);
    setType(cleRes.data.type);
    if (membresRes.data.length === 2) {
      setPartU1(cleRes.data.parts[membresRes.data[0].id] ?? 50);
    }
  };

  useEffect(() => {
    charger();
  }, []);

  if (membres.length !== 2) return null;

  const [u1, u2] = membres;
  const partU2 = 100 - partU1;

  const handleEnregistrer = async () => {
    await definirCleRepartition({ [u1.id]: partU1, [u2.id]: partU2 });
    setType("personnalisee");
    setEnregistre(true);
    setTimeout(() => setEnregistre(false), 2000);
  };

  const handleReinitialiser = async () => {
    await reinitialiserCleRepartition();
    setPartU1(50);
    setType("50_50");
  };

  return (
    <div className="dashboard cle-repartition">
      <h3>Clé de répartition</h3>
      <p className="cle-repartition-intro">
        Par défaut, les dépenses communes sont partagées 50/50. Tu peux ajuster la proportion
        de chacun ci-dessous.
      </p>

      <div className="cle-repartition-labels">
        <span>{u1.nom} — {partU1.toFixed(0)}%</span>
        <span>{u2.nom} — {partU2.toFixed(0)}%</span>
      </div>

      <input
        type="range"
        min="0"
        max="100"
        step="1"
        value={partU1}
        onChange={(e) => setPartU1(Number(e.target.value))}
        className="cle-repartition-curseur"
        style={{ "--valeur": `${partU1}%` }}
      />

      <div className="cle-repartition-actions">
        <button type="button" onClick={handleEnregistrer}>
          {enregistre ? "Enregistré ✓" : "Enregistrer cette répartition"}
        </button>
        {type === "personnalisee" && (
          <button type="button" className="lien" onClick={handleReinitialiser}>
            Revenir au 50/50
          </button>
        )}
      </div>
    </div>
  );
}
