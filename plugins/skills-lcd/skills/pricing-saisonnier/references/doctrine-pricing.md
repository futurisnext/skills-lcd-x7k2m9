# Doctrine pricing LCD — méthode de référence

Sommaire : 1. Typologies et comparables · 2. Point mort · 3. Calibrer le prix de base · 4. Structure de la grille · 5. Spécificités des biens atypiques · 6. Rituel d'ajustement mensuel · 7. Honnêteté.

## 1. Typologies et comparables

Trois typologies de biens LCD :
- **Atypique immersif** : logement classique transformé en expérience (déco, thème, équipements — love room, jungle room, ciné room…).
- **Insolite expérientiel** : hébergement à part entière, souvent extérieur (cabane, bulle, tipi, houseboat…).
- **Classique** : logement meublé standard.

**Règle d'or : comparables de même typologie uniquement, capacité ±2 voyageurs.** Un atypique ou un insolite se compare à d'autres biens expérientiels de la zone élargie — jusqu'à 45-60 min s'il n'y en a pas localement, car la clientèle de l'expérientiel se déplace pour l'expérience. Jamais à un classique « avec jacuzzi gonflable » : la valeur vient de l'expérience, pas de la surface. Pourquoi c'est si important : un hôte qui se calibre sur des classiques sous-évalue un bien expérientiel de 30 à 50 % ; à l'inverse, un classique calibré sur un insolite voisin ne se remplira jamais.

Conséquence pricing : un bien expérientiel se tarife à l'**expérience** (par nuit, proche de l'hôtellerie thématique), un classique se tarife au **marché local** (par m²/capacité).

Si un comparable proposé par l'hôte est hors typologie ou hors capacité : l'écarter en expliquant pourquoi, ou le garder à titre purement indicatif en le signalant comme tel dans le livrable (jamais dans le calcul du positionnement).

## 2. Point mort par nuitée

```
point mort/nuitée = (charges fixes annuelles + 12 × mensualité crédit) ÷ nuits louées estimées
                    + charges variables par nuit louée
```

