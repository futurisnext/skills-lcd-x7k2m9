#!/usr/bin/env python3
"""parse_resas.py — lit les exports de réservations d'une location courte durée
et calcule les chiffres du mois selon les conventions du skill pilotage-dashboard.

Formats reconnus (détection automatique par l'en-tête, FR et EN) :
  - Export CSV Airbnb « Réservations » (Confirmation code / Code de confirmation…)
  - Export CSV Airbnb « Revenus » (Gross earnings / Revenus bruts, Cleaning fee…)
  - Export Booking.com (Book number / Numéro de réservation, Check-in / Arrivée…)
  - Résas en direct, format minimal : arrivee, depart, montant (+ menage, voyageur, canal)

Conventions appliquées (doctrine pilotage) :
  - Une résa à cheval sur 2 mois est ventilée au prorata des nuits dormies dans le mois.
  - Les annulations sont EXCLUES du CA ; leurs indemnités sont comptées à part.
  - Frais de ménage et taxe de séjour sont sortis du CA hébergement.
  - Devise détectée ; alerte si plusieurs devises se mélangent.

Sortie : un JSON propre sur stdout (KPI du mois + détail par résa + avertissements).
Les avertissements sont aussi répétés sur stderr. Code retour 0 même avec des
avertissements ; 2 si AUCUNE donnée exploitable (le fallback manuel prend le relais).

Exemples :
  python3 parse_resas.py --mois 2026-05 export-airbnb.csv --menage-par-sejour 60
  python3 parse_resas.py --mois 2026-06 export-airbnb.csv resas-direct.csv \
      --menage-par-sejour 60 --nuits-bloquees 2 > chiffres-2026-06.json
"""

import argparse
import calendar
import csv
import json
import os
import re
import sys
import unicodedata
from datetime import date, datetime, timedelta

# ---------------------------------------------------------------------------
# Normalisation des en-têtes et synonymes de colonnes (FR + EN)
# ---------------------------------------------------------------------------

def normaliser(texte):
    """minuscule, sans accents, '#' -> 'nb', ponctuation -> espaces simples."""
    t = unicodedata.normalize("NFKD", str(texte))
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower().replace("#", " nb ")
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return t.strip()


# champ canonique -> en-têtes possibles (déjà normalisés)
SYNONYMES = {
    "code": ["confirmation code", "code de confirmation", "book number",
             "numero de reservation", "reservation number", "reservation id",
             "booking code", "code", "reference", "numero"],
    "statut": ["status", "statut"],
    "voyageur": ["guest name", "nom du voyageur", "guest name s", "guest names",
                 "voyageur", "guest", "nom", "name", "nom du client",
                 "client name", "customer name"],
    "personnes": ["nb of adults", "nombre d adultes", "adults", "adultes",
                  "persons", "personnes", "guests", "people"],
    "enfants": ["nb of children", "nombre d enfants", "children", "enfants"],
    "bebes": ["nb of infants", "nombre de bebes", "infants", "bebes"],
    "arrivee": ["start date", "date de debut", "check in", "checkin",
                "check in date", "checkin date", "arrivee", "arrival",
                "date d arrivee", "arrival date"],
    "depart": ["end date", "date de fin", "check out", "checkout",
               "check out date", "checkout date", "depart", "departure",
               "date de depart", "departure date"],
    "nuits": ["nb of nights", "nombre de nuits", "nights", "nuits"],
    "reserve_le": ["booked", "reservee", "booked date", "booking date",
                   "date de reservation", "reserve le", "booked on"],
    "annonce": ["listing", "annonce", "listing name", "property", "logement",
                "property name", "nom de l annonce"],
    "montant": ["earnings", "revenus", "amount", "montant", "price", "tarif",
                "total price", "prix", "total payout", "payout", "revenue",
                "montant total", "total"],
    "montant_hebergement": ["montant hebergement", "hebergement",
                            "accommodation amount", "base amount", "base price"],
    "montant_brut": ["gross earnings", "revenus bruts", "gross booking value"],
    "menage": ["cleaning fee", "frais de menage", "menage", "cleaning",
               "cleaning fees"],
    "taxe_sejour": ["occupancy taxes", "taxe de sejour", "taxes de sejour",
                    "tourist tax", "city tax", "taxes d occupation",
                    "pass through tot", "occupancy tax"],
    "commission": ["host fee", "service fee", "host service fee", "commission",
                   "commission amount", "montant de la commission",
                   "frais de service", "frais de service hote"],
    "devise": ["currency", "devise"],
    "canal": ["canal", "channel", "platform", "plateforme", "source"],
    # colonnes connues mais sans usage dans les KPI (pas d'avertissement) :
    "_ignore": ["booked by", "reserve par", "contact", "phone", "telephone",
                "email", "remarks", "remarques",
                "rooms", "chambres", "details", "type", "date", "paid out",
                "location", "zip code", "country", "unit", "smart pricing"],
}

