import { useState } from "react";
import { register } from "../api";

export default function Register({ onInscrit, onAllerConnexion }) {
  const [nom, setNom] = useState("");
  const [email, setEmail] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [mode, setMode] = useState("creer"); // "creer" ou "rejoindre"
  const [nomFoyer, setNomFoyer] = useState("");
  const [codeFoyer, setCodeFoyer] = useState("");
  const [erreur, setErreur] = useState("");

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
          : { code_foyer: parseInt(codeFoyer, 10) }),
      };
      const res = await register(payload);
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("utilisateur", JSON.stringify(res.data.utilisateur));
      onInscrit(res.data.utilisateur);
    } catch (err) {
      setErreur(
        err.response?.data?.detail || "Erreur lors de l'inscription, réessaie."
      );
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
        placeholder="Mot de passe"
        value={motDePasse}
        onChange={(e) => setMotDePasse(e.target.value)}
        required
      />

      <div className="auth-mode-choix">
        <label>
          <input
            type="radio"
            checked={mode === "creer"}
            onChange={() => setMode("creer")}
          />
          Créer un nouveau foyer (premier inscrit du couple)
        </label>
        <label>
          <input
            type="radio"
            checked={mode === "rejoindre"}
            onChange={() => setMode("rejoindre")}
          />
          Rejoindre un foyer existant
        </label>
      </div>

      {mode === "creer" ? (
        <input
          type="text"
          placeholder="Nom du foyer (optionnel)"
          value={nomFoyer}
          onChange={(e) => setNomFoyer(e.target.value)}
        />
      ) : (
        <input
          type="number"
          placeholder="Numéro du foyer (donné par ton/ta partenaire)"
          value={codeFoyer}
          onChange={(e) => setCodeFoyer(e.target.value)}
          required
        />
      )}

      <button type="submit">S'inscrire</button>
      <p>
        Déjà un compte ?{" "}
        <button type="button" className="lien" onClick={onAllerConnexion}>
          Se connecter
        </button>
      </p>
    </form>
  );
}