- **Charges fixes** : assurance PNO, comptabilité, abonnements (channel manager, capteurs…), taxe foncière, part fixe énergie/eau, entretien des équipements (spa, piscine).
- **Charges variables / nuit louée** : consommables, énergie marginale, maintenance, blanchisserie, ménage NON refacturé. (Le ménage refacturé au voyageur est neutre : il n'entre ni dans les charges ni dans le prix de nuitée.)
- **Nuits louées estimées** = 365 × taux d'occupation de l'hypothèse.
- **Toujours 3 hypothèses** (prudente / réaliste / haute). Pourquoi : l'occupation est la variable la plus incertaine du métier ; un point mort calculé sur une seule hypothèse optimiste donne un faux sentiment de sécurité. Le point mort **prudent** est le vrai plancher psychologique. Repères par défaut : prudente = réaliste − 10 à 12 points, haute = réaliste + 8 à 10 points ; la « réaliste » vient du taux observé (rapport pilotage) ou estimé par l'hôte. À ajuster à la zone (une station de ski n'a pas le profil d'une grande ville).
- La **commission plateforme** (~3 % côté hôte Airbnb, plus en modèle commission unique) se déduit du CA, pas du prix affiché : l'intégrer dans l'analyse de marge, pas dans le plancher.
- La **taxe de séjour** est collectée pour la commune : elle ne compte ni dans le CA ni dans le point mort.

Utiliser `scripts/point_mort.py` pour le calcul : même formule, mêmes arrondis, à chaque fois.

## 3. Calibrer le prix de base

Le « prix de base » est celui de la **moyenne saison en semaine**. Trois ancres, dans cet ordre :

1. **Le relevé concurrents** (même typologie, ±2 voyageurs) : positionner le bien dans la fourchette relevée selon ses atouts différenciants réels (équipements, note, vue, expérience). Un bien mieux équipé que la médiane des comparables peut se placer au-dessus ; l'inverse aussi.
2. **Les prix actuels de l'hôte** : s'ils remplissent à un bon taux, ils sont une information de marché en soi. Un écart de plus de ±15 % entre la grille proposée et la pratique actuelle doit être expliqué et, si possible, lissé sur 2-3 mois.
3. **Le point mort prudent** : plancher absolu (cf. § 2).

Ne jamais inverser l'ordre : partir du point mort pour fixer le prix (cost-plus) laisse de l'argent sur la table quand le marché paie plus, et ne sauve pas un bien hors marché.

## 4. Structure de la grille 12 mois

La grille découpe l'année en **périodes datées** (début/fin réels). Niveaux types — des ordres de grandeur de départ, à calibrer sur le relevé concurrents et les données du bien :

| Période | Définition | Niveau indicatif |
|---|---|---|
| Basse saison | semaines creuses hors vacances | base −10 à −20 % |
| Moyenne saison | printemps/automne, demande normale | base |
| Haute saison | saison touristique de la zone | base +15 à +30 % |
| Très haute saison | pics (Noël/Nouvel An en montagne, août en mer, événement majeur) | base +30 à +60 % |
| Week-end | vendredi & samedi soir, toute l'année | +10 à +25 % vs semaine de la période |
| Vacances scolaires | selon zones A/B/C des bassins émetteurs | aligner sur haute saison |
| Ponts & fériés | mini week-ends prolongés | majoration week-end étendue au pont |
| Événements locaux | dates précises, forte tension | +20 à +50 % ponctuel |
| Saint-Valentin & co | pour les biens romantiques : pic majeur | très haute saison |

Règles de construction :
- **Aucun trou ni chevauchement** : toute date de l'année appartient à exactement une période ; les événements sont des surcharges ponctuelles par-dessus.
- **Durées minimum** : 2 nuits en haute saison et sur les week-ends prisés (réduit le poids relatif du ménage et les trous d'une nuit dans le calendrier), 1 nuit en basse saison (remplissage), 3-7 nuits sur les semaines de très haute saison familiale (mer/montagne).
- **Chaque période porte sa justification** en une ligne et, si elle dépend d'un calendrier externe, sa source.
- Limiter le nombre de périodes (8 à 14 sur l'année hors événements) : une grille à 30 lignes est ingérable pour l'hôte.

## 5. Spécificités des biens atypiques et insolites

- La demande est portée par les **occasions** (anniversaires, demandes en mariage, Saint-Valentin, EVJF) : les week-ends pèsent beaucoup plus que pour un classique — l'écart semaine/week-end peut dépasser +25 %, toute l'année.
- L'**ADR élevé compense une occupation plus basse** : viser le revenu (ADR × occupation), pas le remplissage maximal. Brader un insolite remplit le calendrier mais dégrade le positionnement et attire la mauvaise clientèle.
- En basse saison, préférer des **offres packagées** (nuit + extra inclus : petit-déj, late check-out) à des baisses de prix brutales : la valeur perçue reste intacte, le coût réel de l'offre est faible.
- La clientèle vient de loin (1-2 h de route) : la saisonnalité suit les **week-ends et les vacances des bassins émetteurs** plus que la météo locale.

## 6. Rituel d'ajustement mensuel

Chaque début de mois (idéalement après le rapport pilotage-dashboard) :

1. **Relever** occupation et ADR du mois écoulé (rapport pilotage ou export plateforme).
2. **Regarder le remplissage des 8 prochaines semaines** :
   - \> 70 % de rempli à 6 semaines → monter les prix des nuits restantes de 5-10 % ;
   - < 30 % à 3 semaines → offre/promo **ciblée** (dates précises, packagée) plutôt qu'une baisse générale, qui dévalorise le bien et pénalise les résas déjà prises au prix fort.
3. **Re-relever les concurrents** sur les 2-3 mois à venir (2 fenêtres suffisent) : si tout le marché a bougé, ce n'est pas un problème de bien, c'est un mouvement de marché à suivre.
4. **Vérifier les événements** nouvellement annoncés dans la zone.
5. **Ajuster les 2-3 mois à venir uniquement.** Pourquoi : les résas se prennent surtout dans cette fenêtre, et retoucher l'année entière chaque mois rend la stratégie illisible. Chaque delta = prix avant → prix après + motif en une ligne, tracé dans l'historique de la grille.

## 7. Honnêteté

Tous les pourcentages de ce document sont des **ordres de grandeur de départ**, à calibrer sur les données réelles du bien. Les livrables présentent les impacts en fourchettes estimées, sourcent les données externes (calendriers, événements), datent les relevés de prix et signalent les données manquantes. Un chiffre incertain annoncé comme tel vaut mieux qu'un chiffre précis et faux.