CARTE = {}
for champ, alias in SYNONYMES.items():
    for a in alias:
        CARTE[a] = champ

MOTIFS_ANNULATION = ("annul", "cancel", "no show", "no-show")
SYMBOLES_DEVISE = {"€": "EUR", "$": "USD", "£": "GBP", "chf": "CHF",
                   "eur": "EUR", "usd": "USD", "gbp": "GBP"}


# ---------------------------------------------------------------------------
# Lecture bas niveau : encodage, séparateur, en-tête
# ---------------------------------------------------------------------------

def lire_lignes(chemin, warnings):
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(chemin, encoding=enc) as f:
                contenu = f.read()
            if enc != "utf-8-sig":
                warnings.append(f"{chemin} : encodage {enc} détecté (pas UTF-8).")
            return contenu
        except UnicodeDecodeError:
            continue
    raise IOError(f"Impossible de décoder {chemin}")


def detecter_separateur(premiere_ligne):
    comptes = {sep: premiere_ligne.count(sep) for sep in (",", ";", "\t")}
    return max(comptes, key=comptes.get) if max(comptes.values()) else ","


def mapper_entete(entete, chemin, warnings):
    """Associe chaque colonne du fichier à un champ canonique."""
    mapping, inconnues = {}, []
    for i, brut in enumerate(entete):
        champ = CARTE.get(normaliser(brut))
        if champ is None:
            inconnues.append(brut.strip())
        elif champ != "_ignore" and champ not in mapping:
            mapping[champ] = i
    if inconnues:
        warnings.append(f"{chemin} : colonnes inconnues ignorées : "
                        + ", ".join(repr(c) for c in inconnues) + ".")
    return mapping


def detecter_format(mapping):
    if "montant_brut" in mapping or ("menage" in mapping and "commission" in mapping):
        return "airbnb-revenus"
    if "code" in mapping and "nuits" in mapping and "statut" in mapping:
        return "airbnb-reservations"
    if "commission" in mapping or ("code" in mapping and "personnes" in mapping
                                   and "statut" in mapping):
        return "booking"
    return "direct"


# ---------------------------------------------------------------------------
# Dates et montants
# ---------------------------------------------------------------------------

def _essai_date(s, jour_d_abord):
    s = s.strip()
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.match(r"^(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})$", s)
    if not m:
        return None
    a, b, an = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if an < 100:
        an += 2000
    j, mo = (a, b) if jour_d_abord else (b, a)
    try:
        return date(an, mo, j)
    except ValueError:
        return None


def choisir_ordre_dates(valeurs, chemin, warnings):
    """Décide JJ/MM (FR) ou MM/JJ (EN) sur l'ensemble du fichier."""
    indices_jj, indices_mm = False, False
    for v in valeurs:
        m = re.match(r"^(\d{1,2})[/.\-](\d{1,2})[/.\-]\d{2,4}$", str(v).strip())
        if m:
            if int(m.group(1)) > 12:
                indices_jj = True
            if int(m.group(2)) > 12:
                indices_mm = True
    if indices_jj and indices_mm:
        warnings.append(f"{chemin} : formats de dates contradictoires — "
                        "JJ/MM supposé, à VÉRIFIER ligne par ligne.")
        return True
    if indices_jj:
        return True
    if indices_mm:
        return False
    if any(re.match(r"^\d{1,2}[/.\-]", str(v).strip()) for v in valeurs):
        warnings.append(f"{chemin} : dates ambiguës (aucun jour > 12) — "
                        "format JJ/MM/AAAA supposé. À vérifier avec l'hôte.")
    return True


