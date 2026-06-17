#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère le formulaire PDF « Mon logement » (assets/formulaire-mon-logement.pdf).

Formulaire AcroForm que l'hôte remplit hors-ligne (Adobe Reader, Aperçu,
navigateur) puis dépose dans son dossier Cowork. Les noms de champs sont
mappés 1:1 sur le schéma YAML du profil — voir references/schema-profil.md
(convention : « __ » sépare les niveaux, ex. logement__nom → logement.nom).

Usage :
    python3 scripts/build_pdf_formulaire.py [chemin/de/sortie.pdf]

Dépendance : reportlab (pip install --user reportlab)
"""

import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ---------------------------------------------------------------------------
# Charte : vert sapin / crème (univers LCD atypique, sobre et chaleureux)
# ---------------------------------------------------------------------------
SAPIN = HexColor("#1F4A38")        # vert sapin profond — titres, bordures
SAPIN_CLAIR = HexColor("#3D6B54")  # libellés
CREME = HexColor("#FAF5EC")        # fond de page
BLANC_CASSE = HexColor("#FFFEFA")  # fond des champs
ENCRE = HexColor("#26312B")        # texte saisi
GRIS_DOUX = HexColor("#8A937F")    # textes d'aide

PAGE_W, PAGE_H = A4
MARGE = 42
LARGEUR_UTILE = PAGE_W - 2 * MARGE


class Formulaire:
    """Petit moteur de mise en page à curseur vertical."""

    def __init__(self, chemin):
        self.c = canvas.Canvas(str(chemin), pagesize=A4)
        self.c.setTitle("Mon logement — formulaire de profil LCD")
        self.c.setAuthor("Pack skills LCD")
        self.page_num = 0
        self.y = 0
        self._nouvelle_page(premiere=True)

    # -- structure de page ---------------------------------------------------
    def _fond(self):
        self.c.setFillColor(CREME)
        self.c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    def _pied(self):
        self.c.setFont("Helvetica", 8)
        self.c.setFillColor(GRIS_DOUX)
        self.c.drawCentredString(
            PAGE_W / 2, 24,
            f"Mon logement · formulaire de profil · page {self.page_num}")
        self.c.setStrokeColor(SAPIN)
        self.c.setLineWidth(2)
        self.c.line(MARGE, PAGE_H - 30, PAGE_W - MARGE, PAGE_H - 30)

    def _nouvelle_page(self, premiere=False):
        if not premiere:
            self._pied()
            self.c.showPage()
        self.page_num += 1
        self._fond()
        self.y = PAGE_H - 52
        if not premiere:
            self.c.setFont("Helvetica-Oblique", 8.5)
            self.c.setFillColor(GRIS_DOUX)
            self.c.drawString(MARGE, self.y, "Mon logement — suite")
            self.y -= 18

    def _assurer_place(self, hauteur):
        if self.y - hauteur < 60:
            self._nouvelle_page()

    # -- éléments graphiques ---------------------------------------------------
    def en_tete(self):
        self.c.setFillColor(SAPIN)
        self.c.roundRect(MARGE, self.y - 64, LARGEUR_UTILE, 64, 8, stroke=0, fill=1)
        self.c.setFillColor(CREME)
        self.c.setFont("Helvetica-Bold", 21)
        self.c.drawString(MARGE + 18, self.y - 30, "Mon logement")
        self.c.setFont("Helvetica", 10.5)
        self.c.drawString(MARGE + 18, self.y - 48,
                          "La fiche d'identité de votre location — remplissez ce que vous savez, "
                          "laissez vide le reste.")
        self.y -= 78
        self.c.setFillColor(SAPIN_CLAIR)
        self.c.setFont("Helvetica-Oblique", 9)
        self.c.drawString(
            MARGE, self.y,
            "Une fois rempli, enregistrez ce PDF et déposez-le dans votre dossier de travail : "
            "votre assistant fera le reste.")
        self.y -= 22

    def section(self, titre, sous_titre=None):
        h = 24 + (12 if sous_titre else 0)
        self._assurer_place(h + 30)
        self.y -= 6
        self.c.setFillColor(SAPIN)
        self.c.roundRect(MARGE, self.y - 20, LARGEUR_UTILE, 22, 5, stroke=0, fill=1)
        self.c.setFillColor(CREME)
        self.c.setFont("Helvetica-Bold", 11.5)
        self.c.drawString(MARGE + 10, self.y - 14, titre)
        self.y -= 28
        if sous_titre:
            self.c.setFillColor(GRIS_DOUX)
            self.c.setFont("Helvetica-Oblique", 8.5)
            self.c.drawString(MARGE + 2, self.y, sous_titre)
            self.y -= 14

    # -- champs ---------------------------------------------------------------
    def _libelle(self, texte, x, y):
        self.c.setFillColor(SAPIN_CLAIR)
        self.c.setFont("Helvetica-Bold", 9)
        self.c.drawString(x, y, texte)

    def _champ_texte(self, nom, x, y, largeur, hauteur, info, multiligne=False):
        self.c.acroForm.textfield(
            name=nom, tooltip=info, x=x, y=y, width=largeur, height=hauteur,
            fontName="Helvetica", fontSize=9.5,
            borderColor=SAPIN, fillColor=BLANC_CASSE, textColor=ENCRE,
            borderWidth=0.8, fieldFlags="multiline" if multiligne else "")

    def ligne(self, champs):
        """champs : liste de (libellé, nom_de_champ, proportion, info)."""
        self._assurer_place(34)
        total = sum(p for _, _, p, _ in champs)
        x = MARGE
        for libelle, nom, prop, info in champs:
            largeur = LARGEUR_UTILE * prop / total - (8 if len(champs) > 1 else 0)
            self._libelle(libelle, x, self.y)
            self._champ_texte(nom, x, self.y - 18, largeur, 16, info)
            x += LARGEUR_UTILE * prop / total
        self.y -= 40

    def zone(self, libelle, nom, info, hauteur=46):
        """Champ multiligne pleine largeur."""
        self._assurer_place(hauteur + 30)
        self._libelle(libelle, MARGE, self.y)
        if info:
            self.c.setFillColor(GRIS_DOUX)
            self.c.setFont("Helvetica-Oblique", 7.5)
            self.c.drawString(MARGE + 2, self.y - 10, info)
        self._champ_texte(nom, MARGE, self.y - 14 - hauteur, LARGEUR_UTILE,
                          hauteur, info, multiligne=True)
        self.y -= hauteur + 36

    def radios(self, libelle, nom, options, info=""):
        """options : liste de (valeur, étiquette)."""
        self._assurer_place(40)
        self._libelle(libelle, MARGE, self.y)
        x = MARGE + 4
        y = self.y - 26
        for valeur, etiquette in options:
            self.c.acroForm.radio(
                name=nom, tooltip=f"{info} — {etiquette}".strip(" —"),
                value=valeur, selected=False, x=x, y=y, size=13,
                buttonStyle="circle", borderColor=SAPIN,
                fillColor=BLANC_CASSE, textColor=SAPIN, borderWidth=1)
            self.c.setFillColor(ENCRE)
            self.c.setFont("Helvetica", 9)
            self.c.drawString(x + 17, y + 3, etiquette)
            x += 17 + self.c.stringWidth(etiquette, "Helvetica", 9) + 26
        self.y -= 48

    def terminer(self):
        self._pied()
        self.c.save()


def construire(chemin_sortie):
    f = Formulaire(chemin_sortie)
    f.en_tete()

    # ---- 1. Identité --------------------------------------------------------
    f.section("1. Identité du logement")
    f.ligne([("Nom de l'annonce", "logement__nom", 1.4,
              "Le nom exact tel qu'il apparaît sur votre annonce"),
             ("Type de bien", "logement__type", 1,
              "Ex. appartement, maison, chalet, cabane, bulle…")])
    f.radios("Famille de logement", "logement__typologie",
             [("classique", "Classique"),
              ("atypique immersif", "Atypique immersif (déco / thème)"),
              ("insolite expérientiel", "Insolite (cabane, bulle, tipi…)")],
             "La catégorie qui décrit le mieux votre bien")
    f.ligne([("Thème / univers", "logement__theme", 1,
              "Ex. nature & cocon, jungle, cinéma, romantique…"),
             ("Commune", "logement__commune", 1, "Commune du logement")])
    f.ligne([("Département", "logement__departement", 1, "Ex. Jura (39)"),
             ("Environnement", "logement__zone", 1.4,
              "Mer, montagne, ville, campagne, lacs… + points d'intérêt proches")])

    # ---- 2. Capacité ---------------------------------------------------------
    f.section("2. Capacité")
    f.ligne([("Voyageurs (max)", "capacite__voyageurs", 1, "Nombre de voyageurs maximum"),
             ("Chambres", "capacite__chambres", 1, "Nombre de chambres"),
             ("Salles de bain", "capacite__salles_de_bain", 1, "Nombre de salles de bain")])
    f.ligne([("Lits (nombre et tailles)", "capacite__lits", 1.4,
              "Ex. 1 lit queen + 1 canapé-lit"),
             ("Surface (m²)", "capacite__surface_m2", 0.5, "Surface intérieure en m²"),
             ("Extérieur", "capacite__exterieur", 1,
              "Ex. terrasse 15 m², jardin, balcon…")])

    # ---- 3. Équipements -------------------------------------------------------
    f.section("3. Équipements", "Séparez par des virgules.")
    f.zone("Équipements « waouh » qui vous différencient", "equipements__differenciants",
           "Ex. jacuzzi privatif, sauna, poêle à bois, baie vitrée vue forêt…", 46)
    f.zone("Équipements de confort", "equipements__confort",
           "Ex. parking privé, WiFi, cuisine équipée, climatisation…", 46)
    f.ligne([("Ce qu'il n'y a PAS (volontairement)", "equipements__absents_assumes", 1,
              "Ex. pas de TV — assumé pour la déconnexion")])

    # ---- 4. Chiffres -----------------------------------------------------------
    f.section("4. Vos chiffres", "Des montants approximatifs suffisent. En euros, chiffres uniquement.")
    f.ligne([("Prix moyen / nuit (€)", "chiffres__prix_moyen_nuit", 1, "Prix moyen pratiqué par nuit"),
             ("Prix le plus bas (€)", "chiffres__prix_min_nuit", 1, "Bas de votre fourchette"),
             ("Prix le plus haut (€)", "chiffres__prix_max_nuit", 1, "Haut de votre fourchette")])
    f.ligne([("Frais de ménage facturés (€)", "chiffres__frais_menage", 1,
              "Montant facturé au voyageur par séjour"),
             ("Taux d'occupation (%)", "chiffres__taux_occupation_pct", 1,
              "Part des nuits louées, si vous la connaissez"),
             ("Taxe de séjour (€/pers/nuit)", "chiffres__taxe_sejour_pers_nuit", 1,
              "Montant par personne et par nuit")])
    f.ligne([("Charges fixes / an (€)", "chiffres__charges_fixes_annuelles", 1,
              "Assurance, abonnements, compta, entretien…"),
             ("Charges variables / nuit louée (€)", "chiffres__charges_variables_nuit", 1,
              "Consommables, énergie, blanchisserie…"),
             ("Mensualité de crédit (€/mois)", "chiffres__mensualite_credit", 1,
              "Laissez vide si pas de crédit")])
    f.ligne([("Votre objectif (revenus ou cash-flow visé)", "chiffres__objectif", 1,
              "Ex. 2 900 € de chiffre d'affaires par mois en moyenne")])

    # ---- 5. Plateformes ----------------------------------------------------------
    f.section("5. Annonce & plateformes")
    f.ligne([("Plateforme principale", "plateformes__principale", 1,
              "Ex. Airbnb, Booking, Abritel…"),
             ("Lien de votre annonce", "plateformes__lien_annonce", 1.6,
              "Copiez-collez l'adresse de l'annonce")])
    f.ligne([("Autres canaux de réservation", "plateformes__autres", 1,
              "Ex. réservations en direct via Instagram, Gîtes de France…")])

    # ---- 6. Extras ------------------------------------------------------------
    f.section("6. Extras & options payantes",
              "Ce que vous proposez (ou aimeriez proposer) en plus du séjour.")
    for i in (1, 2, 3, 4):
        f.ligne([(f"Extra {i} — nom", f"extras__{i}__nom", 2,
                  "Ex. panier petit-déjeuner, arrivée anticipée 14h…"),
                 ("Prix (€)", f"extras__{i}__prix", 0.5, "Prix de l'option")])

    # ---- 7. Calendrier -----------------------------------------------------------
    f.section("7. Vos blocages de calendrier")
    f.zone("Périodes où VOUS utilisez ou bloquez le logement", "calendrier__blocages_perso",
           "Ex. 1re semaine d'août en famille, week-end de Pâques, maintenance spa en novembre…", 54)

    # ---- 8. Le séjour ------------------------------------------------------------
    f.section("8. Le séjour, côté pratique")
    f.ligne([("Arrivée à partir de", "sejour__checkin_debut", 1, "Ex. 16:00"),
             ("Arrivée au plus tard à", "sejour__checkin_fin", 1,
              "Ex. 20:00 — laissez vide si pas de limite"),
             ("Départ avant", "sejour__checkout", 1, "Ex. 11:00")])
    f.zone("Comment les voyageurs entrent-ils ?", "sejour__acces",
           "Boîte à clés (et son code), serrure connectée, remise en main propre… "
           "+ instructions pour trouver l'entrée", 58)
    f.ligne([("Nom du réseau WiFi", "sejour__wifi_nom", 1,
              "Le NOM du réseau uniquement — jamais le mot de passe ici")])
    f.zone("Règles de la maison", "sejour__regles",
           "Ex. non fumeur, pas d'animaux, pas de fête, calme après 22h…", 52)
    f.zone("Consignes de départ", "sejour__consignes_depart",
           "Ce que les voyageurs doivent faire avant de partir : poubelles, vaisselle, linge, "
           "où laisser les clés, fenêtres, chauffage…", 76)

    # ---- 9. Contacts ----------------------------------------------------------------
    f.section("9. Contacts utiles", "Ménage, dépannage, jardinier… Vos numéros restent dans votre dossier privé.")
    for i, exemple in ((1, "Ex. ménage"), (2, "Ex. dépannage spa / plomberie"), (3, "Autre")):
        f.ligne([(f"Contact {i} — rôle", f"contacts__{i}__role", 0.8, exemple),
                 ("Nom", f"contacts__{i}__nom", 1, "Nom de la personne ou de l'entreprise"),
                 ("Téléphone", f"contacts__{i}__telephone", 0.8, "Numéro à appeler")])

    # ---- 10. Marché -----------------------------------------------------------------
    f.section("10. Votre marché local")
    f.zone("3 à 5 logements concurrents que vous connaissez", "marche__concurrents",
           "Un par ligne : nom de l'annonce — commune — capacité — prix approximatif", 104)
    f.zone("Événements locaux qui font monter la demande", "marche__evenements",
           "Festivals, compétitions, marchés de Noël… avec le mois si possible", 52)
    f.ligne([("Haute saison chez vous", "marche__saison_haute", 1,
              "Ex. juillet-août, vacances scolaires, Noël…"),
             ("Périodes creuses", "marche__saison_basse", 1,
              "Ex. novembre, mars hors vacances…")])

    # ---- 11. Ton ------------------------------------------------------------------
    f.section("11. Votre façon de parler aux voyageurs")
    f.radios("Vous dites plutôt…", "ton__registre",
             [("tutoiement", "« tu » (tutoiement)"),
              ("vouvoiement", "« vous » (vouvoiement)")],
             "Le registre utilisé avec vos voyageurs")
    f.ligne([("Votre style en quelques mots", "ton__style", 1.2,
              "Ex. chaleureux et complice, avec une pointe d'humour"),
             ("3 mots de l'expérience", "ton__trois_mots", 0.85,
              "Ex. déconnexion, cocon, nature"),
             ("Couleurs / ambiance", "ton__couleurs", 0.85,
              "Ex. vert sapin, bois clair, crème — utile pour vos documents")])

    # ---- 12. Recos & notes ------------------------------------------------------------
    f.section("12. Vos bonnes adresses & tout le reste")
    f.zone("3 à 5 recommandations locales", "recos_locales",
           "Restaurants, activités, commerces… Une par ligne, avec un mot sur pourquoi vous l'aimez", 104)
    f.zone("Tout ce qui n'a pas trouvé sa place ailleurs", "notes_libres",
           "Anecdotes, particularités, ce que les voyageurs adorent…", 72)

    f.terminer()


if __name__ == "__main__":
    defaut = Path(__file__).resolve().parent.parent / "assets" / "formulaire-mon-logement.pdf"
    sortie = Path(sys.argv[1]) if len(sys.argv) > 1 else defaut
    sortie.parent.mkdir(parents=True, exist_ok=True)
    construire(sortie)
    print(f"Formulaire généré : {sortie}")
