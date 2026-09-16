import {
  ShoppingCart,
  Home,
  Zap,
  Gamepad2,
  AlertTriangle,
  Car,
  HeartPulse,
  UtensilsCrossed,
  Shirt,
  Baby,
  Gift,
  PawPrint,
  Plane,
  GraduationCap,
  Tag,
} from "lucide-react";

// Association mot-clé (dans le nom de la catégorie) → icône. La première
// règle qui matche l'emporte ; "Tag" sert de repli générique.
const REGLES = [
  [/courses|alimentation|supermarch[ée]|épicerie/i, ShoppingCart],
  [/loyer|logement|maison|immobilier/i, Home],
  [/[ée]lectric|[ée]nergie|eau|gaz|charges/i, Zap],
  [/loisir|jeu|sortie|cin[ée]ma/i, Gamepad2],
  [/impr[ée]vu|urgence/i, AlertTriangle],
  [/transport|essence|voiture|carburant|p[ée]age/i, Car],
  [/sant[ée]|pharmacie|m[ée]decin|mutuelle/i, HeartPulse],
  [/restaurant|resto|fast.?food|livraison/i, UtensilsCrossed],
  [/v[êe]tement|habill/i, Shirt],
  [/enfant|b[ée]b[ée]/i, Baby],
  [/cadeau/i, Gift],
  [/animal|chat|chien|v[ée]t[ée]rinaire/i, PawPrint],
  [/vacances|voyage|billet/i, Plane],
  [/[ée]tude|formation|scolarit[ée]/i, GraduationCap],
];

export function iconeCategorie(nom = "") {
  return REGLES.find(([regex]) => regex.test(nom))?.[1] || Tag;
}

export function IconeCategorie({ nom, size = 15, className, ...props }) {
  const Icon = iconeCategorie(nom);
  return (
    <Icon
      size={size}
      strokeWidth={1.75}
      className={`icone-categorie${className ? ` ${className}` : ""}`}
      {...props}
    />
  );
}
