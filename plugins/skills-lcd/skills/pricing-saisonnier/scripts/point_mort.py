#!/usr/bin/env python3
"""Calcul du point mort par nuitée d'une location courte durée.

Formule :
    point mort/nuitée = (charges fixes annuelles + 12 x mensualité crédit)
                        / nuits louées estimées
                        + charges variables par nuit louée
    avec nuits louées estimées = 365 x taux d'occupation.

Toujours calculer 3 hypothèses d'occupation (prudente / réaliste / haute).
Le point mort prudent est le plancher de la grille.

Exemples :
    python point_mort.py --charges-fixes 4800 --credit-mensuel 850 \
        --charges-variables-nuit 18 --occupations 0.50,0.62,0.72

    # Vérifier le bloc point_mort d'une grille existante :
    python point_mort.py --verifier grille-prix-mon-bien-2026.yaml
"""

import argparse
import json
import math
import sys

NOMS_HYPOTHESES = ["prudente", "realiste", "haute"]


def point_mort_nuitee(charges_fixes, credit_mensuel, charges_variables_nuit, occupation):
    """Point mort en €/nuitée pour un taux d'occupation donné (0 < occupation <= 1)."""
    if not 0 < occupation <= 1:
        raise ValueError(f"Taux d'occupation invalide : {occupation} (attendu entre 0 et 1)")
    nuits = 365 * occupation
    couts_annuels = charges_fixes + 12 * credit_mensuel
    return couts_annuels / nuits + charges_variables_nuit


def calculer(charges_fixes, credit_mensuel, charges_variables_nuit, occupations):
    """Renvoie la liste des hypothèses au format du bloc point_mort de la grille."""
    hypotheses = []
    for i, occ in enumerate(occupations):
        pm = point_mort_nuitee(charges_fixes, credit_mensuel, charges_variables_nuit, occ)
        hypotheses.append({
            "nom": NOMS_HYPOTHESES[i] if i < len(NOMS_HYPOTHESES) else f"hypothese-{i + 1}",
            "occupation": round(occ, 2),
            "nuits_louees": round(365 * occ),
            "point_mort_nuit": round(pm, 2),
        })
    return hypotheses


def main():
    p = argparse.ArgumentParser(description="Point mort par nuitée (3 hypothèses d'occupation).")
    p.add_argument("--charges-fixes", type=float, help="Charges fixes annuelles en €")
    p.add_argument("--credit-mensuel", type=float, default=0.0, help="Mensualité de crédit en € (défaut 0)")
    p.add_argument("--charges-variables-nuit", type=float, default=0.0, help="Charges variables par nuit louée en €")
    p.add_argument("--occupations", default="0.50,0.65,0.75",
                   help="Taux d'occupation séparés par des virgules, ex. 0.50,0.62,0.72")
    p.add_argument("--json", action="store_true", help="Sortie JSON (bloc point_mort prêt pour la grille)")
    p.add_argument("--verifier", metavar="GRILLE.yaml",
                   help="Recalcule le bloc point_mort d'une grille existante et signale les écarts")
    args = p.parse_args()

    if args.verifier:
        return verifier_grille(args.verifier)

    if args.charges_fixes is None:
        p.error("--charges-fixes est requis (ou utiliser --verifier)")

    occupations = [float(x) for x in args.occupations.split(",") if x.strip()]
    hypotheses = calculer(args.charges_fixes, args.credit_mensuel,
                          args.charges_variables_nuit, occupations)
    plancher = math.ceil(max(h["point_mort_nuit"] for h in hypotheses))

    if args.json:
        print(json.dumps({
            "charges_fixes_annuelles": args.charges_fixes,
            "mensualite_credit": args.credit_mensuel,
            "charges_variables_nuit": args.charges_variables_nuit,
            "hypotheses": hypotheses,
            "plancher_retenu": plancher,
        }, ensure_ascii=False, indent=2))
        return 0

    couts = args.charges_fixes + 12 * args.credit_mensuel
    print(f"Coûts annuels fixes : {couts:,.0f} € "
          f"({args.charges_fixes:,.0f} € charges + 12 x {args.credit_mensuel:,.0f} € crédit)".replace(",", " "))
    print(f"Charges variables : {args.charges_variables_nuit:.2f} €/nuit louée\n")
    print(f"{'Hypothèse':<12}{'Occupation':>12}{'Nuits/an':>10}{'Point mort':>14}")
    for h in hypotheses:
        print(f"{h['nom']:<12}{h['occupation'] * 100:>10.0f} %{h['nuits_louees']:>10}"
              f"{h['point_mort_nuit']:>11.2f} €")
    print(f"\nPlancher de grille retenu (hypothèse la plus prudente, arrondi sup.) : {plancher} €/nuit")
    return 0


def verifier_grille(chemin):
    """Relit le bloc point_mort d'une grille YAML et recalcule chaque hypothèse."""
    try:
        import yaml  # PyYAML, présent dans la plupart des environnements
    except ImportError:
        print("PyYAML indisponible : vérifier à la main avec les options --charges-fixes etc.",
              file=sys.stderr)
        return 1
    with open(chemin, encoding="utf-8") as f:
        grille = yaml.safe_load(f)
    pm = grille.get("point_mort") or {}
    cf = pm.get("charges_fixes_annuelles", 0)
    cm = pm.get("mensualite_credit", 0)
    cv = pm.get("charges_variables_nuit", 0)
    ecarts = 0
    for h in pm.get("hypotheses", []):
        attendu = round(point_mort_nuitee(cf, cm, cv, h["occupation"]), 2)
        declare = h.get("point_mort_nuit")
        ok = declare is not None and abs(attendu - declare) <= 1.0  # tolérance 1 € d'arrondi
        statut = "OK " if ok else "ECART"
        if not ok:
            ecarts += 1
        print(f"[{statut}] {h.get('nom', '?'):<10} occ {h['occupation'] * 100:.0f} % : "
              f"déclaré {declare} € / recalculé {attendu} €")
    plancher = pm.get("plancher_retenu")
    if pm.get("hypotheses"):
        attendu_plancher = math.ceil(max(
            point_mort_nuitee(cf, cm, cv, h["occupation"]) for h in pm["hypotheses"]))
        ok = plancher is not None and abs(plancher - attendu_plancher) <= 1
        if not ok:
            ecarts += 1
        print(f"[{'OK ' if ok else 'ECART'}] plancher_retenu : déclaré {plancher} € / "
              f"recalculé {attendu_plancher} €")
    print("\nAucun écart — point mort cohérent." if ecarts == 0
          else f"\n{ecarts} écart(s) à corriger dans la grille.")
    return 0 if ecarts == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
