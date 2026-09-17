import { useEffect, useState } from "react";
import {
  changerMotDePasse,
  definirQuestionSecrete,
  getMaQuestionSecrete,
  supprimerCompte,
  extraireErreur,
} from "../api";

export default function Compte({ onCompteSupprime }) {
  // Notifications navigateur
  const [notifsActivees, setNotifsActivees] = useState(
    localStorage.getItem("notifications_navigateur") === "true"
  );
  const [messageNotifs, setMessageNotifs] = useState("");

  const handleToggleNotifs = async () => {
    if (!notifsActivees) {
      if (typeof Notification === "undefined") {
        setMessageNotifs("Ton navigateur ne supporte pas les notifications.");
        return;
      }
      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        setMessageNotifs("Autorisation refusée — active les notifications dans les réglages du navigateur.");
        return;
      }
      localStorage.setItem("notifications_navigateur", "true");
      setNotifsActivees(true);
      setMessageNotifs("Notifications activées.");
    } else {
      localStorage.setItem("notifications_navigateur", "false");
      setNotifsActivees(false);
      setMessageNotifs("Notifications désactivées.");
    }
  };

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
      setErreurMotDePasse(extraireErreur(err, "Erreur, réessaie."));
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
        <h3>Notifications</h3>
        <p className="compte-question-actuelle">
          Reçois une vraie notification du navigateur (même si l'onglet n'est pas au premier
          plan) en cas de budget dépassé ou si personne n'a enregistré de dépense commune
          depuis plusieurs jours.
        </p>
        {messageNotifs && <p className="compte-message-ok">{messageNotifs}</p>}
        <label className="compte-notif-toggle">
          <input type="checkbox" checked={notifsActivees} onChange={handleToggleNotifs} />
          Activer les notifications du navigateur
        </label>
      </div>

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
            placeholder="Nouveau mot de passe (8 caractères minimum)"
            value={nouveauMotDePasse}
            onChange={(e) => setNouveauMotDePasse(e.target.value)}
            minLength={8}
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
