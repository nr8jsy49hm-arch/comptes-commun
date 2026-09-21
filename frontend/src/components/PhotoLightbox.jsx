import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { getPhotoDepense } from "../api";

export default function PhotoLightbox({ depenseId, onFermer }) {
  const [photo, setPhoto] = useState(null);

  useEffect(() => {
    getPhotoDepense(depenseId).then((res) => setPhoto(res.data.photo));
  }, [depenseId]);

  return (
    <div className="legal-overlay" onClick={onFermer}>
      <div className="photo-lightbox" onClick={(e) => e.stopPropagation()}>
        <button type="button" className="alerte-fermer photo-lightbox-fermer" onClick={onFermer} aria-label="Fermer">
          <X size={20} strokeWidth={2} />
        </button>
        {photo ? (
          <img src={photo} alt="Justificatif" />
        ) : (
          <p className="photo-lightbox-chargement">Chargement...</p>
        )}
      </div>
    </div>
  );
}
