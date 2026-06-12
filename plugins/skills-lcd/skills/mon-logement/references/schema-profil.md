# Schéma du profil logement (`mon-logement-<nom>.md`) — version 2

Référence du format de la fiche d'identité d'un logement LCD. Ce document est le
**contrat de lecture** partagé par les 5 skills du pack (mon-logement, pricing-saisonnier,
fiches-voyageurs, reponses-voyageurs-avis, pilotage-dashboard). Le skill mon-logement
est le seul à ÉCRIRE ce fichier ; les autres ne font que le LIRE.

## Sommaire
1. [Principes du format](#1-principes-du-format)
2. [Nom et emplacement du fichier](#2-nom-et-emplacement-du-fichier)
3. [Frontmatter YAML : toutes les clés](#3-frontmatter-yaml--toutes-les-clés)
4. [Sections markdown (qualitatif)](#4-sections-markdown-qualitatif)
5. [Convention « donnée manquante »](#5-convention--donnée-manquante-)
6. [Comment lire le profil depuis un autre skill](#6-comment-lire-le-profil-depuis-un-autre-skill)
7. [Mapping champs PDF ↔ clés YAML](#7-mapping-champs-pdf--clés-yaml)
8. [Migration d'un profil v1 (prose)](#8-migration-dun-profil-v1-prose)

---

## 1. Principes du format

- **Frontmatter YAML** (entre les deux lignes `---` en tête de fichier) : TOUTES les
  données factuelles et chiffrées. C'est la partie lue par les machines — exactitude
  des clés et des types obligatoire.
- **Corps markdown** : le qualitatif qui respire (univers de marque, recommandations
  locales racontées, notes libres). Les skills qui rédigent du texte (fiches-voyageurs,
  reponses-voyageurs-avis) s'en nourrissent pour le ton.
- Pourquoi cette séparation : un prix ou un horaire mal extrait d'une prose casse les
  calculs de pricing ou une fiche voyageur ; à l'inverse, un ton de marque enfermé dans
  des champs rigides devient plat. Chaque type de donnée vit dans le format qui le sert.

## 2. Nom et emplacement du fichier

- Nom : `mon-logement-<slug>.md` où `<slug>` = nom de l'annonce en minuscules,
  sans accents, espaces et apostrophes remplacés par des tirets.
  Ex. « La Canopée du Hérisson » → `mon-logement-la-canopee-du-herisson.md`.
- Emplacement : la racine du dossier de travail de l'hôte (le dossier que Claude voit).
- Multi-logements : un fichier par logement.

## 3. Frontmatter YAML : toutes les clés

Modèle complet (voir aussi le gabarit prêt à remplir : `assets/modele-profil.md`).
Tous les montants sont en euros, sans symbole. Les listes vides s'écrivent `[]`.

```yaml
---
type_fiche: mon-logement          # marqueur fixe — permet aux skills d'identifier le fichier
version_schema: 2                 # version de ce schéma
date_mise_a_jour: "2026-06-11"    # AAAA-MM-JJ, mise à jour à chaque modification

logement:
  nom: "La Canopée du Hérisson"   # nom exact de l'annonce
  type: "cabane spa perchée"      # appartement, maison, chalet, cabane…
  typologie: "insolite expérientiel"  # exactement l'une de : classique |
                                      # atypique immersif | insolite expérientiel
  theme: "nature / cocon"
  commune: "Menétrux-en-Joux"
  departement: "Jura (39)"
  zone: "montagne / lacs — proche Cascades du Hérisson et Lac de Chalain"

capacite:
  voyageurs: 2                    # entier
  chambres: 1                     # entier
  lits: "1 lit queen"             # texte libre (nombre + tailles)
  salles_de_bain: 1               # entier
  surface_m2: 35                  # entier ou décimal
  exterieur: "terrasse 15 m²"     # texte libre

equipements:
  differenciants: ["jacuzzi privatif sur terrasse", "poêle à bois"]  # liste de textes
  confort: ["parking privé", "kitchenette équipée"]
  absents_assumes: ["pas de TV (déconnexion assumée)"]   # manques volontaires

chiffres:
  prix_moyen_nuit: 180            # nombre (€)
  prix_min_nuit: 150
  prix_max_nuit: 240
  frais_menage: 60                # facturés au voyageur, par séjour
  taux_occupation_pct: 62         # nombre entre 0 et 100
  charges_fixes_annuelles: 4800
  charges_variables_nuit: 18      # par nuit louée
  mensualite_credit: 850          # 0 si pas de crédit
  taxe_sejour_pers_nuit: 0.90     # € par personne et par nuit
  objectif: "2 900 € de CA/mois en moyenne annuelle"   # texte libre

plateformes:
  principale: "Airbnb"
  lien_annonce: "https://…"       # URL de l'annonce principale
  autres: ["réservations en direct via Instagram"]

extras:                           # options payantes proposées aux voyageurs
  - nom: "panier petit-déjeuner"
    prix: 25                      # nombre (€)
  - nom: "early check-in 14h"
    prix: 20

calendrier:
  blocages_perso: ["1re semaine d'août (usage familial)"]  # liste de textes

sejour:
  checkin_debut: "16:00"          # format HH:MM
  checkin_fin: "20:00"            # "" si pas de limite
  checkout: "11:00"
  acces: "autonome — boîte à clés, code 1939"
  wifi_nom: "Canopee_Guest"       # NOM du réseau seulement, JAMAIS le mot de passe
  regles: ["non fumeur (terrasse ok)", "pas d'animaux"]
  consignes_depart: ["vaisselle faite", "poubelles au local"]

contacts:                         # prestataires de l'hôte (privé, jamais publié)
  - role: "ménage"
    nom: "Sandrine"
    telephone: "06 xx xx xx 01"
  - role: "dépannage spa"
    nom: "Jura Spa Services"
    telephone: "à compléter"

marche:
  concurrents:                    # 3 à 5, même typologie de préférence
    - nom: "Bulle des Lacs"
      commune: "Doucier"
      capacite: "2 pers, spa"
      prix_indicatif: 195         # nombre (€) ou "à compléter"
  saison_haute: ["juillet-août", "vacances scolaires"]
  saison_basse: ["novembre", "mars hors vacances"]
  evenements: ["Transjurassienne (février)", "saison des cascades (mai-sept)"]

ton:
  registre: "tutoiement"          # tutoiement | vouvoiement
  style: "chaleureux, complice, pointe d'humour léger"
  trois_mots: ["déconnexion", "cocon", "nature"]
  couleurs: "vert sapin profond + bois clair/crème"
---
```

Notes de typage :
- `typologie` et `registre` sont des énumérations : toujours l'une des valeurs listées.
- Les clés sont **toujours présentes**, même sans donnée (cf. §5) — un lecteur ne doit
  jamais avoir à tester l'existence d'une clé, seulement la validité de sa valeur.
- Ne jamais renommer, déplacer ou supprimer une clé : les 4 autres skills s'y réfèrent.
  Pour enrichir le schéma, AJOUTER des clés et incrémenter `version_schema`.

## 4. Sections markdown (qualitatif)

Après le frontmatter, dans cet ordre :

```markdown
# Mon logement — <nom de l'annonce>
_Fiche générée par le skill mon-logement le <date>. Les autres skills LCD lisent ce fichier._

## Ton & univers de marque
(2-6 phrases qui donnent la voix : comment l'hôte parle, ce que le lieu promet,
ce qu'on évite. C'est ici que les skills rédactionnels viennent chercher l'âme du lieu.)

## Recommandations locales
(Liste à puces : nom — pourquoi on l'aime. Adresses, activités, commerces.)

## Notes libres
(Tout ce que l'hôte a confié et qui n'entre pas dans les cases : anecdotes,
particularités, ce que les voyageurs adorent. « Rien à signaler » si vide.)
```

## 5. Convention « donnée manquante »

- Champ texte sans donnée → la chaîne exacte `"à compléter"`.
- Champ numérique sans donnée → aussi `"à compléter"` (en chaîne). **Tout lecteur doit
  vérifier qu'une valeur est bien un nombre avant de calculer** ; `"à compléter"` ou
  `null` = donnée manquante, à demander à l'hôte ou à ignorer proprement.
- Liste sans donnée → `[]`.
- On n'invente JAMAIS une valeur pour remplir une case : une donnée manquante affichée
  honnêtement vaut mieux qu'un chiffre faux qui contaminera pricing et dashboard.

## 6. Comment lire le profil depuis un autre skill

1. Chercher les fichiers `mon-logement-*.md` dans le dossier de travail. Plusieurs
   fichiers = plusieurs logements : demander à l'hôte lequel utiliser.
2. Vérifier `type_fiche: mon-logement` dans le frontmatter (évite les faux positifs).
3. Parser le frontmatter (tout ce qui est entre les deux premières lignes `---`) avec
   un parseur YAML — en Python : `yaml.safe_load`. Ne pas extraire les valeurs à la
   main par recherche de texte.
4. `version_schema: 2` attendu. Si absent ou fichier sans frontmatter → profil v1 :
   proposer à l'hôte de lancer le skill **mon-logement** pour migrer la fiche (lecture
   best-effort possible en attendant, mais le signaler).
5. Traiter `"à compléter"` / `null` / `[]` comme « donnée manquante » (cf. §5).

## 7. Mapping champs PDF ↔ clés YAML

Le formulaire `assets/formulaire-mon-logement.pdf` utilise des noms de champs AcroForm
mappés 1:1 sur le schéma : **`__` (double underscore) sépare les niveaux YAML**.
Ex. `logement__nom` → `logement.nom` ; `chiffres__prix_moyen_nuit` → `chiffres.prix_moyen_nuit`.

Cas particuliers (le reste du mapping est mécanique) :

| Champ(s) PDF | Clé YAML | Transformation |
|---|---|---|
| `equipements__differenciants`, `equipements__confort`, `equipements__absents_assumes` | listes correspondantes | découper sur virgules / retours à la ligne |
| `extras__1__nom` + `extras__1__prix` … `extras__4__…` | `extras` (liste d'objets) | une entrée par paire non vide ; prix → nombre |
| `contacts__1__role` / `__nom` / `__telephone` … `__3__…` | `contacts` (liste d'objets) | une entrée par trio non vide |
| `marche__concurrents` (zone multiligne) | `marche.concurrents` | une ligne = un concurrent, format « nom — commune — capacité — prix » |
| `marche__evenements`, `marche__saison_haute`, `marche__saison_basse` | listes | découper sur virgules / lignes |
| `calendrier__blocages_perso`, `sejour__regles`, `sejour__consignes_depart` | listes | découper sur virgules / lignes |
| `logement__typologie` (boutons radio) | `logement.typologie` | valeurs : `classique`, `atypique immersif`, `insolite expérientiel` |
| `ton__registre` (boutons radio) | `ton.registre` | valeurs : `tutoiement`, `vouvoiement` |
| `ton__trois_mots` | `ton.trois_mots` | découper sur virgules (liste) |
| `recos_locales` | section markdown **Recommandations locales** | une ligne = une puce |
| `notes_libres` | section markdown **Notes libres** | recopier tel quel |
| `ton__style`, `ton__couleurs` | `ton.style` / `ton.couleurs` + nourrissent la section **Ton & univers de marque** | — |

Champs numériques : nettoyer ` €`, `%`, espaces ; virgule décimale → point
(le script `scripts/lire_formulaire.py` signale déjà les valeurs non numériques).

## 8. Migration d'un profil v1 (prose)

Un profil v1 est un `mon-logement-*.md` **sans frontmatter YAML** (sections markdown
à puces : Identité, Capacité & équipements, Chiffres, Marché local, Ton & identité,
Infos pratiques).

Démarche :
1. Lire le fichier v1 et reporter chaque donnée vers la clé v2 correspondante —
   les intitulés v1 se devinent sans ambiguïté (ex. « Prix moyen / nuit actuel :
   180 € (fourchette : 150–240 €) » → `prix_moyen_nuit: 180`, `prix_min_nuit: 150`,
   `prix_max_nuit: 240`).
2. Les champs v2 sans équivalent v1 (lien d'annonce, plateformes, taxe de séjour,
   extras, contacts, blocages calendrier) → seules questions à poser à l'hôte.
3. Faire valider le résumé, puis réécrire le fichier au format v2 **au même
   emplacement** (proposer de garder une copie `*.ancien.md` si l'hôte y tient).
