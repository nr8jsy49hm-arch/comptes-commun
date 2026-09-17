import { useEffect, useState } from "react";
import {
  changerMotDePasse,
  definirQuestionSecrete,
  getMaQuestionSecrete,
  supprimerCompte,
} from "../api";

export default function Compte({ onCompteSupprime }) {
  // Changement de mot de passe
  const [motDePasseActuel, setMotDePasseActuel] = useState("");
  const [nouveauMotDePasse, setNouveauMotDePasse] = useState("");
  const [messageMotDePasse, setMessageMotDePasse] = useState("");
  const [erreurMotDePasse, setErreurMotDePasse] = useState("");

  // Question secrète
  const [questionActuelle, setQuestionActuelle] = useState(null);
  const [question, setQuestion] = useState("");
  const [reponse, setReponse] = useState("");
  const [messageQuestion, setMessageQuestion] = useState("");

  // Suppression de compte
  const [confirmationSuppression, setConfirmationSuppression] = useState(false);
  const [motDePasseSuppression, setMotDePasseSuppression] = useState("");
  const [erreurSuppression, setErreurSuppression] = useState("");

  useEffect(() => {
    getMaQuestionSecrete().then((res) => setQuestionActuelle(res.data.question));
  }, []);

  const handleChangerMotDePasse = async (e) => {
    e.preventDefault();
    setErreurMotDePasse("");
    setMessageMotDePasse("");
    try {
      await changerMotDePasse(motDePasseActuel, nouveauMotDePasse);
      setMotDePasseActuel("");
      setNouveauMotDePasse("");
      setMessageMotDePasse("Mot de passe mis à jour.");
    } catch (err) {
      setErreurMotDePasse(err.response?.data?.detail || "Erreur, réessaie.");
    }
  };

  const handleDefinirQuestion = async (e) => {
    e.preventDefault();
    setMessageQuestion("");
    await definirQuestionSecrete(question, reponse);
    setQuestionActuelle(question);
    setQuestion("");
    setReponse("");
    setMessageQuestion("Question secrète enregistrée.");
  };

  const handleSupprimer = async (e) => {
    e.preventDefault();
    setErreurSuppression("");
    try {
      await supprimerCompte(motDePasseSuppression);
      onCompteSupprime();
    } catch (err) {
      setErreurSuppression(
        err.response?.data?.detail || "Erreur lors de la suppression, réessaie."
      );
    }
  };

  return (
    <>
      <div className="dashboard compte-section">
        <h3>Changer mon mot de passe</h3>
        {messageMotDePasse && <p className="compte-message-ok">{messageMotDePasse}</p>}
        {erreurMotDePasse && <p className="auth-erreur">{erreurMotDePasse}</p>}
        <form onSubmit={handleChangerMotDePasse}>
          <input
            type="password"
            placeholder="Mot de passe actuel"
            value={motDePasseActuel}
            onChange={(e) => setMotDePasseActuel(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Nouveau mot de passe"
            value={nouveauMotDePasse}
            onChange={(e) => setNouveauMotDePasse(e.target.value)}
            required
          />
          <button type="submit">Mettre à jour</button>
        </form>
      </div>

      <div className="dashboard compte-section">
        <h3>Question secrète</h3>
        <p className="compte-question-actuelle">
          {questionActuelle
            ? `Question actuelle : ${questionActuelle}`
            : "Aucune question secrète définie pour l'instant — utile pour récupérer ton compte si tu oublies ton mot de passe."}
        </p>
        {messageQuestion && <p className="compte-message-ok">{messageQuestion}</p>}
        <form onSubmit={handleDefinirQuestion}>
          <input
            type="text"
            placeholder="Nouvelle question (ex : nom de ton premier animal ?)"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Réponse"
            value={reponse}
            onChange={(e) => setReponse(e.target.value)}
            required
          />
          <button type="submit">Enregistrer</button>
        </form>
      </div>

      <div className="dashboard compte-section compte-danger">
        <h3>Supprimer mon compte</h3>
        <p>
          Cette action est définitive. Tes dépenses personnelles et ton budget solo seront
          supprimés. Si tu as des dépenses ou règlements communs enregistrés, la suppression
          sera bloquée pour l'instant — préviens-nous si ça arrive.
        </p>
        {!confirmationSuppression ? (
          <button
            type="button"
            className="bouton-danger"
            onClick={() => setConfirmationSuppression(true)}
          >
            Supprimer mon compte
          </button>
        ) : (
          <form onSubmit={handleSupprimer}>
            {erreurSuppression && <p className="auth-erreur">{erreurSuppression}</p>}
            <input
              type="password"
              placeholder="Confirme avec ton mot de passe"
              value={motDePasseSuppression}
              onChange={(e) => setMotDePasseSuppression(e.target.value)}
              required
            />
            <button type="submit" className="bouton-danger">
              Confirmer la suppression définitive
            </button>
            <button type="button" className="lien" onClick={() => setConfirmationSuppression(false)}>
              Annuler
            </button>
          </form>
        )}
      </div>
    </>
  );
}
