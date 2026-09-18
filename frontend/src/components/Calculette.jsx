import { useState } from "react";
import { X, Copy, Delete } from "lucide-react";

function calculer(a, b, operateur) {
  switch (operateur) {
    case "+":
      return a + b;
    case "-":
      return a - b;
    case "×":
      return a * b;
    case "÷":
      return b === 0 ? NaN : a / b;
    default:
      return b;
  }
}

export default function Calculette({ onFermer }) {
  const [affichage, setAffichage] = useState("0");
  const [valeurEnMemoire, setValeurEnMemoire] = useState(null);
  const [operateur, setOperateur] = useState(null);
  const [recommencer, setRecommencer] = useState(false);
  const [copie, setCopie] = useState(false);

  const saisirChiffre = (chiffre) => {
    if (recommencer || affichage === "0") {
      setAffichage(chiffre);
      setRecommencer(false);
    } else {
      setAffichage(affichage + chiffre);
    }
  };

  const saisirVirgule = () => {
    if (recommencer) {
      setAffichage("0,");
      setRecommencer(false);
      return;
    }
    if (!affichage.includes(",")) setAffichage(affichage + ",");
  };

  const choisirOperateur = (op) => {
    const valeurActuelle = parseFloat(affichage.replace(",", "."));
    if (valeurEnMemoire !== null && operateur && !recommencer) {
      const resultat = calculer(valeurEnMemoire, valeurActuelle, operateur);
      setAffichage(String(resultat).replace(".", ","));
      setValeurEnMemoire(resultat);
    } else {
      setValeurEnMemoire(valeurActuelle);
    }
    setOperateur(op);
    setRecommencer(true);
  };

  const egale = () => {
    if (valeurEnMemoire === null || !operateur) return;
    const valeurActuelle = parseFloat(affichage.replace(",", "."));
    const resultat = calculer(valeurEnMemoire, valeurActuelle, operateur);
    setAffichage(String(Math.round(resultat * 100) / 100).replace(".", ","));
    setValeurEnMemoire(null);
    setOperateur(null);
    setRecommencer(true);
  };

  const effacer = () => {
    setAffichage("0");
    setValeurEnMemoire(null);
    setOperateur(null);
    setRecommencer(false);
  };

  const effacerDernier = () => {
    if (affichage.length <= 1 || recommencer) {
      setAffichage("0");
    } else {
      setAffichage(affichage.slice(0, -1));
    }
  };

  const copier = () => {
    navigator.clipboard.writeText(affichage.replace(",", "."));
    setCopie(true);
    setTimeout(() => setCopie(false), 1500);
  };

  return (
    <div className="legal-overlay" onClick={onFermer}>
      <div className="calculette" onClick={(e) => e.stopPropagation()}>
        <div className="calculette-header">
          <h3>Calculette</h3>
          <button type="button" className="alerte-fermer" onClick={onFermer} aria-label="Fermer">
            <X size={18} strokeWidth={2} />
          </button>
        </div>

        <div className="calculette-affichage">
          {copie && <span className="calculette-copie">Copié !</span>}
          {affichage} €
        </div>

        <div className="calculette-grille">
          <button type="button" className="calculette-touche calculette-fonction" onClick={effacer}>
            AC
          </button>
          <button type="button" className="calculette-touche calculette-fonction" onClick={effacerDernier}>
            <Delete size={16} strokeWidth={1.75} />
          </button>
          <button type="button" className="calculette-touche calculette-fonction" onClick={copier}>
            <Copy size={16} strokeWidth={1.75} />
          </button>
          <button type="button" className="calculette-touche calculette-operateur" onClick={() => choisirOperateur("÷")}>
            ÷
          </button>

          {["7", "8", "9"].map((c) => (
            <button key={c} type="button" className="calculette-touche" onClick={() => saisirChiffre(c)}>
              {c}
            </button>
          ))}
          <button type="button" className="calculette-touche calculette-operateur" onClick={() => choisirOperateur("×")}>
            ×
          </button>

          {["4", "5", "6"].map((c) => (
            <button key={c} type="button" className="calculette-touche" onClick={() => saisirChiffre(c)}>
              {c}
            </button>
          ))}
          <button type="button" className="calculette-touche calculette-operateur" onClick={() => choisirOperateur("-")}>
            −
          </button>

          {["1", "2", "3"].map((c) => (
            <button key={c} type="button" className="calculette-touche" onClick={() => saisirChiffre(c)}>
              {c}
            </button>
          ))}
          <button type="button" className="calculette-touche calculette-operateur" onClick={() => choisirOperateur("+")}>
            +
          </button>

          <button type="button" className="calculette-touche" onClick={() => saisirChiffre("0")}>
            0
          </button>
          <button type="button" className="calculette-touche" onClick={saisirVirgule}>
            ,
          </button>
          <button
            type="button"
            className="calculette-touche calculette-egale"
            onClick={egale}
            style={{ gridColumn: "span 2" }}
          >
            =
          </button>
        </div>
      </div>
    </div>
  );
}
