import { useEffect, useState } from "react";
import { User, Home, Wallet, Target, History, LogOut, Sun, Moon, Settings } from "lucide-react";
import Dashboard from "./components/Dashboard";
import DepenseForm from "./components/DepenseForm";
import Reglement from "./components/Reglement";
import ListeDepenses from "./components/ListeDepenses";
import Historique from "./components/Historique";
import Objectifs from "./components/Objectifs";
import SoloDepenses from "./components/SoloDepenses";
import Compte from "./components/Compte";
import Login from "./components/Login";
import Register from "./components/Register";
import MotDePasseOublie from "./components/MotDePasseOublie";

function getUtilisateurStocke() {
  const raw = localStorage.getItem("utilisateur");
  return raw ? JSON.parse(raw) : null;
}

// Ordre voulu : Solo → Commun (tableau de bord + dépenses) → Objectifs → Historique
const ONGLETS = [
  { id: "solo", label: "Solo", Icon: User },
  { id: "tableau", label: "Tableau de bord", Icon: Home },
  { id: "depenses", label: "Dépenses", Icon: Wallet },
  { id: "objectifs", label: "Objectifs", Icon: Target },
  { id: "historique", label: "Historique", Icon: History },
];

function getThemeInitial() {
  const stocke = localStorage.getItem("theme");
  if (stocke) return stocke;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export default function App() {
  const [utilisateur, setUtilisateur] = useState(getUtilisateurStocke());
  const [ecranAuth, setEcranAuth] = useState("login"); // "login" ou "register"
  const [refreshKey, setRefreshKey] = useState(0);
  const [ongletActif, setOngletActif] = useState("solo");
  const [theme, setTheme] = useState(getThemeInitial);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);

  const basculerTheme = () => setTheme((t) => (t === "dark" ? "light" : "dark"));

  const handleDeconnexion = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("utilisateur");
    setUtilisateur(null);
  };

  const handleCompteSupprime = () => {
    handleDeconnexion();
  };

  if (!utilisateur) {
    return (
      <div className="app app-auth">
        <h1>Comptes Communs</h1>
        {ecranAuth === "login" && (
          <Login
            onConnecte={setUtilisateur}
            onAllerInscription={() => setEcranAuth("register")}
            onMotDePasseOublie={() => setEcranAuth("oublie")}
          />
        )}
        {ecranAuth === "register" && (
          <Register
            onInscrit={setUtilisateur}
            onAllerConnexion={() => setEcranAuth("login")}
          />
        )}
        {ecranAuth === "oublie" && (
          <MotDePasseOublie onRetourConnexion={() => setEcranAuth("login")} />
        )}
      </div>
    );
  }

  const ongletCourant = ONGLETS.find((o) => o.id === ongletActif);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="sidebar-brand-mark">CC</span>
          <span className="sidebar-brand-nom">Comptes Communs</span>
        </div>

        <nav className="nav-vertical">
          {ONGLETS.map((o) => (
            <button
              key={o.id}
              type="button"
              className={`nav-item${ongletActif === o.id ? " nav-item-actif" : ""}`}
              onClick={() => setOngletActif(o.id)}
            >
              <o.Icon size={18} strokeWidth={1.75} />
              <span>{o.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-utilisateur">
            <span className="sidebar-utilisateur-nom">{utilisateur.nom}</span>
            <span className="sidebar-utilisateur-foyer">Foyer n°{utilisateur.foyer_id}</span>
          </div>
          <button
            type="button"
            className={`nav-item${ongletActif === "compte" ? " nav-item-actif" : ""}`}
            onClick={() => setOngletActif("compte")}
          >
            <Settings size={17} strokeWidth={1.75} />
            <span>Mon compte</span>
          </button>
          <button type="button" className="nav-item nav-item-deconnexion" onClick={handleDeconnexion}>
            <LogOut size={17} strokeWidth={1.75} />
            <span>Déconnexion</span>
          </button>
          <button type="button" className="nav-item" onClick={basculerTheme}>
            {theme === "dark" ? <Sun size={17} strokeWidth={1.75} /> : <Moon size={17} strokeWidth={1.75} />}
            <span>{theme === "dark" ? "Mode clair" : "Mode sombre"}</span>
          </button>
        </div>
      </aside>

      <main className="contenu">
        <header className="contenu-header">
          <h1>{ongletActif === "compte" ? "Mon compte" : ongletCourant?.label}</h1>
        </header>

        <div className="contenu-page" key={ongletActif}>
          {ongletActif === "solo" && <SoloDepenses />}

          {ongletActif === "tableau" && <Dashboard key={refreshKey} />}

          {ongletActif === "depenses" && (
            <>
              <DepenseForm onDepenseCreee={() => setRefreshKey((k) => k + 1)} />
              <Reglement onReglementCree={() => setRefreshKey((k) => k + 1)} />
              <ListeDepenses key={refreshKey} />
            </>
          )}

          {ongletActif === "objectifs" && <Objectifs />}

          {ongletActif === "historique" && <Historique key={refreshKey} />}

          {ongletActif === "compte" && <Compte onCompteSupprime={handleCompteSupprime} />}
        </div>
      </main>
    </div>
  );
}
