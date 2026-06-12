#!/usr/bin/env python3
"""Convertit une fiche HTML print-ready en PDF A4 — avec chaîne de fallbacks.

Usage :
    python html_to_pdf.py fiche.html [fiche.pdf] [--pages-attendues N]

Stratégie (premier moyen disponible qui marche) :
  1. Chrome / Chromium / Edge headless (`--print-to-pdf`) — rendu fidèle,
     cherché dans le PATH, les emplacements classiques (Linux/macOS/Windows)
     et le cache navigateurs de Playwright (~/.cache/ms-playwright).
  2. WeasyPrint (si le module Python et ses bibliothèques système sont là).
  3. Sinon : code de sortie 3 → livrer le HTML tel quel et indiquer à l'hôte
     comment l'imprimer depuis son navigateur (toujours un chemin qui marche).

`--pages-attendues N` vérifie le nombre de pages du PDF produit (une fiche =
une page A4 : la garantie qualité du kit). Échec → code de sortie 4.

Codes de sortie : 0 ok · 1 mauvais usage · 3 aucun convertisseur · 4 nombre
de pages inattendu (le PDF est quand même produit).
"""
import glob
import os
import shutil
import subprocess
import sys


def candidats_chromium():
    """Tous les binaires Chrome/Chromium plausibles, par ordre de préférence."""
    noms_path = [
        "chromium", "chromium-browser", "google-chrome", "google-chrome-stable",
        "chrome", "msedge", "microsoft-edge", "brave-browser",
    ]
    for nom in noms_path:
        binaire = shutil.which(nom)
        if binaire:
            yield binaire
    chemins_fixes = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    ]
    for chemin in chemins_fixes:
        if os.path.isfile(chemin):
            yield chemin
    # Navigateurs installés par Playwright (fréquents sur les postes Claude)
    cache = os.path.expanduser("~/.cache/ms-playwright")
    for motif in ("chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell",
                  "chromium-*/chrome-linux64/chrome",
                  "chromium-*/chrome-linux/chrome"):
        for chemin in sorted(glob.glob(os.path.join(cache, motif)), reverse=True):
            yield chemin


def env_execution():
    """Environnement d'exécution, enrichi de bibliothèques locales éventuelles.

    Certains environnements sans droits admin stockent les .so manquants de
    Chromium dans ~/.cache/lcd-skills/chromium-libs (téléchargés via
    `apt-get download` + `dpkg -x`, sans sudo). On les ajoute si présents.
    """
    env = os.environ.copy()
    extra = os.path.expanduser("~/.cache/lcd-skills/chromium-libs")
    if os.path.isdir(extra):
        env["LD_LIBRARY_PATH"] = extra + os.pathsep + env.get("LD_LIBRARY_PATH", "")
    return env


def convertir_chromium(html_abs, pdf_abs):
    for binaire in candidats_chromium():
        cmd = [
            binaire, "--headless", "--disable-gpu", "--no-sandbox",
            "--no-pdf-header-footer", "--print-to-pdf=" + pdf_abs,
            "file://" + html_abs,
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True,
                                 timeout=120, env=env_execution())
        except (subprocess.TimeoutExpired, OSError):
            continue
        if res.returncode == 0 and os.path.isfile(pdf_abs) and os.path.getsize(pdf_abs) > 0:
            return binaire
    return None


def convertir_weasyprint(html_abs, pdf_abs):
    try:
        from weasyprint import HTML  # noqa: import tardif volontaire
    except Exception:
        return False
    try:
        HTML(filename=html_abs).write_pdf(pdf_abs)
        return os.path.isfile(pdf_abs) and os.path.getsize(pdf_abs) > 0
    except Exception:
        return False


def compter_pages(pdf_abs):
    try:
        from pypdf import PdfReader
        return len(PdfReader(pdf_abs).pages)
    except Exception:
        try:
            import fitz  # PyMuPDF
            with fitz.open(pdf_abs) as doc:
                return doc.page_count
        except Exception:
            return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pages_attendues = None
    if "--pages-attendues" in sys.argv:
        try:
            pages_attendues = int(sys.argv[sys.argv.index("--pages-attendues") + 1])
        except (IndexError, ValueError):
            print("--pages-attendues attend un nombre entier")
            sys.exit(1)
        args = [a for a in args if a != str(pages_attendues)]

    if not args:
        print(__doc__)
        sys.exit(1)
    html = args[0]
    if not os.path.isfile(html):
        print(f"Fichier introuvable : {html}")
        sys.exit(1)
    pdf = args[1] if len(args) > 1 else os.path.splitext(html)[0] + ".pdf"
    html_abs, pdf_abs = os.path.abspath(html), os.path.abspath(pdf)

    moteur = convertir_chromium(html_abs, pdf_abs)
    if moteur:
        print(f"PDF généré via Chromium ({moteur})")
    elif convertir_weasyprint(html_abs, pdf_abs):
        print("PDF généré via WeasyPrint")
    else:
        print("Aucun convertisseur PDF disponible (ni Chromium/Chrome headless, ni WeasyPrint).")
        print("→ Livrer le HTML tel quel : il s'imprime très bien depuis un navigateur")
        print("  (Fichier > Imprimer, format A4, marges par défaut, « Graphiques d'arrière-plan » cochés).")
        sys.exit(3)

    nb = compter_pages(pdf_abs)
    if nb is not None:
        print(f"{pdf_abs} — {nb} page(s)")
        if pages_attendues is not None and nb != pages_attendues:
            print(f"ATTENTION : {nb} page(s) au lieu de {pages_attendues} attendue(s) — "
                  "du contenu déborde probablement. Raccourcir ou rééquilibrer la fiche.")
            sys.exit(4)
    else:
        print(pdf_abs)


if __name__ == "__main__":
    main()
