import os
import logging
import requests

logger = logging.getLogger("uvicorn.error")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://comptes-commun.vercel.app")


def envoyer_email(destinataire: str, sujet: str, html: str) -> bool:
    """Envoie un email via l'API Resend. Ne lève jamais d'exception : si l'envoi échoue
    (pas de clé configurée, service indisponible...), on logue et on continue — un email
    qui ne part pas ne doit jamais faire planter une inscription."""
    if not RESEND_API_KEY:
        logger.warning(
            "⚠️  RESEND_API_KEY n'est pas configurée — email non envoyé (à : %s, sujet : %s). "
            "Définis RESEND_API_KEY sur Railway pour activer l'envoi réel.",
            destinataire,
            sujet,
        )
        return False

    try:
        res = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json={
                "from": RESEND_FROM_EMAIL,
                "to": [destinataire],
                "subject": sujet,
                "html": html,
            },
            timeout=10,
        )
        if res.status_code >= 400:
            logger.error("Échec envoi email à %s : %s %s", destinataire, res.status_code, res.text)
            return False
        return True
    except requests.RequestException as e:
        logger.error("Erreur réseau lors de l'envoi d'email à %s : %s", destinataire, e)
        return False


def envoyer_email_verification(destinataire: str, nom: str, token: str) -> bool:
    lien = f"{FRONTEND_URL}/?verify={token}"
    html = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
        <h2>Confirme ton email</h2>
        <p>Bonjour {nom},</p>
        <p>Clique sur le lien ci-dessous pour confirmer ton adresse email sur Comptes Communs :</p>
        <p><a href="{lien}" style="background:#b08549;color:#fff;padding:10px 18px;
            border-radius:6px;text-decoration:none;">Confirmer mon email</a></p>
        <p style="color:#888;font-size:0.85em;">Ce lien expire dans 24 heures. Si tu n'es pas à
        l'origine de cette inscription, ignore cet email.</p>
    </div>
    """
    return envoyer_email(destinataire, "Confirme ton email — Comptes Communs", html)
