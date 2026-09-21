import { useEffect, useState } from "react";
import { Camera } from "lucide-react";
import { creerDepense, getCategories, creerCategorie, getMembresFoyer, getEtiquettes, creerEtiquette } from "../api";
import { redimensionnerImage } from "../image";

function getUtilisateurStocke() {
  const raw = localStorage.getItem("utilisateur");
  return raw ? JSON.parse(raw) : null;
}

export default function DepenseForm({ onDepenseCreee }) {
  const utilisateur = getUtilisateurStocke();

  const [montant, setMontant] = useState("");
  const [note, setNote] = useState("");
  const [categories, setCategories] = useState([]);
  const [membres, setMembres] = useState([]);
  const [categorieId, setCategorieId] = useState("");
  const [payeurId, setPayeurId] = useState(utilisateur?.id || "");
  const [nouvelleCategorie, setNouvelleCategorie] = useState("");
  const [etiquettes, setEtiquettes] = useState([]);
  const [etiquettesChoisies, setEtiquettesChoisies] = useState([]);
  const [nouvelleEtiquette, setNouvelleEtiquette] = useState("");
  const [photo, setPhoto] = useState(null);
  const [chargementPhoto, setChargementPhoto] = useState(false);

  const chargerCategories = async () => {
    const res = await getCategories();
    setCategories(res.data);
    // Sélectionne la première catégorie par défaut si aucune n'est choisie
    if (res.data.length > 0 && !categorieId) {
      setCategorieId(res.data[0].id);
    }
  };

  const chargerEtiquettes = async () => {
    const res = await getEtiquettes();
    setEtiquettes(res.data);
  };

  useEffect(() => {
    chargerCategories();
    chargerEtiquettes();
    getMembresFoyer().then((res) => setMembres(res.data));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleAjouterCategorie = async () => {
    if (!nouvelleCategorie.trim()) return;
    const res = await creerCategorie({ nom: nouvelleCategorie.trim() });
    setNouvelleCategorie("");
    await chargerCategories();
    setCategorieId(res.data.id);
  };

  const handleToggleEtiquette = (id) => {
    setEtiquettesChoisies((prev) =>
      prev.includes(id) ? prev.filter((e) => e !== id) : [...prev, id]
    );
  };

  const handleAjouterEtiquette = async () => {
    if (!nouvelleEtiquette.trim()) return;
    const res = await creerEtiquette(nouvelleEtiquette.trim());
    setNouvelleEtiquette("");
    await chargerEtiquettes();
    setEtiquettesChoisies((prev) => [...prev, res.data.id]);
  };

  const handleChoisirPhoto = async (e) => {
    const fichier = e.target.files?.[0];
    if (!fichier) return;
    setChargementPhoto(true);
    try {
      const dataUrl = await redimensionnerImage(fichier);
      setPhoto(dataUrl);
    } finally {
      setChargementPhoto(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!categorieId || !payeurId) return;
    await creerDepense({
      montant: parseFloat(montant),
      date: new Date().toISOString().slice(0, 10),
      note,
      categorie_id: categorieId,
      payeur_id: payeurId,
      etiquette_ids: etiquettesChoisies,
      photo,
    });
    setMontant("");
    setNote("");
    setEtiquettesChoisies([]);
    setPhoto(null);
    onDepenseCreee?.();
  };

  return (
    <form onSubmit={handleSubmit} className="depense-form">
      <h3>Ajouter une dépense</h3>

      <input
        type="number"
        step="0.01"
        placeholder="Montant (€)"
        value={montant}
        onChange={(e) => setMontant(e.target.value)}
        required
      />

      <input
        type="text"
        placeholder="Note (optionnel)"
        value={note}
        onChange={(e) => setNote(e.target.value)}
      />

      <label>
        Catégorie
        <select value={categorieId} onChange={(e) => setCategorieId(Number(e.target.value))}>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.nom}
            </option>
          ))}
        </select>
      </label>

      {/* Ajout rapide d'une nouvelle catégorie sans quitter le formulaire */}
      <div className="ajout-categorie">
        <input
          type="text"
          placeholder="Nouvelle catégorie..."
          value={nouvelleCategorie}
          onChange={(e) => setNouvelleCategorie(e.target.value)}
        />
        <button type="button" className="lien" onClick={handleAjouterCategorie}>
          + Ajouter catégorie
        </button>
      </div>

      <label>
        Payé par
        <select value={payeurId} onChange={(e) => setPayeurId(Number(e.target.value))}>
          {membres.map((m) => (
            <option key={m.id} value={m.id}>
              {m.nom}
            </option>
          ))}
        </select>
      </label>

      <div className="etiquettes-champ">
        <span className="etiquettes-champ-titre">Étiquettes (optionnel)</span>
        <div className="etiquettes-choix">
          {etiquettes.map((et) => (
            <button
              type="button"
              key={et.id}
              className={`etiquette-pastille${etiquettesChoisies.includes(et.id) ? " etiquette-pastille-active" : ""}`}
              onClick={() => handleToggleEtiquette(et.id)}
            >
              {et.nom}
            </button>
          ))}
        </div>
        <div className="ajout-categorie">
          <input
            type="text"
            placeholder="Nouvelle étiquette..."
            value={nouvelleEtiquette}
            onChange={(e) => setNouvelleEtiquette(e.target.value)}
          />
          <button type="button" className="lien" onClick={handleAjouterEtiquette}>
            + Ajouter étiquette
          </button>
        </div>
      </div>

      <div className="etiquettes-champ">
        <span className="etiquettes-champ-titre">Justificatif (optionnel)</span>
        {photo ? (
          <div className="photo-apercu">
            <img src={photo} alt="Aperçu du justificatif" />
            <button type="button" className="lien" onClick={() => setPhoto(null)}>
              Retirer
            </button>
          </div>
        ) : (
          <label className="photo-input-label">
            <Camera size={16} strokeWidth={1.75} />
            {chargementPhoto ? "Traitement..." : "Ajouter une photo"}
            <input type="file" accept="image/*" onChange={handleChoisirPhoto} hidden />
          </label>
        )}
      </div>

      <button type="submit">Ajouter</button>
    </form>
  );
}
