# Gabarits & système de thème

Référence de personnalisation des gabarits d'`assets/`. À lire avant de produire le kit.

## Sommaire
1. [Le contrat : structure fixe, thème variable](#1-le-contrat)
2. [Les variables de thème](#2-les-variables-de-thème)
3. [Trois ambiances prêtes à l'emploi](#3-trois-ambiances)
4. [Dériver la palette du profil](#4-dériver-la-palette-du-profil)
5. [Variables de contenu par gabarit](#5-variables-de-contenu-par-gabarit)
6. [Garde-fous design](#6-garde-fous-design)

---

## 1. Le contrat : structure fixe, thème variable {#1-le-contrat}

Chaque gabarit d'`assets/` est un HTML A4 print-ready **finalisé** : mise en page,
hiérarchie, espacements et composants ont été conçus et testés pour tenir sur leurs
pages et rester élégants quel que soit le logement. C'est la garantie de qualité
constante du produit.

Ce que tu personnalises — et RIEN d'autre :
1. **Le bloc `:root` THÈME** (premier bloc du `<style>`, clairement délimité) :
   couleurs et polices.
2. **Les `{{variables}}`** de contenu.
3. **Les blocs marqués `↻`** (commentaires HTML) : à dupliquer/supprimer selon le
   nombre d'items, en copiant la structure à l'identique.
4. Les blocs marqués OPTIONNEL : à supprimer entièrement s'ils ne s'appliquent pas.

Pourquoi cette rigueur : un hôte non-tech ne peut pas rattraper une mise en page
cassée. Si une fiche déborde, on raccourcit le contenu ou on rééquilibre les blocs
répétables — on ne touche jamais aux styles de structure.

Avant livraison, supprimer du HTML final les commentaires de gabarit (`↻`, FALLBACK,
en-tête du fichier) : l'hôte reçoit un document propre.

## 2. Les variables de thème {#2-les-variables-de-thème}

Le bloc `:root` est identique dans les 5 gabarits — applique la même palette partout,
c'est ce qui fait « collection » plutôt que fiches dépareillées.

| Variable | Rôle | Contrainte |
|---|---|---|
| `--primaire` | titres, valeurs fortes, bandeaux | foncée : contraste AAA sur `--fond` |
| `--accent` | filets, puces, surtitres, pastilles distance | moyenne, chaude de préférence |
| `--fond` | fond de page | très claire (presque blanc) : économie d'encre, lisibilité |
| `--carte` | fond des encadrés | plus claire ou plus blanche que `--fond` |
| `--encre` | texte courant | quasi-noir, jamais noir pur (#2x2x2x) |
| `--encre-douce` | texte secondaire + version EN | grise teintée de la palette |
| `--filet` | bordures fines | très claire, teintée de la palette |
| `--police-titre` | titres | pile de polices SYSTÈME (pas de webfont : impression hors ligne) |
| `--police-texte` | texte courant | idem, lisible en 11pt |
| `--rayon` | arrondi des cartes | 0 à 6px (au-delà : effet appli mobile) |

## 3. Trois ambiances prêtes à l'emploi {#3-trois-ambiances}

Points de départ éprouvés — choisis la plus proche de l'univers du profil, puis
ajuste `--primaire`/`--accent` vers les couleurs réelles du logement.

**Forêt** — nature, cocon, chaleureux (cabanes, chalets, gîtes ruraux) :
```css
--primaire:#2F4A3C; --accent:#A8763E; --fond:#FAF6EF; --carte:#FFFFFF;
--encre:#2C2A26; --encre-douce:#857D70; --filet:#E2D9C8;
--police-titre:'Palatino Linotype',Palatino,'Book Antiqua',Georgia,serif;
--police-texte:'Segoe UI','Helvetica Neue',Arial,sans-serif; --rayon:5px;
```

**Lin** — épuré, moderne, lumineux (appartements urbains, studios design) :
```css
--primaire:#23303A; --accent:#B5765A; --fond:#FFFFFF; --carte:#F6F4F1;
--encre:#272A2D; --encre-douce:#8A8480; --filet:#E6E2DC;
--police-titre:'Segoe UI Semibold','Helvetica Neue',Arial,sans-serif;
--police-texte:'Segoe UI','Helvetica Neue',Arial,sans-serif; --rayon:3px;
```

**Encre** — élégant, feutré, sombre (suites, love rooms, maisons de caractère) :
```css
--primaire:#3A2430; --accent:#9C7A45; --fond:#FBF8F3; --carte:#F4EFE7;
--encre:#2B2326; --encre-douce:#8C7F76; --filet:#E3DACB;
--police-titre:'Palatino Linotype',Palatino,Georgia,serif;
--police-texte:'Segoe UI','Helvetica Neue',Arial,sans-serif; --rayon:4px;
```

« Sombre » s'exprime par des teintes profondes de `--primaire`/`--accent` sur fond
ivoire — jamais par un fond de page foncé : à l'impression, un A4 sombre vide la
cartouche, gondole le papier et se photocopie mal.

Exemple de dérivation — love room « bordeaux et crème » sur la base Encre :
`--primaire:#5C1F2C` (bordeaux profond), `--accent:#B08A4F` (laiton),
`--fond:#FBF5EF`, `--filet:#EADDD2`, `--encre-douce:#94807A`.

## 4. Dériver la palette du profil {#4-dériver-la-palette-du-profil}

Source : `ton.couleurs` + `logement.theme` + section « Ton & univers de marque ».

1. La couleur dominante citée par l'hôte → `--primaire`, assombrie s'il le faut
   pour rester très lisible sur fond clair (un « vert d'eau » devient un vert
   profond de la même famille pour les titres).
2. La couleur secondaire (bois, doré, terracotta…) → `--accent`.
3. `--fond`, `--carte`, `--filet`, `--encre-douce` : des déclinaisons très claires
   ou grisées de la même famille — jamais des couleurs nouvelles.
4. Polices : serif classique = chaleureux/élégant/authentique ; sans-serif =
   épuré/moderne/urbain. Le `ton.style` du profil tranche.
5. Annonce la palette à l'hôte en une phrase (« vert sapin profond pour les titres,
   ocre bois pour les détails, fond crème ») — il valide ou ajuste, c'est SA marque.

## 5. Variables de contenu par gabarit {#5-variables-de-contenu-par-gabarit}

Communes : `{{nom_logement}}`, `{{contact_hote}}` (prénom + téléphone, ou prénom +
« via la messagerie Airbnb » si l'hôte ne diffuse pas son numéro — demander),
`{{annee}}`.

**gabarit-guide-accueil.html** (2 pages exactement)
- `{{baseline}}` : devise courte dans le ton du profil
- `{{mot_bienvenue_fr}}` / `_en` : 3-4 phrases personnalisées (l'âme du lieu)
- `{{checkin_debut}}` `{{checkin_fin}}` `{{checkout}}` : depuis `sejour.*`
- `{{acces_resume_fr}}` / `_en` : l'accès SANS code sensible si le guide circule
- ↻ « maison en bref » : 4-6 × `{{equipement}}` + consigne d'une ligne FR/EN
- ↻ règles : max 6 × `{{regle_fr}}`/`_en`, formulées positivement
- ↻ « bon à savoir » : 2-4 blocs `{{info_titre}}`/`{{info_fr}}`/`{{info_en}}`
  (toujours un bloc WiFi qui renvoie à la fiche dédiée — jamais le mot de passe ici)
- `{{mot_fin_fr}}` / `_en` : au revoir + invitation douce à laisser un avis

**gabarit-fiche-wifi.html** (1 page)
- `{{wifi_ssid}}` (profil : `sejour.wifi_nom`), `{{wifi_motdepasse}}` (demandé à
  l'hôte — JAMAIS dans le profil), image `qr-wifi.png` à côté du HTML

**gabarit-checklist-sortie.html** (1 page)
- `{{checkout}}`, `{{phrase_intro_fr}}`/`_en` (complice), ↻ 6-8 items depuis
  `sejour.consignes_depart` (FR positif + EN court), `{{phrase_merci_fr}}`/`_en`

**gabarit-fiche-equipement.html** (1 page PAR équipement)
- `{{nom_equipement}}`, `{{phrase_equipement_fr}}`/`_en` (une phrase d'envie),
  ↻ 2-4 `<li>` par bloc Avant/Pendant/Après, bloc sécurité OPTIONNEL

**gabarit-livret-local.html** (2-4 pages)
- voir `references/livret-local.md` pour le contenu ; pagination manuelle :
  ~2 recos par page avec des descriptions de 2-3 phrases FR + EN (3 si courtes),
  la page 1 perd de la place dans l'en-tête. `break-inside:avoid` protège les
  cartes mais c'est TOI qui répartis les pages — et `--pages-attendues` qui valide

## 6. Garde-fous design {#6-garde-fous-design}

- Une fiche = sa pagination prévue (guide 2 pages, WiFi/sortie/équipement 1 page).
  Les gabarits sont conçus pour qu'un débordement crée une page de plus au lieu de
  rogner silencieusement : la vérification `html_to_pdf.py --pages-attendues N`
  est donc OBLIGATOIRE, pas optionnelle — d'autant que les polices de substitution
  varient d'une machine à l'autre (un texte qui tient ici peut déborder ailleurs).
  S'il y a débordement : raccourcir le contenu (les lignes EN comptent !) ou
  rééquilibrer les blocs répétables, jamais les styles, puis reconvertir.
- Pas d'emojis dans les fiches : les pictos du design (puces, filets, pastilles)
  sont déjà dans les gabarits. Exception tolérée : UN emoji signature si l'hôte le
  demande (mascotte du lieu) dans un texte de bienvenue.
- Pas de dégradés, pas d'ombres portées à l'impression, pas de violet « IA »,
  pas de couleurs néon.
- Le texte EN reste discret (italique, `--encre-douce`) mais COMPLET sur
  l'essentiel : un anglophone doit pouvoir utiliser la fiche sans le FR.
- Corps de texte ≥ 10pt partout (la classe `.en` à 9.5pt est le strict minimum,
  réservé aux traductions).
- Les couleurs de fond ne sortent à l'impression que si « graphiques
  d'arrière-plan » est coché — c'est dans le LISEZMOI, et c'est pourquoi les fonds
  sont presque blancs : la fiche reste belle même imprimée sans.
