import { useState } from "react";
import { Mail, X } from "lucide-react";
import { renvoyerVerificationEmail } from "../api";

export default function EmailVerificationBanner({ utilisateur, onIgnorer }) {
  const [envoye, setEnvoye] = useState(false);
  const [chargement, setChargement] = useState(false);

  if (!utilisateur || utilisateur.email_verifie) return null;

  const handleRenvoyer = async () => {
    setChargement(true);
    try {
      await renvoyerVerificationEmail();
      setEnvoye(true);
    } finally {
      setChargement(false);
    }
  };

  return (
    <div className="alertes-bandeau">
      <div className="alerte-item alerte-info">
        <Mail size={16} strokeWidth={1.75} />
        <span>
          {envoye
            ? "Email de confirmation renvoyé — pense à vérifier tes spams."
            : "Confirme ton adresse email pour sécuriser ton compte."}
        </span>
        {!envoye && (
          <button type="button" className="lien" onClick={handleRenvoyer} disabled={chargement}>
            Renvoyer l'email
          </button>
        )}
        <button type="button" className="alerte-fermer" onClick={onIgnorer} aria-label="Ignorer">
          <X size={15} strokeWidth={2} />
        </button>
      </div>
    </div>
  );
}
