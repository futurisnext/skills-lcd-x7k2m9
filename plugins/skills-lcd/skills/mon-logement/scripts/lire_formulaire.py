#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lit un formulaire « Mon logement » rempli et affiche son contenu en JSON.

Usage :
    python3 scripts/lire_formulaire.py <chemin/du/formulaire.pdf>

Sortie (stdout) : un objet JSON
    {
      "ok": true,
      "champs": { "logement__nom": "La Canopée…", ... },   # champs remplis
      "champs_vides": ["chiffres__mensualite_credit", ...], # à demander à l'hôte
      "alertes": ["..."]                                    # incohérences détectées
    }

En cas de PDF illisible ou sans formulaire : {"ok": false, "erreur": "..."}
→ dans ce cas, basculer sur l'interview conversationnelle (voir SKILL.md).

Dépendance : pypdf (pip install --user pypdf)
"""

import json
import sys


def _nettoyer(valeur):
    """Normalise une valeur de champ AcroForm en chaîne propre."""
    if valeur is None:
        return ""
    texte = str(valeur).strip()
    # Les groupes de boutons radio renvoient parfois "/valeur" ou "/Off"
    if texte.startswith("/"):
        texte = texte[1:]
    if texte in ("Off", ""):
        return ""
    return texte


def _nombre(texte):
    """Tente de convertir un texte saisi par l'hôte en nombre (gère '180 €', '0,90')."""
    brut = (texte.replace("€", "").replace("%", "").replace(",", ".")
            .replace(" ", "").replace("\xa0", "").replace(" ", "").strip())
    try:
        n = float(brut)
        return int(n) if n == int(n) else n
    except ValueError:
        return None


def lire(chemin):
    try:
        from pypdf import PdfReader
    except ImportError:
        return {"ok": False,
                "erreur": "pypdf n'est pas installé (pip install --user pypdf)"}

    try:
        lecteur = PdfReader(chemin)
        champs_bruts = lecteur.get_fields()
    except Exception as exc:  # PDF corrompu, chiffré, etc.
        return {"ok": False, "erreur": f"PDF illisible : {exc}"}

    if not champs_bruts:
        return {"ok": False,
                "erreur": "Aucun champ de formulaire trouvé dans ce PDF "
                          "(ce n'est probablement pas le formulaire Mon logement)."}

    champs, vides = {}, []
    for nom, definition in champs_bruts.items():
        valeur = _nettoyer(definition.get("/V"))
        if valeur:
            champs[nom] = valeur
        else:
            vides.append(nom)

    # --- contrôles de cohérence simples (les alertes sont à reposer à l'hôte) ---
    alertes = []
    v = {cle: _nombre(val) for cle, val in champs.items()}

    moyen = v.get("chiffres__prix_moyen_nuit")
    mini = v.get("chiffres__prix_min_nuit")
    maxi = v.get("chiffres__prix_max_nuit")
    if mini is not None and maxi is not None and mini > maxi:
        alertes.append("Le prix le plus bas est supérieur au prix le plus haut.")
    if moyen is not None and mini is not None and moyen < mini:
        alertes.append("Le prix moyen est inférieur au prix le plus bas.")
    if moyen is not None and maxi is not None and moyen > maxi:
        alertes.append("Le prix moyen est supérieur au prix le plus haut.")

    occupation = v.get("chiffres__taux_occupation_pct")
    if occupation is not None and not (0 <= occupation <= 100):
        alertes.append("Le taux d'occupation n'est pas entre 0 et 100 %.")

    taxe = v.get("chiffres__taxe_sejour_pers_nuit")
    if taxe is not None and taxe > 10:
        alertes.append("La taxe de séjour semble très élevée — montant par personne "
                       "et par nuit attendu (souvent < 5 €).")

    # Champs numériques remplis mais non convertibles en nombre
    numeriques = [cle for cle in champs
                  if cle.startswith("chiffres__") and cle != "chiffres__objectif"
                  or cle in ("capacite__voyageurs", "capacite__chambres",
                             "capacite__salles_de_bain", "capacite__surface_m2")]
    for cle in numeriques:
        if v.get(cle) is None:
            alertes.append(f"Le champ « {cle} » contient « {champs[cle]} », "
                           "qui ne ressemble pas à un nombre.")

    wifi = champs.get("sejour__wifi_nom", "")
    if any(mot in wifi.lower() for mot in ("mdp", "mot de passe", "password", "pass:")):
        alertes.append("Le champ WiFi semble contenir un mot de passe : ne garder que "
                       "le NOM du réseau, ne jamais stocker le mot de passe.")

    return {"ok": True, "champs": champs, "champs_vides": sorted(vides),
            "alertes": alertes}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"ok": False,
                          "erreur": "Usage : python3 lire_formulaire.py <formulaire.pdf>"},
                         ensure_ascii=False))
        sys.exit(1)
    print(json.dumps(lire(sys.argv[1]), ensure_ascii=False, indent=2))
