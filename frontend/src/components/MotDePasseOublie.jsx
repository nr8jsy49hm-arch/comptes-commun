import { useState } from "react";
import { demanderQuestionSecrete, reinitialiserMotDePasse } from "../api";

export default function MotDePasseOublie({ onRetourConnexion }) {
  const [etape, setEtape] = useState("email"); // "email" | "reponse" | "fait"
  const [email, setEmail] = useState("");
  const [question, setQuestion] = useState(null);
  const [reponse, setReponse] = useState("");
  const [nouveauMotDePasse, setNouveauMotDePasse] = useState("");
  const [erreur, setErreur] = useState("");

  const handleDemander = async (e) => {
    e.preventDefault();
    setErreur("");
    const res = await demanderQuestionSecrete(email);
    if (!res.data.question) {
      setErreur(
        "Aucune question secrète n'est définie pour cet email. Demande à ton/ta partenaire de t'aider à changer le mot de passe directement, ou contacte-nous."
      );
      return;
    }
    setQuestion(res.data.question);
    setEtape("reponse");
  };

  const handleReinitialiser = async (e) => {
    e.preventDefault();
    setErreur("");
    try {
      await reinitialiserMotDePasse(email, reponse, nouveauMotDePasse);
      setEtape("fait");
    } catch (err) {
      setErreur(err.response?.data?.detail || "Réponse incorrecte, réessaie.");
    }
  };

  if (etape === "fait") {
    return (
      <div className="auth-form">
        <h2>Mot de passe changé</h2>
        <p>Tu peux maintenant te connecter avec ton nouveau mot de passe.</p>
        <button type="button" onClick={onRetourConnexion}>
          Retour à la connexion
        </button>
      </div>
    );
  }

  if (etape === "reponse") {
    return (
      <form onSubmit={handleReinitialiser} className="auth-form">
        <h2>Question secrète</h2>
        {erreur && <p className="auth-erreur">{erreur}</p>}
        <p>{question}</p>
        <input
          type="text"
          placeholder="Ta réponse"
          value={reponse}
          onChange={(e) => setReponse(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Nouveau mot de passe"
          value={nouveauMotDePasse}
          onChange={(e) => setNouveauMotDePasse(e.target.value)}
          required
        />
        <button type="submit">Réinitialiser le mot de passe</button>
        <p>
          <button type="button" className="lien" onClick={onRetourConnexion}>
            Retour à la connexion
          </button>
        </p>
      </form>
    );
  }

  return (
    <form onSubmit={handleDemander} className="auth-form">
      <h2>Mot de passe oublié</h2>
      {erreur && <p className="auth-erreur">{erreur}</p>}
      <input
        type="email"
        placeholder="Ton email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <button type="submit">Continuer</button>
      <p>
        <button type="button" className="lien" onClick={onRetourConnexion}>
          Retour à la connexion
        </button>
      </p>
    </form>
  );
}
