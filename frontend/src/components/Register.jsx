import { useEffect, useState } from "react";
import { register, verifierInvitation, extraireErreur } from "../api";

export default function Register({ onInscrit, onAllerConnexion, invitationToken }) {
  const [nom, setNom] = useState("");
  const [email, setEmail] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [mode, setMode] = useState(invitationToken ? "rejoindre" : "creer");
  const [nomFoyer, setNomFoyer] = useState("");
  const [tokenSaisi, setTokenSaisi] = useState(invitationToken || "");
  const [infoInvitation, setInfoInvitation] = useState(null); // { valide, nom_foyer }
  const [questionSecrete, setQuestionSecrete] = useState("");
  const [reponseSecrete, setReponseSecrete] = useState("");
  const [erreur, setErreur] = useState("");

  useEffect(() => {
    if (mode !== "rejoindre" || !tokenSaisi) {
      setInfoInvitation(null);
      return;
    }
    verifierInvitation(tokenSaisi)
      .then((res) => setInfoInvitation(res.data))
      .catch(() => setInfoInvitation({ valide: false }));
  }, [mode, tokenSaisi]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErreur("");
    try {
      const payload = {
        nom,
        email,
        mot_de_passe: motDePasse,
        ...(mode === "creer"
          ? { nom_foyer: nomFoyer || undefined }
          : { invitation_token: tokenSaisi.trim() }),
        ...(questionSecrete && reponseSecrete
          ? { question_secrete: questionSecrete, reponse_secrete: reponseSecrete }
          : {}),
      };
      const res = await register(payload);
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("utilisateur", JSON.stringify(res.data.utilisateur));
      onInscrit(res.data.utilisateur);
    } catch (err) {
      setErreur(extraireErreur(err, "Erreur lors de l'inscription, réessaie."));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      <h2>Inscription</h2>
      {erreur && <p className="auth-erreur">{erreur}</p>}

      <input
        type="text"
        placeholder="Ton prénom"
        value={nom}
        onChange={(e) => setNom(e.target.value)}
        required
      />
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Mot de passe (8 caractères minimum)"
        value={motDePasse}
        onChange={(e) => setMotDePasse(e.target.value)}
        minLength={8}
        required
      />

      {!invitationToken && (
        <div className="auth-mode-choix">
          <label>
            <input
              type="radio"
              checked={mode === "creer"}
              onChange={() => setMode("creer")}
            />
            Créer un nouveau foyer (premier inscrit)
          </label>
          <label>
            <input
              type="radio"
              checked={mode === "rejoindre"}
              onChange={() => setMode("rejoindre")}
            />
            J'ai un lien d'invitation
          </label>
        </div>
      )}

      {mode === "creer" ? (
        <input
          type="text"
          placeholder="Nom du foyer (optionnel)"
          value={nomFoyer}
          onChange={(e) => setNomFoyer(e.target.value)}
        />
      ) : (
        <>
          {!invitationToken && (
            <input
              type="text"
              placeholder="Colle ton lien ou code d'invitation"
              value={tokenSaisi}
              onChange={(e) => {
                const v = e.target.value;
                // Accepte qu'on colle le lien complet ou juste le jeton
                const match = v.match(/invite=([^&\s]+)/);
                setTokenSaisi(match ? match[1] : v.trim());
              }}
              required
            />
          )}
          {infoInvitation && (
            <p className={infoInvitation.valide ? "compte-message-ok" : "auth-erreur"}>
              {infoInvitation.valide
                ? `Tu vas rejoindre : ${infoInvitation.nom_foyer}`
                : "Ce lien d'invitation est invalide, expiré ou déjà utilisé."}
            </p>
          )}
        </>
      )}

      <label>
        Question secrète (recommandé, pour récupérer ton compte)
        <input
          type="text"
          placeholder="Ex : nom de ton premier animal ?"
          value={questionSecrete}
          onChange={(e) => setQuestionSecrete(e.target.value)}
        />
      </label>
      {questionSecrete && (
        <input
          type="text"
          placeholder="Ta réponse"
          value={reponseSecrete}
          onChange={(e) => setReponseSecrete(e.target.value)}
        />
      )}

      <button type="submit" disabled={mode === "rejoindre" && infoInvitation && !infoInvitation.valide}>
        S'inscrire
      </button>
      <p>
        Déjà un compte ?{" "}
        <button type="button" className="lien" onClick={onAllerConnexion}>
          Se connecter
        </button>
      </p>
    </form>
  );
}
