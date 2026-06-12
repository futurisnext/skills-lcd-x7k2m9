# Doctrine pilotage LCD — définitions, conventions, seuils

Le contrat de ce skill : des chiffres exacts, des conventions stables d'un mois sur
l'autre, et une lecture honnête. Un hôte prend des décisions d'argent réel sur la foi
de ce rapport — un KPI calculé différemment chaque mois est pire qu'inutile.

## Sommaire
1. [KPI de référence](#1-kpi-de-référence)
2. [Conventions de calcul (non négociables)](#2-conventions-de-calcul-non-négociables)
3. [Point mort : d'où il vient](#3-point-mort--doù-il-vient)
4. [Nuits disponibles](#4-nuits-disponibles)
5. [Seuils d'alerte](#5-seuils-dalerte)
6. [Tendances, cumul annuel et projections](#6-tendances-cumul-annuel-et-projections)
7. [Structure du rapport](#7-structure-du-rapport)

---

## 1. KPI de référence

| KPI | Formule | Lecture |
|---|---|---|
| CA hébergement | Σ montants nuitées (hors ménage refacturé, hors taxe de séjour) | le revenu « cœur » |
| Taux d'occupation | nuits louées ÷ nuits disponibles | disponibilité réellement vendue |
| ADR | CA hébergement ÷ nuits louées | prix moyen par nuit vendue |
| RevPAR | CA hébergement ÷ nuits disponibles | LE chiffre de synthèse (prix × remplissage) |
| Point mort/nuitée | (charges fixes annuelles + 12 × mensualité) ÷ nuits louées estimées + charges variables/nuit | plancher de prix |
| Part du direct | CA direct ÷ CA total | marge récupérée sur les commissions |

Le RevPAR est le meilleur indicateur de pilotage : il monte si on vend plus cher OU
plus souvent, et démasque les fausses victoires (occupation gonflée par des prix
bradés, ou ADR flatteur avec un calendrier vide). Face à l'hôte, dis « revenu par
nuit disponible » — RevPAR entre parenthèses la première fois.

## 2. Conventions de calcul (non négociables)

Ces conventions sont appliquées par `scripts/parse_resas.py`. Si tu calcules à la
main (fallback), applique exactement les mêmes — sinon les tendances mois à mois
ne veulent plus rien dire.

- **Ventilation à cheval** : une résa qui chevauche deux mois est ventilée au
  prorata des **nuits réellement dormies** dans chaque mois. Une arrivée le 30 avril
  pour 2 nuits met 1 nuit (et la moitié du montant) en avril, 1 nuit en mai.
- **Annulations** : exclues du CA et des nuits louées. Les indemnités d'annulation
  encaissées sont comptées **à part** (ligne « indemnités »), jamais fondues dans le
  CA — sinon l'ADR devient faux.
- **Ménage** : les frais de ménage refacturés au voyageur sortent du CA hébergement
  (c'est un remboursement de coût, pas du revenu de nuitée). Suivis à part, comptés
  au **mois d'arrivée** du séjour.
- **Taxe de séjour** : jamais dans le CA — elle est collectée pour la commune.
- **Commissions plateformes** : suivies à part quand l'export les donne. Le CA
  hébergement est le montant **avant commission** quand l'export le permet ; sinon
  prends ce que l'export donne et dis-le (l'export Airbnb « Réservations » donne des
  revenus nets de commission hôte, ~3 %).
- **Résas futures** : présentes dans l'export mais après le mois analysé → pas dans
  le CA du mois, mais elles alimentent l'analyse du remplissage à venir (alertes).
- **Arrondis** : on calcule en centimes, on arrondit à l'affichage. ADR et RevPAR à
  2 décimales dans l'historique, entiers acceptés dans le commentaire.

## 3. Point mort : d'où il vient

Ordre de priorité des sources :

1. **La grille de pricing** (`grille-prix-<logement>-*.yaml`, bloc `point_mort`) :
   c'est la source de vérité si elle existe — mêmes hypothèses que celles validées
   avec l'hôte lors du pricing. Prends les 3 hypothèses (prudente / réaliste / haute).
2. **Recalcul depuis le profil** (`mon-logement-*.md`) sinon :
   `point mort/nuitée = (charges_fixes_annuelles + 12 × mensualite_credit) ÷ (365 × occupation) + charges_variables_nuit`
   pour 3 occupations : prudente 0,50, réaliste = `taux_occupation_pct` du profil,
   haute = réaliste + 10 points. Indique dans le rapport que c'est un recalcul.
3. **Rien de tout ça** : demande charges fixes annuelles, mensualité de crédit et
   charges variables par nuit (3 questions). Sans réponse, pas de ligne point mort —
   dis-le plutôt que d'afficher une ligne inventée.

La comparaison qui compte chaque mois : **ADR du mois vs point mort réaliste** (et la
ligne prudente matérialisée sur le graphe ADR). Sous le point mort réaliste, l'hôte
gagne moins que ses coûts complets par nuit vendue.

Nota : si la grille de pricing couvre une période qui n'inclut pas le mois analysé,
son point mort reste valable (il est annuel) mais ne compare pas les prix vendus aux
périodes de la grille — dis simplement que la grille démarre plus tard.

## 4. Nuits disponibles

Nombre de jours réels du mois (28-31), **moins les nuits bloquées par l'hôte**
(usage perso, travaux) s'il les signale — demande-le-lui systématiquement. Un blocage
perso n'est pas une nuit invendue : sans cette correction, l'occupation est faussée
à la baisse et tu déclencherais de fausses alertes.

## 5. Seuils d'alerte

Une alerte = un fait chiffré + UNE recommandation + le skill qui sait la traiter.
Jamais deux recommandations pour une alerte, jamais d'alerte sans chiffre.

| Condition | Niveau | Renvoi |
|---|---|---|
| ADR du mois < point mort réaliste | rouge | pricing-saisonnier (rituel d'ajustement) |
| ADR du mois < point mort prudent | rouge vif — chaque nuit vendue perd de l'argent | pricing-saisonnier |
| Occupation < hypothèse prudente du point mort (souvent 50 %) | orange ; rouge si 2 mois de suite | pricing-saisonnier (ajustement) |
| Occupation en baisse > 15 points vs même mois année précédente | orange | chercher la cause : marché, annonce, prix, avis |
| Remplissage à venir faible (nuits réservées du mois suivant < ⅓ des nuits, vu à ~4 semaines) | orange | pricing-saisonnier (ajustement des 2-3 mois à venir) |
| Note moyenne en baisse ou avis < 4★ signalé dans le mois | orange | reponses-voyageurs-avis (traiter sous 48 h) |
| Données manquantes ou douteuses qui faussent le rapport | grise mais affichée en premier | corriger la donnée avant de conclure |

Pistes (pas des alertes, à glisser dans le commentaire si pertinent) :
- Part du direct < 10 % → opportunité de marge (fidélisation, résas en direct).
- Extras peu vendus alors qu'ils existent (panier petit-déj…) → les proposer au bon
  moment (fiches-voyageurs / messages d'accueil).

## 6. Tendances, cumul annuel et projections

- **Flèches de tendance** : vs mois précédent, lues dans l'historique
  (`historique-pilotage-<logement>.yaml`). Premier mois de suivi → pas de flèches,
  dis que les tendances commencent le mois prochain.
- **Courbes 12 mois** : CA, occupation, ADR (avec ligne point mort) — générées par
  `scripts/graphes_svg.py` depuis l'historique. Moins de 2 mois d'historique → pas de
  courbes, des cartes seulement.
- **Cumul année** : somme des CA de l'année civile en cours vs objectif mensuel ×
  nombre de mois suivis cette année. Si le suivi a commencé en cours d'année, compare
  sur les mois suivis et dis-le — comparer 2 mois de CA à 12 mois d'objectif est
  un mensonge visuel.
- **Projections** : toujours en fourchette (« à ce rythme, l'année se termine entre
  X et Y € »), basées sur le réalisé + la saisonnalité connue, jamais une promesse.

## 7. Structure du rapport

Trois livrables par run, mêmes chiffres partout (détail des formats :
`references/schema-historique.md` pour l'historique, `assets/modele-rapport.html`
pour la page) :

1. **HTML** : cartes KPI avec flèches, ligne point mort matérialisée, courbes 12 mois,
   cumul vs objectif, encadré alertes, 3 actions max, tableau détail replié, pied de
   page sources. Une page, sobre, imprimable, lisible hors-ligne (SVG inline, zéro
   dépendance réseau).
2. **Markdown** : mêmes chiffres en texte — c'est la version copiable/archivable.
3. **Historique YAML** : une entrée par mois, source unique des courbes. Relancer le
   même mois **remplace** son entrée (pas de doublon).

Les **3 actions du mois** (maximum) : priorisées, concrètes, chacune reliée à un
levier précis — pricing (relancer pricing-saisonnier sur les 2-3 mois à venir),
annonce, accueil/avis, extras. Trois actions faites valent mieux que dix vœux pieux ;
si une seule action suffit, n'en invente pas deux autres.