def parser_montant(s, devises_vues):
    """'1 234,56 €' / '$1,234.56' / '450' -> float. None si vide/illisible."""
    if s is None:
        return None
    s = str(s).strip()
    if not s:
        return None
    bas = s.lower()
    for symbole, code in SYMBOLES_DEVISE.items():
        if symbole in bas:
            devises_vues.add(code)
            break
    s = re.sub(r"[^\d,.\-]", "", s)
    if not re.search(r"\d", s):
        return None
    if "," in s and "." in s:
        # le dernier séparateur est le séparateur décimal
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        # virgule décimale (FR) si 1-2 décimales, sinon séparateur de milliers
        s = s.replace(",", ".") if re.search(r",\d{1,2}$", s) else s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Lecture d'un fichier d'export -> liste de réservations normalisées
# ---------------------------------------------------------------------------

def lire_export(chemin, args, warnings, devises_vues):
    contenu = lire_lignes(chemin, warnings)
    lignes = [l for l in contenu.splitlines() if l.strip()]
    if not lignes:
        warnings.append(f"{chemin} : fichier vide — ignoré.")
        return [], {"fichier": chemin, "format": "vide", "lignes_lues": 0,
                    "lignes_ignorees": 0}
    sep = detecter_separateur(lignes[0])
    rangees = list(csv.reader(lignes, delimiter=sep))
    mapping = mapper_entete(rangees[0], chemin, warnings)
    fmt = detecter_format(mapping)

    if "arrivee" not in mapping or "depart" not in mapping:
        warnings.append(f"{chemin} : impossible de trouver les colonnes de dates "
                        "d'arrivée/départ — fichier NON exploité. Passe en lecture "
                        "manuelle (chiffres à faire valider par l'hôte).")
        return [], {"fichier": chemin, "format": "inconnu",
                    "lignes_lues": len(rangees) - 1, "lignes_ignorees": len(rangees) - 1}
    if not any(k in mapping for k in ("montant", "montant_hebergement", "montant_brut")):
        warnings.append(f"{chemin} : aucune colonne de montant reconnue — "
                        "fichier NON exploité.")
        return [], {"fichier": chemin, "format": fmt,
                    "lignes_lues": len(rangees) - 1, "lignes_ignorees": len(rangees) - 1}

    echantillon = [r[mapping["arrivee"]] for r in rangees[1:] if len(r) > mapping["arrivee"]]
    echantillon += [r[mapping["depart"]] for r in rangees[1:] if len(r) > mapping["depart"]]
    jour_d_abord = choisir_ordre_dates(echantillon, chemin, warnings)

    canal_defaut = {"airbnb-reservations": "airbnb", "airbnb-revenus": "airbnb",
                    "booking": "booking"}.get(fmt, args.canal_defaut)

    resas, ignorees = [], 0
    for num, r in enumerate(rangees[1:], start=2):
        if len(r) < max(mapping.values()) + 1:
            ignorees += 1
            warnings.append(f"{chemin} ligne {num} : ligne incomplète "
                            f"({len(r)} champs au lieu de {len(rangees[0])}) — ignorée.")
            continue

        def champ(nom):
            return r[mapping[nom]].strip() if nom in mapping else ""

        arrivee = _essai_date(champ("arrivee"), jour_d_abord)
        depart = _essai_date(champ("depart"), jour_d_abord)
        if not arrivee or not depart:
            ignorees += 1
            warnings.append(f"{chemin} ligne {num} : date illisible "
                            f"(« {champ('arrivee')} » / « {champ('depart')} ») — ignorée.")
            continue
        if depart <= arrivee:
            ignorees += 1
            warnings.append(f"{chemin} ligne {num} : départ {depart} ≤ arrivée "
                            f"{arrivee} — ignorée (vérifier le format des dates).")
            continue

        nuits_total = (depart - arrivee).days
        nuits_declarees = champ("nuits")
        if nuits_declarees and nuits_declarees.isdigit() and int(nuits_declarees) != nuits_total:
            warnings.append(f"{chemin} ligne {num} : colonne nuits = {nuits_declarees} "
                            f"mais les dates donnent {nuits_total} — les DATES font foi.")

        statut = champ("statut")
        annulee = any(motif in normaliser(statut) for motif in MOTIFS_ANNULATION)

        montant = parser_montant(champ("montant"), devises_vues)
        montant_brut = parser_montant(champ("montant_brut"), devises_vues)
        montant_heb_direct = parser_montant(champ("montant_hebergement"), devises_vues)
        menage = parser_montant(champ("menage"), devises_vues)
        taxe = parser_montant(champ("taxe_sejour"), devises_vues)
        commission = parser_montant(champ("commission"), devises_vues)

        if champ("devise"):
            devises_vues.add(champ("devise").upper())

        # Montant hébergement : la valeur la plus « propre » disponible.
        if montant_heb_direct is not None:
            hebergement = montant_heb_direct
        else:
            # le brut (avant commission) est la bonne base du CA hébergement ;
            # la commission est suivie à part, jamais déduite du CA
            base = montant_brut if montant_brut is not None else montant
            if base is None:
                ignorees += 1
                if not annulee:
                    warnings.append(f"{chemin} ligne {num} : montant illisible "
                                    f"(« {champ('montant')} ») — ignorée.")
                continue
            hebergement = base
            if menage is not None:
                hebergement -= menage
            elif args.menage_par_sejour and not annulee:
                menage = args.menage_par_sejour
                hebergement -= menage
            if taxe:
                # les exports Airbnb/Booking séparent normalement la taxe du montant ;
                # on ne la déduit pas, on la suit à part — mais on prévient.
                warnings.append(f"{chemin} ligne {num} : taxe de séjour {taxe:.2f} "
                                "détectée — supposée NON incluse dans le montant "
                                "(comportement normal des exports). À vérifier si doute.")

        resas.append({
            "code": champ("code") or f"{os.path.basename(chemin)}:ligne{num}",
            "voyageur": champ("voyageur"),
            "canal": (champ("canal") or canal_defaut).lower(),
            "statut": statut or "confirmée",
            "annulee": annulee,
            "arrivee": arrivee,
            "depart": depart,
            "nuits_total": nuits_total,
            "hebergement": round(hebergement, 2),
            "menage": menage or 0.0,
            "taxe_sejour": taxe or 0.0,
            "commission": commission or 0.0,
            "indemnite": round(montant if (annulee and montant) else 0.0, 2),
            "fichier": chemin,
        })

    return resas, {"fichier": chemin, "format": fmt,
                   "lignes_lues": len(rangees) - 1, "lignes_ignorees": ignorees}


