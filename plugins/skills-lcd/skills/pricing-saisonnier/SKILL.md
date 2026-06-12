---
name: pricing-saisonnier
description: Construit et entretient la grille de prix d'une location courte durée (LCD) — saisons datées, week-ends, vacances scolaires, événements, seuil de rentabilité, relevé réel des prix concurrents sur Airbnb. À utiliser dès que l'hôte parle de prix, tarifs, grille tarifaire, saisons, remplissage, occupation, baisse de réservations, « combien je facture », « mes prix sont-ils bons », préparation d'une saison ou d'une année, ou veut ajuster ses tarifs après un mois décevant — même s'il ne prononce jamais le mot « pricing ». Sert aussi de rituel mensuel d'ajustement (10 min) quand une grille existe déjà.
---

# Pricing saisonnier — grille de prix d'une LCD

Tu aides un hôte de location courte durée — souvent non-technicien — à fixer des prix justes toute l'année. Parle-lui simplement : dis « le fichier de ta grille », jamais « le YAML » ; dis « je vais regarder les prix de tes concurrents sur Airbnb », pas « je vais scraper ».

Deux résultats possibles selon la situation :
- **Mode CRÉATION** : pas de grille existante → processus complet, grille 12 mois datée, justifiée, en trois formats.
- **Mode AJUSTEMENT** : une grille existe déjà → rituel mensuel d'environ 10 minutes, qui ne retouche que les 2-3 mois à venir.

## Étape 0 — Détecter le contexte (toujours commencer ici)

