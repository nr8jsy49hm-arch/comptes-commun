import { useEffect, useState } from "react";
import { User, Home, Wallet, Target, History, LogOut, Sun, Moon, Settings, Calculator } from "lucide-react";
import Dashboard from "./components/Dashboard";
import Graphiques from "./components/Graphiques";
import ComparaisonPeriodes from "./components/ComparaisonPeriodes";
import SimulateurAchat from "./components/SimulateurAchat";
import Calculette from "./components/Calculette";
import DepenseForm from "./components/DepenseForm";
import Reglement from "./components/Reglement";
import ListeDepenses from "./components/ListeDepenses";
import GestionCategories from "./components/GestionCategories";
import GestionEtiquettes from "./components/GestionEtiquettes";
import GestionRecurrentes from "./components/GestionRecurrentes";
import CleRepartition from "./components/CleRepartition";
import Historique from "./components/Historique";
import Objectifs from "./components/Objectifs";
import SoloDepenses from "./components/SoloDepenses";
import Compte from "./components/Compte";
import Login from "./components/Login";
import Register from "./components/Register";
import MotDePasseOublie from "./components/MotDePasseOublie";
import NotificationsBanner from "./components/NotificationsBanner";
import EmailVerificationBanner from "./components/EmailVerificationBanner";
import { verifierEmailToken, getMe } from "./api";

function getUtilisateurStocke() {
  const raw = localStorage.getItem("utilisateur");
  return raw ? JSON.parse(raw) : null;
}

// Ordre voulu : Solo → Commun (tableau de bord + dépenses) → Objectifs → Historique
const ONGLETS = [
  { id: "solo", label: "Compte Perso", Icon: User },
  { id: "tableau", label: "Tableau de bord", Icon: Home },
  { id: "depenses", label: "Nos Dépenses", Icon: Wallet },
  { id: "objectifs", label: "Objectifs", Icon: Target },
  { id: "historique", label: "Historique", Icon: History },
];

function getThemeInitial() {
  const stocke = localStorage.getItem("theme");
  if (stocke) return stocke;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function getInvitationDepuisUrl() {
  return new URLSearchParams(window.location.search).get("invite");
}

function getVerificationDepuisUrl() {
  return new URLSearchParams(window.location.search).get("verify");
}

export default function App() {
  const [utilisateur, setUtilisateur] = useState(getUtilisateurStocke());
  const [invitationToken] = useState(getInvitationDepuisUrl);
  const [ecranAuth, setEcranAuth] = useState(getInvitationDepuisUrl() ? "register" : "login");
  const [refreshKey, setRefreshKey] = useState(0);
  const [ongletActif, setOngletActif] = useState("solo");
  const [theme, setTheme] = useState(getThemeInitial);
  const [messageVerification, setMessageVerification] = useState(null);
  const [bandeauEmailIgnore, setBandeauEmailIgnore] = useState(false);
  const [afficherCalculette, setAfficherCalculette] = useState(false);

  useEffect(() => {
    const token = getVerificationDepuisUrl();
    if (!token) return;
    verifierEmailToken(token).then((res) => {
      setMessageVerification(res.data);
      // Nettoie l'URL pour ne pas re-déclencher la vérification à chaque rechargement
      window.history.replaceState({}, "", window.location.pathname);
      // Si on est déjà connecté (même personne), rafraîchit son statut affiché
      if (localStorage.getItem("token")) {
        getMe().then((meRes) => {
          const maj = { ...getUtilisateurStocke(), email_verifie: meRes.data.email_verifie };
          localStorage.setItem("utilisateur", JSON.stringify(maj));
          setUtilisateur(maj);
        });
      }
    });
  }, []);

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
        {messageVerification && (
          <p className={messageVerification.reussi ? "compte-message-ok" : "auth-erreur"}>
            {messageVerification.message}
          </p>
        )}
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
            invitationToken={invitationToken}
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
          <button type="button" className="nav-item" onClick={() => setAfficherCalculette(true)}>
            <Calculator size={17} strokeWidth={1.75} />
            <span>Calculette</span>
          </button>
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

        <NotificationsBanner />
        {!bandeauEmailIgnore && (
          <EmailVerificationBanner
            utilisateur={utilisateur}
            onIgnorer={() => setBandeauEmailIgnore(true)}
          />
        )}

        <div className="contenu-page" key={ongletActif}>
          {ongletActif === "solo" && <SoloDepenses />}

          {ongletActif === "tableau" && (
            <>
              <Dashboard key={refreshKey} />
              <ComparaisonPeriodes key={refreshKey} />
              <SimulateurAchat key={refreshKey} />
              <Graphiques key={refreshKey} />
            </>
          )}

          {ongletActif === "depenses" && (
            <>
              <DepenseForm onDepenseCreee={() => setRefreshKey((k) => k + 1)} />
              <Reglement onReglementCree={() => setRefreshKey((k) => k + 1)} />
              <CleRepartition key={refreshKey} />
              <GestionRecurrentes key={refreshKey} />
              <GestionCategories key={refreshKey} />
              <GestionEtiquettes key={refreshKey} />
              <ListeDepenses key={refreshKey} />
            </>
          )}

          {ongletActif === "objectifs" && <Objectifs />}

          {ongletActif === "historique" && <Historique key={refreshKey} />}

          {ongletActif === "compte" && <Compte onCompteSupprime={handleCompteSupprime} />}
        </div>
      </main>

      {afficherCalculette && <Calculette onFermer={() => setAfficherCalculette(false)} />}
    </div>
  );
}
