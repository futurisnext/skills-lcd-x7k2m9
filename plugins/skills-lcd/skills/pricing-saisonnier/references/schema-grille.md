# Schéma du fichier de grille — `grille-prix-<logement>-<annee>.yaml`

C'est la version **structurée** de la grille : la source de vérité que relisent le mode AJUSTEMENT et le skill pilotage-dashboard. Les versions `.md` et `.html` sont des rendus de ce fichier — en cas de modification, toujours modifier le fichier de grille d'abord, puis régénérer les rendus.

Nommage : `<logement>` en minuscules-avec-tirets (ex. `la-canopee-du-herisson`), `<annee>` = période couverte (`2026` ou `2026-2027` si la grille est à cheval).

Conventions :
- Dates au format `AAAA-MM-JJ`. Prix en euros entiers, **par nuit, hors frais de ménage et taxe de séjour**.
- « Week-end » = nuits du vendredi et du samedi.
- Les périodes couvrent l'année **sans trou ni chevauchement** ; les `evenements` sont des surcharges ponctuelles qui priment sur la période qui les contient.
- Champ inconnu → omettre la clé ou `null` + une entrée dans `donnees_manquantes`. Ne jamais inventer une valeur.

## Schéma commenté

```yaml
schema_version: 1
logement:
  nom: la-canopee-du-herisson        # même slug que le profil mon-logement
  typologie: insolite-experientiel   # classique | atypique-immersif | insolite-experientiel
  capacite: 2
  commune: "Menétrux-en-Joux (39)"
periode_couverte:
  debut: 2026-07-01
  fin: 2027-06-30
genere_le: 2026-06-11                # date de génération/dernière mise à jour
mode_generation: creation            # creation | ajustement

point_mort:
  charges_fixes_annuelles: 4800      # € (assurance, abonnements, compta, entretien…)
  mensualite_credit: 850             # €/mois (0 si pas de crédit)
  charges_variables_nuit: 18         # €/nuit louée
  hypotheses:                        # toujours 3 : prudente / realiste / haute — valeurs sorties de scripts/point_mort.py, jamais recalculées de tête
    - { nom: prudente, occupation: 0.50, nuits_louees: 182, point_mort_nuit: 100.19 }
    - { nom: realiste, occupation: 0.62, nuits_louees: 226, point_mort_nuit: 84.28 }
    - { nom: haute,    occupation: 0.72, nuits_louees: 263, point_mort_nuit: 75.08 }
  plancher_retenu: 101               # = point mort de l'hypothèse prudente, arrondi à l'euro supérieur

releve_concurrents:
  date_releve: 2026-06-11
  methode: guide-par-hote            # navigation | guide-par-hote | declaratif
  fenetres:                          # les fenêtres de dates réellement utilisées
    - { id: we-haute,       debut: 2026-08-14, fin: 2026-08-16 }
    - { id: semaine-haute,  debut: 2026-08-10, fin: 2026-08-14 }
    - { id: we-moyenne,     debut: 2026-10-09, fin: 2026-10-11 }
    - { id: semaine-basse,  debut: 2026-11-16, fin: 2026-11-20 }
  concurrents:
    - nom: "Bulle des Lacs"
      commune: Doucier
      capacite: 2
      prix:                          # €/nuit par fenêtre ; "complet" | "non-trouve" acceptés
        we-haute: 235
        semaine-haute: 205
        we-moyenne: 195
        semaine-basse: complet
      note: "spa privatif, typologie identique"   # optionnel

periodes:                            # triées par date, sans trou ni chevauchement
  - nom: "Haute saison été"
    debut: 2026-07-04
    fin: 2026-08-30
    saison: haute                    # basse | moyenne | haute | tres-haute
    prix_semaine: 195                # €/nuit dimanche→jeudi
    prix_weekend: 225                # €/nuit vendredi & samedi
    min_stay_semaine: 2              # nuits minimum
    min_stay_weekend: 2
    justification: "Vacances d'été toutes zones, saison cascades, pic de demande couples"
    sources: ["education.gouv.fr — calendrier scolaire 2026-2027"]   # si calendrier externe

evenements:                          # surcharges ponctuelles (optionnel)
  - nom: "Saint-Valentin"
    debut: 2027-02-12
    fin: 2027-02-14
    prix: 260                        # €/nuit pendant l'événement (remplace la période)
    min_stay: 2
    justification: "Pic majeur pour un bien couples/romantique"
    sources: []

recommandations:                     # 3 max, priorisées
  - "Imposer 2 nuits minimum sur tous les week-ends de haute saison"

donnees_manquantes:                  # honnêteté : ce qui fiabiliserait la grille
  - "Taux d'occupation réel par mois (export Airbnb) — affinerait les hypothèses du point mort"

sources:                             # sources globales (calendriers, événements)
  - "education.gouv.fr — calendrier scolaire 2026-2027 (zones A/B/C)"

historique_ajustements: []           # rempli par le mode AJUSTEMENT, plus récent en premier
  # - date: 2026-12-01
  #   periodes_modifiees: ["Basse saison automne"]
  #   deltas: ["prix_semaine 145 → 135"]
  #   motif: "Occupation novembre faible (38 %), marché en baisse au relevé du 01/12"
```

## Ce que lisent les autres consommateurs

- **Mode AJUSTEMENT** : `periodes` (dates et prix à retoucher), `releve_concurrents.date_releve` (fraîcheur), `point_mort.plancher_retenu` (plancher), `historique_ajustements` (ne pas re-proposer un delta déjà refusé/appliqué).
- **pilotage-dashboard** : `point_mort.hypotheses` et `plancher_retenu` (comparer l'ADR réel au point mort), `periodes` (comparer prix vendus vs grille), `logement.nom` (rapprochement avec le profil).

Toute évolution du schéma incrémente `schema_version` et reste rétro-compatible en lecture (les anciens champs gardent leur sens).