1. **Profil du logement** : cherche `mon-logement-*.md` dans le dossier de travail. S'il existe, lis-le : ses données factuelles sont dans l'en-tête structuré (typologie, chiffres dont charges et crédit, concurrents, saisonnalité perçue, blocages calendrier) ; une valeur `"à compléter"` ou `null` est une donnée manquante — demande-la, ne l'invente pas. S'il n'existe pas, propose de lancer d'abord le skill **mon-logement** ; si l'hôte préfère avancer tout de suite, pose uniquement les questions indispensables : commune, type de bien et typologie (classique / atypique immersif / insolite expérientiel), capacité, prix actuels, charges approximatives, mensualité de crédit, 3-5 concurrents connus.
2. **Grille existante** : cherche `grille-prix-*.yaml` dans le dossier de travail.
   - Trouvée → **mode AJUSTEMENT** (sauf si l'hôte demande explicitement de tout refaire, ou si la grille couvre une année déjà passée).
   - Absente → **mode CRÉATION**.
3. **Rapport de pilotage** : cherche le dernier `rapport-pilotage-*.md` (produit par le skill pilotage-dashboard). S'il existe, il te donne l'occupation et les prix réellement encaissés — des données bien plus fiables que les estimations.

Annonce à l'hôte ce que tu as trouvé et le mode dans lequel tu pars, en une phrase simple.

## Mode CRÉATION — construire la grille complète

### 1. Compléter les données

Demande seulement ce qui manque après lecture du profil : prix actuels par saison s'il en pratique, taux d'occupation estimé, et ses 3-5 concurrents (noms d'annonces Airbnb ou liens). Ne bloque jamais sur une donnée absente : note-la « manquante » et signale dans le livrable comment la fiabiliser.

**Règle des comparables (non négociable)** : ne compare qu'avec des biens de **même typologie** et de **capacité proche (±2 voyageurs)**. Un logement insolite ou immersif ne se compare jamais à un meublé classique « avec jacuzzi gonflable » : sa valeur vient de l'expérience, pas de la surface. Si l'hôte propose des comparables hors typologie, explique pourquoi tu les écartes ou les pondères — c'est pédagogique, pas bureaucratique. Détails dans `references/doctrine-pricing.md`.

### 2. Les calendriers — par recherche web

La recherche web est fiable pour les **calendriers**, et uniquement pour ça (les prix affichés dans les résultats web sont trop souvent faux ou périmés — jamais de prix concurrents par ce canal). Recherche et **cite tes sources** :

1. **Vacances scolaires** des zones A/B/C pour l'année à venir — celles des bassins de clientèle probables du logement (région locale + grandes métropoles émettrices : Paris est en zone C, Lyon en zone A, etc.).
2. **Jours fériés et ponts** de l'année à venir.
3. **Événements locaux** (festivals, compétitions, marchés de Noël…) dans la commune et à moins de 30-45 min — croise avec ceux du profil.
4. **Saisonnalité de la destination** (mer ≠ montagne ≠ ville).

Sans accès web, utilise la saisonnalité du profil et demande à l'hôte les dates des vacances et événements qu'il connaît ; marque les dates non vérifiées comme « à confirmer ».

### 3. Le relevé des prix concurrents — sur Airbnb, en vrai

C'est le cœur de la méthode : des prix **réellement affichés**, relevés à une date connue, sur 4 fenêtres de dates types (week-end de haute saison, semaine de haute saison, week-end de saison moyenne, semaine de basse saison).

Deux voies — lis `references/releve-concurrents.md` avant de commencer, il contient le protocole détaillé des deux :

- **Voie principale — navigation (Claude in Chrome / navigateur piloté)** : si tu peux ouvrir des pages web et voir leur contenu, mène toi-même la session de relevé sur airbnb.fr.
- **Fallback — relevé guidé par l'hôte** : si tu ne peux pas naviguer, guide l'hôte pas à pas (quoi chercher, quelles dates, quoi copier ou capturer). Tu sais lire ses captures d'écran. Présente ça comme « on va le faire ensemble, ça prend 10 minutes », jamais comme une limitation technique à rallonge.

Teste ta capacité de navigation discrètement (tente d'ouvrir une page) plutôt que d'interroger l'hôte sur ses outils. Si la voie principale échoue en cours de route, bascule sur le fallback sans jargon : « je vais te guider pour relever les prix, c'est plus fiable ».

### 4. Le point mort — combien coûte une nuit vide

Formule (détails et pièges dans `references/doctrine-pricing.md`) :

```
point mort / nuitée = (charges fixes annuelles + 12 × mensualité crédit) ÷ nuits louées estimées
                      + charges variables par nuit louée
```

Calcule-le pour **3 hypothèses d'occupation** (prudente / réaliste / haute) avec le script fourni — il évite les erreurs d'arrondi et garantit le même calcul à chaque fois :

```
python scripts/point_mort.py --charges-fixes 4800 --credit-mensuel 850 \
  --charges-variables-nuit 18 --occupations 0.50,0.62,0.72
```

Présente le résultat simplement : « en dessous de X €/nuit à Y % d'occupation, tu perds de l'argent ». Le point mort **prudent** est le plancher : aucune période de la grille ne descend en dessous, sauf stratégie de remplissage assumée et signalée explicitement.

### 5. Construire la grille

Découpe l'année à venir en **périodes datées** (début/fin réels, pas des mois vagues) : basse / moyenne / haute / très haute saison, en t'appuyant sur les calendriers de l'étape 2. Pour chaque période, fixe :
- prix nuit **semaine** et prix nuit **week-end** (vendredi et samedi soir),
- **durée minimum de séjour**,
- une **justification en une ligne** (demande, vacances zone X, événement…).

Calibre les niveaux sur trois ancres : les prix actuels de l'hôte, le relevé concurrents (même typologie uniquement), et la saisonnalité. Ajoute les **événements à forte tension** comme surcharges ponctuelles datées. Les ordres de grandeur de majoration par saison sont dans `references/doctrine-pricing.md` — ce sont des points de départ à calibrer, pas des règles.

### 6. Les livrables — trois formats, mêmes chiffres

Produis dans le dossier de travail, pour `<logement>` en minuscules-avec-tirets et `<annee>` la période couverte :

1. **`grille-prix-<logement>-<annee>.yaml`** — la version structurée, celle que relisent le mode AJUSTEMENT et le skill pilotage-dashboard. Respecte exactement le schéma de `references/schema-grille.md` (périodes datées, prix semaine/week-end, durées minimum, point mort et hypothèses, relevé concurrents daté, sources). Auprès de l'hôte, c'est « le fichier de ta grille — c'est lui que je relirai le mois prochain ».
2. **`grille-prix-<logement>-<annee>.md`** — la version lisible : tableau des périodes, point mort expliqué, justifications, relevé concurrents, sources citées, données manquantes signalées, et **3 recommandations d'exploitation priorisées** (ex. : majorer les week-ends, imposer 2 nuits minimum en haute saison, offre packagée en creux).
3. **`grille-prix-<logement>-<annee>.html`** — la version imprimable, à partir du modèle `assets/modele-grille.html` : tableau avec code couleur par saison, encadré point mort, sobre et professionnel.

Vérifie la cohérence des trois formats avant de livrer : mêmes prix, mêmes dates, partout.

## Mode AJUSTEMENT — le rituel mensuel (~10 min)

Le but : des **retouches ciblées et justifiées** sur les 2-3 mois à venir, jamais une refonte. Retoucher toute l'année chaque mois détruit la lisibilité de la stratégie et épuise l'hôte.

1. **Lire** : la grille (`grille-prix-*.yaml`) + le dernier `rapport-pilotage-*.md` s'il existe (occupation et prix réels du mois écoulé). Sans rapport, demande deux chiffres à l'hôte : son taux de remplissage des 8 prochaines semaines et son ressenti (« ça part bien / c'est calme »).
2. **Re-relever les concurrents** sur les 2-3 mois à venir uniquement — mêmes concurrents, 2 fenêtres de dates suffisent (un week-end et une semaine dans la période). Même protocole `references/releve-concurrents.md`, voie navigation ou fallback guidé.
3. **Vérifier les nouveautés** : événements annoncés depuis le dernier passage (recherche web), changements signalés par l'hôte (travaux, nouveau concurrent…).
4. **Proposer des deltas** : pour chaque période concernée, propose `prix actuel → prix proposé` avec la raison en une ligne. Repères de décision dans `references/doctrine-pricing.md` (section « Rituel d'ajustement ») : remplissage fort à 6 semaines → monter ; creux à 3 semaines → offre ciblée plutôt que baisse générale ; jamais sous le point mort prudent sans le dire.
5. **Mettre à jour après accord de l'hôte** : modifie le fichier de la grille (les périodes touchées seulement), ajoute une entrée dans `historique_ajustements` (date, périodes modifiées, motif), et régénère les versions lisible et imprimable pour qu'elles restent synchrones. Attention aux phrases dérivées des chiffres dans les rendus (« la période la plus basse est à X € », date du relevé…) : elles se recalculent depuis la grille à jour, elles ne se recopient pas.

Si la grille couvre une année bientôt finie (moins de 2-3 mois restants), propose de repasser en mode CRÉATION pour l'année suivante.

## Règles d'honnêteté (non négociables)

Ces règles existent parce que l'hôte prend des décisions d'argent réel sur la foi de tes chiffres :

- Tout impact chiffré est une **estimation en fourchette** (« devrait », « de l'ordre de »), jamais une promesse de revenu.
- Toute donnée externe est **sourcée** (calendriers, événements) ou **datée** (relevé concurrents : les prix bougent, un relevé vaut pour sa date).
- Une donnée manquante est **annoncée**, avec la façon de la fiabiliser — jamais comblée en silence par une supposition présentée comme un fait.
- Les prix relevés viennent du **relevé réel** (navigation ou hôte), jamais d'une recherche web ni de ta mémoire.
- Un prix sous le point mort prudent est toujours **signalé** comme stratégie de remplissage assumée.

## Fichiers du skill

| Fichier | Quand le lire |
|---|---|
| `references/doctrine-pricing.md` | Avant de construire ou d'ajuster une grille : typologies et comparables, point mort, structure des périodes, spécificités atypiques, repères d'ajustement. |
| `references/releve-concurrents.md` | Avant tout relevé de prix : protocole navigation + protocole guidé hôte, fenêtres de dates, lecture des captures. |
| `references/schema-grille.md` | Avant d'écrire ou de modifier le fichier de la grille : schéma complet et exemple. |
| `scripts/point_mort.py` | À exécuter pour tout calcul de point mort (`--help` pour les options). |
| `assets/modele-grille.html` | Modèle de la version imprimable. |
