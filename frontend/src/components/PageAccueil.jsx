import { PiggyBank, Wallet, Target, Users } from "lucide-react";

const FONCTIONNALITES = [
  {
    Icon: Wallet,
    titre: "Dépenses partagées",
    texte: "Enregistrez vos dépenses communes, la répartition se calcule toute seule.",
  },
  {
    Icon: Target,
    titre: "Objectifs d'épargne",
    texte: "Vacances, apport pour un achat... suivez votre progression ensemble.",
  },
  {
    Icon: PiggyBank,
    titre: "Cagnottes de groupe",
    texte: "Un lien à partager pour que vos proches participent à un projet commun.",
  },
  {
    Icon: Users,
    titre: "Commun et solo",
    texte: "Un espace partagé pour le foyer, un espace perso pour chacun.",
  },
];

export default function PageAccueil({ onSeConnecter, onCreerCompte }) {
  return (
    <div className="page-accueil">
      <div className="page-accueil-hero">
        <span className="page-accueil-marque">
          <PiggyBank size={26} strokeWidth={1.5} />
          Comptes Communs
        </span>
        <h1>Vos finances partagées, sans prise de tête.</h1>
        <p>
          Dépenses, budgets, objectifs d'épargne et projets de groupe — tout au même endroit,
          pour vous et les gens avec qui vous partagez vos comptes.
        </p>
        <div className="page-accueil-actions">
          <button type="button" onClick={onCreerCompte}>
            Créer un compte
          </button>
          <button type="button" className="lien" onClick={onSeConnecter}>
            J'ai déjà un compte
          </button>
        </div>
      </div>

      <div className="page-accueil-fonctionnalites">
        {FONCTIONNALITES.map((f) => (
          <div key={f.titre} className="page-accueil-carte">
            <f.Icon size={22} strokeWidth={1.5} />
            <h3>{f.titre}</h3>
            <p>{f.texte}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