# ---------------------------------------------------------------------------
# Ventilation mensuelle et KPI
# ---------------------------------------------------------------------------

def nuits_dans_mois(resa, annee, mois):
    n = 0
    d = resa["arrivee"]
    while d < resa["depart"]:
        if d.year == annee and d.month == mois:
            n += 1
        d += timedelta(days=1)
    return n


def calculer(resas, annee, mois, args, warnings):
    nb_jours = calendar.monthrange(annee, mois)[1]
    debut_mois = date(annee, mois, 1)
    fin_mois = date(annee, mois, nb_jours)

    actives = [r for r in resas if not r["annulee"]]
    detail, ca, nuits, menage_mois, taxe_mois, commission_mois = [], 0.0, 0, 0.0, 0.0, 0.0
    indemnites = 0.0
    par_canal = {}

    for r in resas:
        n_mois = nuits_dans_mois(r, annee, mois)
        if r["annulee"]:
            if r["indemnite"] and debut_mois <= r["arrivee"] <= fin_mois:
                indemnites += r["indemnite"]
                detail.append({
                    "code": r["code"], "voyageur": r["voyageur"], "canal": r["canal"],
                    "statut": r["statut"], "arrivee": r["arrivee"].isoformat(),
                    "depart": r["depart"].isoformat(), "nuits_total": r["nuits_total"],
                    "nuits_dans_mois": 0, "ca_hebergement_mois": 0.0,
                    "indemnite_annulation": r["indemnite"],
                })
            continue
        if n_mois == 0:
            continue
        part = r["hebergement"] * n_mois / r["nuits_total"]
        ca += part
        nuits += n_mois
        c = par_canal.setdefault(r["canal"], {"ca_hebergement": 0.0, "nuits": 0})
        c["ca_hebergement"] += part
        c["nuits"] += n_mois
        if debut_mois <= r["arrivee"] <= fin_mois:
            menage_mois += r["menage"]
            taxe_mois += r["taxe_sejour"]
            commission_mois += r["commission"]
        detail.append({
            "code": r["code"], "voyageur": r["voyageur"], "canal": r["canal"],
            "statut": r["statut"], "arrivee": r["arrivee"].isoformat(),
            "depart": r["depart"].isoformat(), "nuits_total": r["nuits_total"],
            "nuits_dans_mois": n_mois, "ca_hebergement_mois": round(part, 2),
            "prix_moyen_nuit_sejour": round(r["hebergement"] / r["nuits_total"], 2),
            "a_cheval": n_mois < r["nuits_total"],
        })

    nuits_disponibles = nb_jours - args.nuits_bloquees
    if nuits > nuits_disponibles:
        warnings.append(f"{nuits} nuits louées > {nuits_disponibles} nuits disponibles : "
                        "doublons probables entre fichiers ou surréservation — À VÉRIFIER.")

    # Réservations à venir (après la fin du mois analysé) : matière pour les alertes
    a_venir = {}
    for r in actives:
        d = max(r["arrivee"], fin_mois + timedelta(days=1))
        while d < r["depart"]:
            cle = f"{d.year:04d}-{d.month:02d}"
            a_venir.setdefault(cle, {"nuits_reservees": 0, "ca_attendu": 0.0})
            a_venir[cle]["nuits_reservees"] += 1
            a_venir[cle]["ca_attendu"] += r["hebergement"] / r["nuits_total"]
            d += timedelta(days=1)
    for v in a_venir.values():
        v["ca_attendu"] = round(v["ca_attendu"], 2)

    # Couverture de la période
    if actives:
        depart_max = max(r["depart"] for r in actives)
        arrivee_min = min(r["arrivee"] for r in actives)
        if depart_max <= fin_mois:
            warnings.append("Aucune réservation au-delà du mois analysé : l'export "
                            "couvre peut-être une période incomplète (résas de fin de "
                            "mois ou à venir absentes ?).")
        periode = {"de": arrivee_min.isoformat(), "a": depart_max.isoformat()}
    else:
        periode = None
        warnings.append("Aucune réservation active exploitable — rien à calculer.")

    detail.sort(key=lambda d: d["arrivee"])
    occupation = nuits / nuits_disponibles if nuits_disponibles else 0
    return {
        "kpi": {
            "ca_hebergement": round(ca, 2),
            "nuits_louees": nuits,
            "nuits_disponibles": nuits_disponibles,
            "nuits_bloquees": args.nuits_bloquees,
            "occupation_pct": round(100 * occupation, 1),
            "adr": round(ca / nuits, 2) if nuits else None,
            "revpar": round(ca / nuits_disponibles, 2) if nuits_disponibles else None,
        },
        "a_cote_du_ca": {
            "menage_facture": round(menage_mois, 2),
            "taxe_sejour": round(taxe_mois, 2),
            "commissions_plateformes": round(commission_mois, 2),
            "indemnites_annulation": round(indemnites, 2),
        },
        "mix_canaux": {
            canal: {"ca_hebergement": round(v["ca_hebergement"], 2),
                    "nuits": v["nuits"],
                    "part_ca_pct": round(100 * v["ca_hebergement"] / ca, 1) if ca else 0}
            for canal, v in sorted(par_canal.items())
        },
        "reservations_du_mois": detail,
        "a_venir": dict(sorted(a_venir.items())),
        "periode_couverte_par_les_exports": periode,
    }


# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        description="Chiffres du mois d'une LCD à partir des exports de réservations.")
    p.add_argument("fichiers", nargs="+", help="exports CSV (Airbnb, Booking, direct)")
    p.add_argument("--mois", required=True, metavar="AAAA-MM",
                   help="mois à analyser, ex. 2026-05")
    p.add_argument("--menage-par-sejour", type=float, default=0.0,
                   help="frais de ménage par séjour (€) à soustraire quand l'export "
                        "n'a pas de colonne ménage (ex. export Airbnb Réservations)")
    p.add_argument("--nuits-bloquees", type=int, default=0,
                   help="nuits bloquées par l'hôte ce mois-ci (usage perso, travaux)")
    p.add_argument("--canal-defaut", default="direct",
                   help="canal attribué aux fichiers au format minimal (défaut: direct)")
    args = p.parse_args()

    m = re.match(r"^(\d{4})-(\d{2})$", args.mois)
    if not m:
        p.error("--mois attendu au format AAAA-MM (ex. 2026-05)")
    annee, mois = int(m.group(1)), int(m.group(2))

    warnings, devises_vues = [], set()
    resas, fichiers_info = [], []
    for chemin in args.fichiers:
        try:
            r, info = lire_export(chemin, args, warnings, devises_vues)
        except (IOError, OSError) as e:
            warnings.append(f"{chemin} : lecture impossible ({e}) — fichier ignoré.")
            fichiers_info.append({"fichier": chemin, "format": "erreur",
                                  "lignes_lues": 0, "lignes_ignorees": 0})
            continue
        resas.extend(r)
        fichiers_info.append(info)

    # Déduplication par code de confirmation entre fichiers
    vus, dedup = {}, []
    for r in resas:
        cle = r["code"]
        if cle in vus:
            warnings.append(f"Réservation {cle} présente dans {vus[cle]} ET "
                            f"{r['fichier']} — comptée une seule fois.")
            continue
        vus[cle] = r["fichier"]
        dedup.append(r)

    if len(devises_vues) > 1:
        warnings.append("Plusieurs devises détectées (" + ", ".join(sorted(devises_vues))
                        + ") — les montants NE SONT PAS convertis, à traiter avec l'hôte.")
    if args.menage_par_sejour:
        warnings.append(f"Ménage estimé à {args.menage_par_sejour:.0f} € par séjour "
                        "(option --menage-par-sejour) pour les exports sans colonne "
                        "ménage — à confirmer avec l'hôte.")

    resultat = {
        "mois": args.mois,
        "genere_le": datetime.now().strftime("%Y-%m-%d"),
        "devise": sorted(devises_vues)[0] if len(devises_vues) == 1
                  else (sorted(devises_vues) if devises_vues else "EUR (supposée)"),
        "fichiers": fichiers_info,
        "conventions": [
            "CA hébergement hors frais de ménage et hors taxe de séjour",
            "séjours à cheval ventilés au prorata des nuits dormies dans le mois",
            "annulations exclues du CA, indemnités comptées à part",
        ],
    }
    resultat.update(calculer(dedup, annee, mois, args, warnings))
    resultat["avertissements"] = warnings

    json.dump(resultat, sys.stdout, ensure_ascii=False, indent=2)
    print()
    for w in warnings:
        print("AVERTISSEMENT :", w, file=sys.stderr)

    exploitables = sum(1 for r in dedup if not r["annulee"])
    return 0 if exploitables else 2


if __name__ == "__main__":
    sys.exit(main())
