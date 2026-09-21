import { useEffect, useState } from "react";
import { AlertTriangle, X } from "lucide-react";
import { getAlertes } from "../api";

const SEUIL_RAPPEL_JOURS = 5;

function cleAujourdhui() {
  return new Date().toISOString().slice(0, 10);
}

function chargerIgnorees() {
  try {
    const brut = localStorage.getItem("alertes_ignorees");
    const data = brut ? JSON.parse(brut) : {};
    // On ne garde que les ignorances du jour — une alerte réapparaît le lendemain si toujours vraie
    return data.date === cleAujourdhui() ? data.cles : [];
  } catch {
    return [];
  }
}

function sauvegarderIgnorees(cles) {
  localStorage.setItem("alertes_ignorees", JSON.stringify({ date: cleAujourdhui(), cles }));
}

function notifierNavigateur(titre, corps) {
  if (localStorage.getItem("notifications_navigateur") !== "true") return;
  if (typeof Notification === "undefined" || Notification.permission !== "granted") return;

  const derniere = JSON.parse(localStorage.getItem("derniere_notif_navigateur") || "{}");
  if (derniere[titre] === cleAujourdhui()) return; // déjà notifié aujourd'hui pour ce titre

  new Notification(titre, { body: corps, icon: undefined });
  derniere[titre] = cleAujourdhui();
  localStorage.setItem("derniere_notif_navigateur", JSON.stringify(derniere));
}

export default function NotificationsBanner() {
  const [alertes, setAlertes] = useState([]);
  const [ignorees, setIgnorees] = useState(chargerIgnorees);

  useEffect(() => {
    getAlertes().then((res) => {
      const data = res.data;
      const liste = [];

      if (data.depassement_budget_commun) {
        const cle = `budget-commun-${data.depassement_budget_commun}`;
        const texte = `Budget commun dépassé de ${data.depassement_budget_commun.toFixed(2)} € ce mois-ci.`;
        liste.push({ cle, texte });
        notifierNavigateur("Budget commun dépassé", texte);
      }

      if (data.depassement_budget_solo) {
        const cle = `budget-solo-${data.depassement_budget_solo}`;
        const texte = `Ton budget perso est dépassé de ${data.depassement_budget_solo.toFixed(2)} € ce mois-ci.`;
        liste.push({ cle, texte });
        notifierNavigateur("Budget perso dépassé", texte);
      }

      if (data.jours_sans_depense_commune != null && data.jours_sans_depense_commune >= SEUIL_RAPPEL_JOURS) {
        const cle = `rappel-saisie-${data.jours_sans_depense_commune}`;
        const texte = `Aucune dépense commune enregistrée depuis ${data.jours_sans_depense_commune} jours — pensez à mettre à jour vos comptes.`;
        liste.push({ cle, texte });
        notifierNavigateur("Rappel de saisie", texte);
      }

      (data.changements_recurrentes || []).forEach((texte, i) => {
        const cle = `recurrente-${i}-${texte}`;
        liste.push({ cle, texte });
        notifierNavigateur("Montant récurrent changé", texte);
      });

      (data.enveloppes_depassees || []).forEach((texte, i) => {
        const cle = `enveloppe-${i}-${texte}`;
        liste.push({ cle, texte });
        notifierNavigateur("Enveloppe dépassée", texte);
      });

      setAlertes(liste);
    });
  }, []);

  const ignorer = (cle) => {
    const nouvelles = [...ignorees, cle];
    setIgnorees(nouvelles);
    sauvegarderIgnorees(nouvelles);
  };

  const visibles = alertes.filter((a) => !ignorees.includes(a.cle));

  if (visibles.length === 0) return null;

  return (
    <div className="alertes-bandeau">
      {visibles.map((a) => (
        <div key={a.cle} className="alerte-item">
          <AlertTriangle size={16} strokeWidth={1.75} />
          <span>{a.texte}</span>
          <button
            type="button"
            className="alerte-fermer"
            onClick={() => ignorer(a.cle)}
            aria-label="Ignorer cette alerte pour aujourd'hui"
          >
            <X size={15} strokeWidth={2} />
          </button>
        </div>
      ))}
    </div>
  );
}
