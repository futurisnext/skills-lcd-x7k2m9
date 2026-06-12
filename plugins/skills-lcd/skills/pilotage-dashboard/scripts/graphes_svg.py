#!/usr/bin/env python3
"""graphes_svg.py — génère les courbes du rapport de pilotage en SVG inline.

Lit l'historique (`historique-pilotage-<logement>.yaml`, schéma du skill) et écrit
un fragment HTML contenant jusqu'à 4 graphiques (12 derniers mois) :
  1. CA hébergement (barres) + ligne objectif mensuel
  2. Taux d'occupation (courbe)
  3. ADR (courbe) + lignes point mort réaliste et prudent
  4. Cumul de l'année civile en cours vs objectif cumulé sur les mois suivis

SVG pur, zéro dépendance réseau : le rapport reste lisible hors-ligne et propre à
l'impression. Les chiffres viennent de l'historique — ne JAMAIS retoucher les
courbes à la main : corriger l'historique puis régénérer.

Usage :
  python3 graphes_svg.py historique-pilotage-la-canopee-du-herisson.yaml \
      [--mois 2026-06] [--sortie courbes.html]
"""

import argparse
import re
import sys

LARGEUR, HAUTEUR = 660, 210
MARGE_G, MARGE_D, MARGE_H, MARGE_B = 56, 16, 22, 30
ACCENT = "#2f5d50"
ACCENT_CLAIR = "#7fa99b"
ROUGE = "#b4543e"
GRIS = "#999"
MOIS_FR = ["janv.", "févr.", "mars", "avr.", "mai", "juin",
           "juil.", "août", "sept.", "oct.", "nov.", "déc."]


# ---------------------------------------------------------------------------
# Lecture de l'historique (PyYAML si présent, sinon lecture ligne à ligne
# calée sur le schéma du skill — voir references/schema-historique.md)
# ---------------------------------------------------------------------------

def lire_historique(chemin):
    texte = open(chemin, encoding="utf-8").read()
    try:
        import yaml
        return yaml.safe_load(texte)
    except ImportError:
        pass

    data = {"mois": [], "point_mort": {}}
    m = re.search(r"^objectif_ca_mensuel:\s*([\d.]+)", texte, re.M)
    data["objectif_ca_mensuel"] = float(m.group(1)) if m else None
    m = re.search(r"^devise:\s*(\S+)", texte, re.M)
    data["devise"] = m.group(1) if m else "EUR"
    bloc_pm = re.search(r"^point_mort:\n((?:[ \t]+.*\n?)*)", texte, re.M)
    if bloc_pm:
        for cle in ("prudente", "realiste", "haute"):
            m = re.search(rf"\b{cle}:\s*([\d.]+)", bloc_pm.group(1))
            if m:
                data["point_mort"][cle] = float(m.group(1))
    # entrées mensuelles : chaque "- mois:" ouvre un bloc indenté
    for bloc in re.split(r"\n(?=\s*- mois:)", texte):
        m = re.search(r"-\s*mois:\s*\"?(\d{4}-\d{2})\"?", bloc)
        if not m:
            continue
        entree = {"mois": m.group(1)}
        for cle in ("ca_hebergement", "occupation_pct", "adr", "revpar",
                    "nuits_louees", "nuits_disponibles", "vs_objectif_pct"):
            mm = re.search(rf"^\s+{cle}:\s*(-?[\d.]+)", bloc, re.M)
            entree[cle] = float(mm.group(1)) if mm else None
        data["mois"].append(entree)
    return data


# ---------------------------------------------------------------------------
# Primitives SVG
# ---------------------------------------------------------------------------

def _fmt(v):
    if abs(v) >= 100:
        return f"{v:,.0f}".replace(",", " ")  # 2 985 — lisible à la française
    return f"{v:.1f}".rstrip("0").rstrip(".")


def _etiquette_mois(am):
    annee, mois = am.split("-")
    return f"{MOIS_FR[int(mois) - 1]} {annee[2:]}"


