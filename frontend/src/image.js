/**
 * Redimensionne et compresse une image sélectionnée par l'utilisateur avant envoi,
 * pour éviter d'envoyer des photos de plusieurs Mo prises directement au téléphone.
 * Renvoie une data URL JPEG (base64), utilisable directement pour l'affichage ou l'envoi.
 */
export function redimensionnerImage(fichier, maxLargeur = 1000, qualite = 0.7) {
  return new Promise((resolve, reject) => {
    const lecteur = new FileReader();
    lecteur.onload = (evenement) => {
      const image = new Image();
      image.onload = () => {
        const ratio = Math.min(1, maxLargeur / image.width);
        const canvas = document.createElement("canvas");
        canvas.width = Math.round(image.width * ratio);
        canvas.height = Math.round(image.height * ratio);
        const contexte = canvas.getContext("2d");
        contexte.drawImage(image, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL("image/jpeg", qualite));
      };
      image.onerror = reject;
      image.src = evenement.target.result;
    };
    lecteur.onerror = reject;
    lecteur.readAsDataURL(fichier);
  });
}
