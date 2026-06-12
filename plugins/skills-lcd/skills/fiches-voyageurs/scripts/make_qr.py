#!/usr/bin/env python3
"""Génère un QR code de connexion WiFi (PNG, fond transparent en option).

Usage :
    python make_qr.py "NomDuReseau" "MotDePasse" sortie.png [WPA|WEP|nopass]

Le QR encode la chaîne standard `WIFI:T:<auth>;S:<ssid>;P:<motdepasse>;;`
reconnue par iOS et Android : scanner = connecté.

SÉCURITÉ — le QR contient le mot de passe EN CLAIR. N'importe qui peut le
décoder depuis une simple photo. Le PNG produit (et la fiche qui l'affiche)
ne doivent JAMAIS être publiés en ligne ni apparaître sur une photo d'annonce.

Si le module `qrcode` manque : pip install --user "qrcode[pil]"
"""
import sys


def echapper(s: str) -> str:
    """Échappe les caractères spéciaux de la syntaxe WIFI: (\\ ; , : ")."""
    for c in '\\;,:"':
        s = s.replace(c, "\\" + c)
    return s


def chaine_wifi(ssid: str, password: str, auth: str = "WPA") -> str:
    if auth == "nopass":
        return f"WIFI:T:nopass;S:{echapper(ssid)};;"
    return f"WIFI:T:{auth};S:{echapper(ssid)};P:{echapper(password)};;"


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    ssid, password, out = sys.argv[1], sys.argv[2], sys.argv[3]
    auth = sys.argv[4] if len(sys.argv) > 4 else "WPA"
    if auth not in ("WPA", "WEP", "nopass"):
        print(f"Type d'authentification inconnu : {auth} (attendu WPA, WEP ou nopass)")
        sys.exit(1)

    payload = chaine_wifi(ssid, password, auth)

    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_M
    except ImportError:
        print("Module manquant : pip install --user \"qrcode[pil]\"")
        print(f"Fallback manuel — chaîne à encoder dans un générateur fiable :\n{payload}")
        sys.exit(2)

    # ERROR_CORRECT_M + box_size 14 : net à l'impression en 45-55 mm,
    # scannable même si la fiche est plastifiée ou un peu abîmée.
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_M, border=2, box_size=14)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(out)
    print(f"OK -> {out} (ne jamais publier ce fichier : mot de passe en clair)")


if __name__ == "__main__":
    main()
