# Schéma de l'historique — `historique-pilotage-<logement>.yaml`

L'historique est la **mémoire chiffrée** du pilotage : une entrée par mois, tous les
KPI. C'est la source unique des flèches de tendance et des courbes 12 mois du
rapport (`scripts/graphes_svg.py` le lit directement). Le rapport HTML et le rapport
markdown sont des rendus ; l'historique est la donnée.

Face à l'hôte, c'est « ton carnet de bord » — jamais « le YAML ».

Nommage : `historique-pilotage-<logement>.yaml` avec `<logement>` en
minuscules-avec-tirets, même slug que le profil (ex. `la-canopee-du-herisson`).
Emplacement : le dossier de travail de l'hôte, à côté du profil. UN fichier par
logement, qui grandit mois après mois.

## Règles d'écriture

- Les entrées de `mois` sont **triées chronologiquement**, la plus récente en dernier.
- Relancer un mois déjà présent **remplace** son entrée (jamais de doublon de mois) ;
  noter dans `notes` qu'il s'agit d'une révision si les chiffres ont changé.
- Tous les montants dans la devise du fichier (`devise`), 2 décimales max.
- Donnée indisponible → `null` (jamais 0, qui est une vraie valeur, jamais une
  invention). Les lecteurs vérifient le type avant de calculer.
- Ne jamais renommer ou supprimer une clé existante ; pour enrichir, AJOUTER des
  clés et incrémenter `schema_version`.

## Schéma commenté

```yaml
type_fiche: historique-pilotage     # marqueur fixe — identification du fichier
schema_version: 1
logement: la-canopee-du-herisson    # slug, même que le profil mon-logement
nom_logement: "La Canopée du Hérisson"
devise: EUR
objectif_ca_mensuel: 2900           # nombre extrait de chiffres.objectif du profil
                                    # (null si l'hôte n'a pas d'objectif)
point_mort:                         # rappel de la référence utilisée pour les alertes
  source: "grille-prix-la-canopee-du-herisson-2026-2027.yaml"
                                    # ou "recalcul doctrine depuis le profil"
  prudente: 100.19                  # €/nuit
  realiste: 84.28
  haute: 75.08

mois:                               # une entrée par mois suivi, chronologique
  - mois: "2026-05"                 # AAAA-MM
    genere_le: "2026-06-11"         # date du run
    ca_hebergement: 2985.00         # hors ménage, hors taxe — conventions doctrine
    nuits_louees: 17
    nuits_disponibles: 31           # jours du mois - nuits bloquées par l'hôte
    nuits_bloquees: 0
    occupation_pct: 54.8
    adr: 175.59
    revpar: 96.29
    menage_facture: 420.00          # ménage refacturé (mois d'arrivée des séjours)
    taxe_sejour: 0.00               # 0 si collectée-reversée par la plateforme
    commissions_plateformes: 0.00   # quand l'export les donne, sinon null
    indemnites_annulation: 92.50
    mix_canaux:                     # un bloc par canal actif ce mois-ci
      airbnb: { ca_hebergement: 2985.00, nuits: 17 }
    vs_objectif_pct: 2.9            # (CA - objectif) / objectif × 100 ; null sans objectif
    alertes: []                     # libellés courts des alertes levées ce mois
    sources:                        # fichiers d'exports utilisés (traçabilité)
      - "export-airbnb-canopee-mai-juin-2026.csv"
    notes: ""                       # lecture manuelle, données partielles, révision…
```

## Qui lit quoi

- **`scripts/graphes_svg.py`** : `mois[].mois`, `ca_hebergement`, `occupation_pct`,
  `adr`, plus `objectif_ca_mensuel` et `point_mort.realiste`/`prudente` pour les
  lignes de référence. Il se contente des 12 dernières entrées.
- **Le rapport du mois suivant** : l'entrée précédente (flèches de tendance) et le
  même mois de l'année d'avant s'il existe (alerte « baisse > 15 points vs n-1 »).
- **pricing-saisonnier (rituel d'ajustement)** : occupation et ADR réels des
  derniers mois — des données bien plus fiables que les estimations de l'hôte.
