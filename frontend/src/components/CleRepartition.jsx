import { useEffect, useState } from "react";
import { getMembresFoyer, getCleRepartition, definirCleRepartition, reinitialiserCleRepartition } from "../api";

export default function CleRepartition() {
  const [membres, setMembres] = useState([]);
  const [type, setType] = useState("equirepartition");
  const [parts, setParts] = useState({}); // { utilisateur_id: pourcentage }
  const [enregistre, setEnregistre] = useState(false);
  const [erreur, setErreur] = useState("");

  const charger = async () => {
    const [membresRes, cleRes] = await Promise.all([getMembresFoyer(), getCleRepartition()]);
    setMembres(membresRes.data);
    setType(cleRes.data.type);
    setParts(cleRes.data.parts);
  };

  useEffect(() => {
    charger();
  }, []);

  if (membres.length < 2) return null;

  const total = Object.values(parts).reduce((acc, v) => acc + Number(v || 0), 0);

  const handleChangerPart = (id, valeur) => {
    setParts((p) => ({ ...p, [id]: valeur === "" ? "" : Number(valeur) }));
  };

  const handleEnregistrer = async () => {
    setErreur("");
    if (Math.abs(total - 100) > 0.5) {
      setErreur(`Les parts doivent totaliser 100% (actuellement ${total.toFixed(0)}%).`);
      return;
    }
    await definirCleRepartition(parts);
    setType("personnalisee");
    setEnregistre(true);
    setTimeout(() => setEnregistre(false), 2000);
  };

  const handleReinitialiser = async () => {
    await reinitialiserCleRepartition();
    await charger();
  };

  return (
    <div className="dashboard cle-repartition">
      <h3>Clé de répartition</h3>
      <p className="cle-repartition-intro">
        Par défaut, les dépenses communes sont partagées à parts égales entre les{" "}
        {membres.length} membres du foyer ({(100 / membres.length).toFixed(0)}% chacun). Tu peux
        ajuster la proportion de chacun ci-dessous.
      </p>

      {erreur && <p className="auth-erreur">{erreur}</p>}

      <div className="cle-repartition-liste">
        {membres.map((m) => (
          <label key={m.id} className="cle-repartition-ligne">
            <span>{m.nom}</span>
            <span className="cle-repartition-input-pct">
              <input
                type="number"
                min="0"
                max="100"
                step="1"
                value={parts[m.id] ?? ""}
                onChange={(e) => handleChangerPart(m.id, e.target.value)}
              />
              %
            </span>
          </label>
        ))}
      </div>

      <p className={`cle-repartition-total${Math.abs(total - 100) > 0.5 ? " cle-repartition-total-erreur" : ""}`}>
        Total : {total.toFixed(0)}%
      </p>

      <div className="cle-repartition-actions">
        <button type="button" onClick={handleEnregistrer}>
          {enregistre ? "Enregistré ✓" : "Enregistrer cette répartition"}
        </button>
        {type === "personnalisee" && (
          <button type="button" className="lien" onClick={handleReinitialiser}>
            Revenir à parts égales
          </button>
        )}
      </div>
    </div>
  );
}
