import { useState } from "react";
import { X } from "lucide-react";

export default function LegalDocs({ onFermer }) {
  const [onglet, setOnglet] = useState("confidentialite");

  return (
    <div className="legal-overlay" onClick={onFermer}>
      <div className="legal-modal" onClick={(e) => e.stopPropagation()}>
        <div className="legal-header">
          <div className="onglets" style={{ marginBottom: 0, border: "none" }}>
            <button
              type="button"
              className={`onglet${onglet === "confidentialite" ? " onglet-actif" : ""}`}
              onClick={() => setOnglet("confidentialite")}
            >
              Confidentialité
            </button>
            <button
              type="button"
              className={`onglet${onglet === "cgu" ? " onglet-actif" : ""}`}
              onClick={() => setOnglet("cgu")}
            >
              CGU
            </button>
          </div>
          <button type="button" className="alerte-fermer" onClick={onFermer} aria-label="Fermer">
            <X size={18} strokeWidth={2} />
          </button>
        </div>

        <div className="legal-avertissement">
          ⚠️ Document provisoire, rédigé à titre indicatif — à faire relire par un professionnel
          du droit avant tout usage commercial réel.
        </div>

        <div className="legal-contenu">
          {onglet === "confidentialite" ? <PolitiqueConfidentialite /> : <CGU />}
        </div>
      </div>
    </div>
  );
}

function PolitiqueConfidentialite() {
  return (
    <>
      <h3>Politique de confidentialité</h3>
      <p><em>Dernière mise à jour : [à compléter]</em></p>

      <h4>1. Responsable du traitement</h4>
      <p>
        [Nom / raison sociale à compléter], contact : [email de contact à compléter].
      </p>

      <h4>2. Données collectées</h4>
      <ul>
        <li>Identité : prénom, adresse email</li>
        <li>Authentification : mot de passe (stocké sous forme hachée, jamais en clair), réponse à une question secrète (également hachée)</li>
        <li>Données financières que tu saisis toi-même : dépenses, catégories, budgets, objectifs d'épargne, règlements entre membres du foyer</li>
        <li>Données techniques : horodatages de création, adresse IP (utilisée uniquement pour la limitation anti-abus, non stockée durablement)</li>
      </ul>

      <h4>3. Finalités</h4>
      <p>
        Ces données sont utilisées exclusivement pour faire fonctionner le service : gestion de
        ton compte, calcul des dépenses et répartitions, notifications liées à ton budget.
        Aucune donnée n'est vendue ni utilisée à des fins publicitaires.
      </p>

      <h4>4. Base légale</h4>
      <p>Exécution du contrat (fourniture du service que tu as demandé en créant un compte).</p>

      <h4>5. Durée de conservation</h4>
      <p>
        Tes données sont conservées tant que ton compte existe. Tu peux le supprimer à tout
        moment depuis "Mon compte" ; certaines données peuvent être conservées temporairement si
        elles sont encore référencées par des dépenses ou règlements communs avec un autre membre
        du foyer.
      </p>

      <h4>6. Destinataires et sous-traitants</h4>
      <p>Tes données transitent par les prestataires techniques suivants :</p>
      <ul>
        <li><strong>Railway</strong> — hébergement du serveur et de la base de données</li>
        <li><strong>Vercel</strong> — hébergement de l'interface web</li>
        <li><strong>Resend</strong> — envoi des emails de confirmation</li>
      </ul>
      <p>Aucune donnée n'est transmise à d'autres tiers.</p>

      <h4>7. Tes droits</h4>
      <p>Conformément au RGPD, tu disposes des droits suivants :</p>
      <ul>
        <li><strong>Accès et portabilité</strong> : télécharge une copie de tes données depuis "Mon compte" → "Exporter mes données"</li>
        <li><strong>Rectification</strong> : modifiable directement dans l'appli pour la plupart des champs</li>
        <li><strong>Effacement</strong> : suppression de compte disponible dans "Mon compte"</li>
        <li><strong>Opposition</strong> : contacte [email de contact] pour toute demande</li>
      </ul>

      <h4>8. Sécurité</h4>
      <p>
        Mots de passe hachés (bcrypt), connexions chiffrées (HTTPS), limitation des tentatives de
        connexion, jetons d'invitation non-devinables.
      </p>

      <h4>9. Cookies et stockage local</h4>
      <p>
        L'appli utilise uniquement le stockage local de ton navigateur pour garder ta session
        connectée et tes préférences d'affichage (thème). Aucun cookie de suivi publicitaire ou
        analytique tiers n'est utilisé.
      </p>
    </>
  );
}

function CGU() {
  return (
    <>
      <h3>Conditions Générales d'Utilisation</h3>
      <p><em>Dernière mise à jour : [à compléter]</em></p>

      <h4>1. Objet</h4>
      <p>
        Les présentes CGU encadrent l'utilisation de l'application Comptes Communs, un outil de
        gestion de finances partagées entre membres d'un même foyer.
      </p>

      <h4>2. Acceptation</h4>
      <p>
        La création d'un compte implique l'acceptation pleine et entière des présentes CGU et de
        la politique de confidentialité.
      </p>

      <h4>3. Description du service</h4>
      <p>
        Le service permet d'enregistrer des dépenses, de définir des budgets, de suivre des
        objectifs d'épargne et de répartir des charges entre les membres d'un foyer. Le service
        est fourni "en l'état", sans garantie de disponibilité continue.
      </p>

      <h4>4. Compte utilisateur</h4>
      <p>
        Tu es responsable de la confidentialité de ton mot de passe et de toute activité effectuée
        depuis ton compte. Chaque compte est personnel et ne doit pas être partagé.
      </p>

      <h4>5. Contenu et responsabilité</h4>
      <p>
        Les données financières saisies relèvent de ta seule responsabilité. Le service ne
        constitue ni un conseil financier, ni un outil de comptabilité officielle.
      </p>

      <h4>6. Propriété intellectuelle</h4>
      <p>
        L'application, son code et son design restent la propriété de [nom de l'éditeur à
        compléter]. Tes données t'appartiennent et te sont restituables à tout moment.
      </p>

      <h4>7. Résiliation</h4>
      <p>
        Tu peux supprimer ton compte à tout moment depuis "Mon compte". L'éditeur se réserve le
        droit de suspendre un compte en cas d'usage abusif.
      </p>

      <h4>8. Modification des CGU</h4>
      <p>
        Ces CGU peuvent évoluer ; toute modification substantielle sera communiquée aux
        utilisateurs.
      </p>

      <h4>9. Droit applicable</h4>
      <p>Droit français.</p>
    </>
  );
}