class Graphe:
    def __init__(self, titre, v_max, v_min=0.0, unite="€"):
        if v_max <= v_min:
            v_max = v_min + 1
        self.v_min, self.v_max, self.unite = v_min, v_max, unite
        self.elements = [
            f'<svg viewBox="0 0 {LARGEUR} {HAUTEUR}" role="img" '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'style="width:100%;height:auto;font-family:Georgia,serif">',
            f'<text x="{MARGE_G}" y="14" font-size="13" fill="{ACCENT}" '
            f'font-weight="bold">{titre}</text>',
        ]

    def x(self, i, n):
        pas = (LARGEUR - MARGE_G - MARGE_D) / max(n, 1)
        return MARGE_G + pas * (i + 0.5)

    def y(self, v):
        h = HAUTEUR - MARGE_H - MARGE_B
        part = (v - self.v_min) / (self.v_max - self.v_min)
        return HAUTEUR - MARGE_B - part * h

    def grille(self, etiquettes):
        for frac in (0.0, 0.5, 1.0):
            v = self.v_min + frac * (self.v_max - self.v_min)
            y = self.y(v)
            self.elements.append(
                f'<line x1="{MARGE_G}" y1="{y:.1f}" x2="{LARGEUR - MARGE_D}" '
                f'y2="{y:.1f}" stroke="#e2e2e2" stroke-width="1"/>'
                f'<text x="{MARGE_G - 6}" y="{y + 4:.1f}" font-size="10" '
                f'fill="{GRIS}" text-anchor="end">{_fmt(v)}{self.unite}</text>')
        n = len(etiquettes)
        for i, e in enumerate(etiquettes):
            # au-delà de 8 mois, n'étiquette qu'un mois sur deux (le dernier toujours)
            if n > 8 and i % 2 != (n - 1) % 2:
                continue
            self.elements.append(
                f'<text x="{self.x(i, n):.1f}" y="{HAUTEUR - 12}" font-size="10" '
                f'fill="{GRIS}" text-anchor="middle">{e}</text>')

    def ligne_reference(self, v, libelle, couleur=ROUGE, pointilles="6 4"):
        if v is None or not (self.v_min <= v <= self.v_max):
            return
        y = self.y(v)
        self.elements.append(
            f'<line x1="{MARGE_G}" y1="{y:.1f}" x2="{LARGEUR - MARGE_D}" '
            f'y2="{y:.1f}" stroke="{couleur}" stroke-width="1.5" '
            f'stroke-dasharray="{pointilles}"/>'
            f'<text x="{LARGEUR - MARGE_D}" y="{y - 5:.1f}" font-size="10" '
            f'fill="{couleur}" text-anchor="end">{libelle}</text>')

    def barres(self, valeurs, surlignage=None):
        n = len(valeurs)
        pas = (LARGEUR - MARGE_G - MARGE_D) / max(n, 1)
        larg = min(34, pas * 0.6)
        y0 = self.y(self.v_min)
        for i, v in enumerate(valeurs):
            if v is None:
                continue
            x = self.x(i, n) - larg / 2
            y = self.y(v)
            coul = ACCENT if (surlignage is None or i == surlignage) else ACCENT_CLAIR
            self.elements.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{larg:.1f}" '
                f'height="{max(y0 - y, 0):.1f}" fill="{coul}" rx="2"/>'
                f'<text x="{self.x(i, n):.1f}" y="{y - 4:.1f}" font-size="10" '
                f'fill="#444" text-anchor="middle">{_fmt(v)}</text>')

    def courbe(self, valeurs, couleur=ACCENT, etiqueter=True):
        n = len(valeurs)
        points = [(self.x(i, n), self.y(v)) for i, v in enumerate(valeurs)
                  if v is not None]
        if len(points) >= 2:
            chemin = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
            self.elements.append(
                f'<polyline points="{chemin}" fill="none" stroke="{couleur}" '
                f'stroke-width="2"/>')
        for (x, y), v in zip(points, [v for v in valeurs if v is not None]):
            self.elements.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{couleur}"/>')
            if etiqueter:
                self.elements.append(
                    f'<text x="{x:.1f}" y="{y - 7:.1f}" font-size="10" '
                    f'fill="#444" text-anchor="middle">{_fmt(v)}</text>')

    def rendre(self):
        return "\n".join(self.elements + ["</svg>"])


def figure(svg, legende):
    return (f'<figure style="margin:18px 0 6px">\n{svg}\n'
            f'<figcaption style="font-size:11px;color:#777">{legende}'
            f'</figcaption>\n</figure>')


# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="Courbes SVG du rapport de pilotage.")
    p.add_argument("historique", help="historique-pilotage-<logement>.yaml")
    p.add_argument("--mois", help="mois du rapport (AAAA-MM), surligné sur les barres")
    p.add_argument("--sortie", help="fichier de sortie (défaut: stdout)")
    args = p.parse_args()

    data = lire_historique(args.historique)
    entrees = sorted(data.get("mois") or [], key=lambda e: e["mois"])[-12:]
    if not entrees:
        print("Aucune entrée mensuelle dans l'historique.", file=sys.stderr)
        return 2

    libelles = [_etiquette_mois(e["mois"]) for e in entrees]
    objectif = data.get("objectif_ca_mensuel")
    pm = data.get("point_mort") or {}
    surl = next((i for i, e in enumerate(entrees) if e["mois"] == args.mois), None)
    fragments = []

    # 1. CA + objectif
    cas = [e.get("ca_hebergement") for e in entrees]
    maxi = max([v for v in cas if v is not None] + ([objectif] if objectif else []))
    g = Graphe("CA hébergement par mois (€)", maxi * 1.25)
    g.grille(libelles)
    g.ligne_reference(objectif, f"objectif {_fmt(objectif)} €" if objectif else "")
    g.barres(cas, surl)
    fragments.append(figure(g.rendre(),
        "CA hébergement, hors ménage et taxe de séjour — source : carnet de bord."))

    # 2. Occupation
    occs = [e.get("occupation_pct") for e in entrees]
    g = Graphe("Taux d'occupation (%)", 100, unite="%")
    g.grille(libelles)
    g.ligne_reference(50, "hyp. prudente 50 %", couleur=GRIS)
    g.courbe(occs)
    fragments.append(figure(g.rendre(),
        "Nuits louées ÷ nuits disponibles (blocages perso déduits)."))

    # 3. ADR vs point mort
    adrs = [e.get("adr") for e in entrees]
    valeurs_pm = [v for v in (pm.get("realiste"), pm.get("prudente")) if v]
    maxi = max([v for v in adrs if v is not None] + valeurs_pm) * 1.25
    g = Graphe("Prix moyen par nuit vendue (ADR, €)", maxi)
    g.grille(libelles)
    g.ligne_reference(pm.get("prudente"), f"point mort prudent {_fmt(pm.get('prudente'))} €"
                      if pm.get("prudente") else "", couleur=ROUGE)
    g.ligne_reference(pm.get("realiste"), f"point mort réaliste {_fmt(pm.get('realiste'))} €"
                      if pm.get("realiste") else "", couleur="#c98a3d")
    g.courbe(adrs)
    fragments.append(figure(g.rendre(),
        "Sous la ligne « point mort », une nuit vendue coûte plus qu'elle ne rapporte."))

    # 4. Cumul année civile vs objectif
    annee = (args.mois or entrees[-1]["mois"])[:4]
    annee_entrees = [e for e in entrees if e["mois"].startswith(annee)]
    if objectif and annee_entrees:
        cumul, cumuls, cibles = 0.0, [], []
        for i, e in enumerate(annee_entrees, start=1):
            cumul += e.get("ca_hebergement") or 0.0
            cumuls.append(cumul)
            cibles.append(objectif * i)
        g = Graphe(f"Cumul {annee} vs objectif (€) — sur les mois suivis",
                   max(cumuls[-1], cibles[-1]) * 1.2)
        g.grille([_etiquette_mois(e["mois"]) for e in annee_entrees])
        g.courbe(cibles, couleur=GRIS, etiqueter=False)
        g.courbe(cumuls)
        fragments.append(figure(g.rendre(),
            f"Trait vert : CA cumulé réalisé. Trait gris : objectif cumulé "
            f"({_fmt(objectif)} €/mois × mois suivis en {annee})."))

    sortie = "\n".join(fragments)
    if args.sortie:
        with open(args.sortie, "w", encoding="utf-8") as f:
            f.write(sortie)
        print(f"{len(fragments)} graphique(s) écrits dans {args.sortie}", file=sys.stderr)
    else:
        print(sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
