import { useState } from "react";
import { login } from "../api";

export default function Login({ onConnecte, onAllerInscription, onMotDePasseOublie }) {
  const [email, setEmail] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [erreur, setErreur] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErreur("");
    try {
      const res = await login(email, motDePasse);
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("utilisateur", JSON.stringify(res.data.utilisateur));
      onConnecte(res.data.utilisateur);
    } catch (err) {
      setErreur(
        err.response?.data?.detail || "Erreur de connexion, réessaie."
      );
    }
  };

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      <h2>Connexion</h2>
      {erreur && <p className="auth-erreur">{erreur}</p>}
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Mot de passe"
        value={motDePasse}
        onChange={(e) => setMotDePasse(e.target.value)}
        required
      />
      <button type="submit">Se connecter</button>
      <p>
        <button type="button" className="lien" onClick={onMotDePasseOublie}>
          Mot de passe oublié ?
        </button>
      </p>
      <p>
        Pas encore de compte ?{" "}
        <button type="button" className="lien" onClick={onAllerInscription}>
          S'inscrire
        </button>
      </p>
    </form>
  );
}
