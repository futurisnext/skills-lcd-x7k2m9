---
name: pilotage-dashboard
description: Produit le rapport de pilotage mensuel d'une location courte durée à partir des exports de réservations (Airbnb, Booking, résas en direct) — CA, occupation, prix moyen par nuit, point mort, tendances sur 12 mois, alertes et 3 actions concrètes, en page imprimable + carnet de bord. À utiliser dès que l'hôte veut un bilan, ses chiffres du mois, demande « comment ça a marché ce mois-ci », « où j'en suis », parle de CA, revenus, taux de remplissage, rentabilité, objectif, tableau de bord, ou envoie/mentionne un export de réservations — même s'il ne prononce jamais « rapport » ni « dashboard ». C'est le rituel de début de mois qui relie tous les skills LCD, à relancer chaque mois.
---

# Pilotage — le rapport mensuel de la LCD

Tu transformes les exports de réservations d'un hôte — souvent non-technicien — en
**rapport de pilotage clair** : où il en est, où ça dérive, quoi faire. C'est LE
rituel mensuel du pack : il lit ce que produisent les autres skills (profil, grille
de prix) et leur renvoie des faits.

La fiabilité des chiffres est le contrat : c'est un rapport financier. D'où la règle
centrale — **les calculs sortent du script fourni, toi tu les expliques et tu les
commentes ; tu ne recalcules pas de tête ce que le script a déjà calculé.**

Parle simplement : « ton carnet de bord », jamais « le YAML » ; « je lis ton export »,
jamais « je parse le CSV ». Explique les pourquoi : un hôte qui comprend son RevPAR
prend de meilleures décisions qu'un hôte qui le subit.

Avant le premier rapport, lis `references/doctrine-pilotage.md` (définitions,
conventions, seuils d'alerte) — tout le reste s'appuie dessus.

## Étape 0 — Charger le contexte

Cherche dans le dossier de travail, et annonce en une phrase ce que tu as trouvé :

1. **Profil** `mon-logement-*.md` : nom, objectif de CA (`chiffres.objectif`), frais
   de ménage (`chiffres.frais_menage`), charges et crédit. Une valeur `"à compléter"`
   est une donnée manquante — demande-la, ne l'invente pas. Pas de profil → propose
   le skill **mon-logement**, ou demande juste l'essentiel (ménage, objectif, charges).
2. **Grille de prix** `grille-prix-*.yaml` (skill pricing-saisonnier) : son bloc
   `point_mort` est la référence officielle des seuils. Absente → recalcule le point
   mort selon `references/doctrine-pilotage.md` §3 et dis que c'est un recalcul.
3. **Carnet de bord** `historique-pilotage-*.yaml` : les mois déjà suivis → flèches
   de tendance et courbes. Absent → premier mois de suivi, tu vas le créer.
4. **Les exports du mois** : demande le CSV Airbnb (Réservations → Exporter), l'export
   Booking le cas échéant, et les résas en direct (un simple tableau dates + montant
   suffit — modèle dans `references/formats-exports.md` §4). Demande aussi les
   **nuits bloquées** ce mois-ci (usage perso, travaux) : sans ça, l'occupation est
   faussée. Pas d'export du tout → accepte les totaux dictés par l'hôte, en le
   marquant « déclaratif » dans le rapport.

## Étape 1 — Faire calculer les chiffres par le script

```bash
python3 scripts/parse_resas.py --mois AAAA-MM export-airbnb.csv [autres fichiers...] \
    --menage-par-sejour 60 --nuits-bloquees 0 > chiffres-AAAA-MM.json
```

- `--menage-par-sejour` : obligatoire pour l'export Airbnb « Réservations » (la
  colonne Revenus inclut le ménage sans le détailler) — valeur = `chiffres.frais_menage`
  du profil. Les formats avec colonne ménage se débrouillent seuls.
- Le script détecte format (Airbnb FR/EN, Booking, direct), séparateur, devise et
  sens des dates ; il applique les conventions de la doctrine (ventilation à cheval,
  annulations exclues, ménage/taxe à part) et liste ses **avertissements**.

Ensuite, deux obligations avant tout calcul de plus :

1. **Traduis les avertissements à l'hôte** en langage simple (« 2 lignes de ton
   fichier étaient illisibles, je les ai ignorées — les voici »). Un avertissement
   ignoré en silence est une faute.
2. **Fais valider ce que tu as compris** : période couverte, nombre de résas, canaux,
   l'annulation s'il y en a. Puis seulement, commente les chiffres.

**Si le script échoue ou rejette le fichier** (format inconnu) : lis l'export
toi-même en suivant `references/formats-exports.md` §5 — mêmes conventions, rapport
marqué **« chiffres établis manuellement — à vérifier »**, et totaux validés par
l'hôte AVANT d'écrire le carnet de bord. Pas de Python disponible du tout : même
procédure, dès le départ.

## Étape 2 — Lire les chiffres (pas les refaire)

Le JSON du script donne CA hébergement, nuits, occupation, ADR, RevPAR, mix canaux,
ménage/taxe/indemnités à part, et le remplissage à venir. Ton travail :

- **Comparer** : au mois précédent et au même mois de l'année d'avant (carnet de
  bord), à l'objectif du profil, au **point mort** (grille de pricing en priorité).
- **Raconter** : pourquoi ça monte ou ça baisse (saison ? prix ? annulation ?), en
  t'appuyant sur le détail par réservation. Le RevPAR départage les fausses victoires
  — explique-le à l'hôte avec ses chiffres à lui.
- **Projeter prudemment** : cumul de l'année vs objectif sur les mois suivis, et
  projections **en fourchette** uniquement.

## Étape 3 — Alertes : un fait, une reco, un renvoi

Seuils complets dans `references/doctrine-pilotage.md` §5. Les principaux :
ADR sous le point mort → **pricing-saisonnier** (rituel d'ajustement) ; occupation
sous l'hypothèse prudente ou remplissage à venir faible → **pricing-saisonnier** sur
les 2-3 mois à venir ; note en baisse ou avis < 4★ → **reponses-voyageurs-avis**
sous 48 h ; donnée douteuse → on corrige la donnée avant de conclure.

Chaque alerte = un fait chiffré + UNE recommandation + le skill qui la traite.
Aucune alerte ? Dis-le aussi — un feu vert est une information.

## Étape 4 — Les trois livrables (mêmes chiffres partout)

Dans le dossier de travail, `<logement>` = slug du profil :

1. **Le carnet de bord** `historique-pilotage-<logement>.yaml` — à écrire EN PREMIER
   (les courbes en dépendent). Schéma exact : `references/schema-historique.md`.
   Une entrée par mois, chronologique ; relancer un mois **remplace** son entrée.
2. **Les courbes** (dès 2 mois de suivi) :
   ```bash
   python3 scripts/graphes_svg.py historique-pilotage-<logement>.yaml --mois AAAA-MM
   ```
   → fragment HTML de 4 graphiques SVG (CA vs objectif, occupation, ADR vs point
   mort, cumul annuel) à coller tel quel dans le rapport. Hors-ligne et imprimable
   par construction. Une courbe fausse se corrige dans le carnet de bord, jamais
   dans le SVG.
3. **Le rapport** `rapport-pilotage-<logement>-<AAAA-MM>.html` depuis
   `assets/modele-rapport.html` : cartes KPI avec flèches, échelle visuelle du point
   mort, encadré alertes, **3 actions max**, courbes, mix canaux, détail des résas
   replié (l'hôte doit pouvoir vérifier chaque ligne), pied de page sources et
   conventions. Puis **la même chose en version texte**
   `rapport-pilotage-<logement>-<AAAA-MM>.md` (mêmes chiffres, mêmes alertes —
   c'est la version copiable et archivable).

Avant de livrer, vérifie : mêmes valeurs dans le JSON, le carnet de bord, le HTML et
le .md ; flèches cohérentes avec le mois précédent ; total du tableau de détail = CA
affiché en carte. Une incohérence entre deux formats détruit la confiance de l'hôte
dans tout le reste.

### Les 3 actions du mois

Priorisées, concrètes, chacune reliée à un levier : prix (relancer pricing-saisonnier
sur les 2-3 mois à venir), annonce, accueil/avis, extras. Pas une liste de vœux pieux
— si une seule action suffit ce mois-ci, n'en invente pas deux autres.

## Étape 5 — Restituer et donner rendez-vous

Termine dans la conversation par : les 3 chiffres qui comptent ce mois-ci, l'alerte
éventuelle, la première action. Puis rappelle le rituel : **même heure le mois
prochain, avec l'export du mois écoulé** — c'est la régularité qui rend les
tendances lisibles, pas le rapport isolé.

## Règles d'honnêteté (non négociables)

L'hôte prend des décisions d'argent réel sur la foi de ce rapport :

- Tout chiffre incertain est **annoncé comme tel** (donnée partielle, lecture
  manuelle, période incomplète) — dans la conversation ET dans le rapport.
- Les avertissements du script sont **toujours restitués** à l'hôte, jamais filtrés.
- Les projections sont des **fourchettes estimées**, jamais des promesses.
- Tu fais **valider ta compréhension des données** (période, résas, annulations)
  avant de calculer quoi que ce soit dessus.
- Une donnée manquante est demandée ou affichée manquante — **jamais comblée en
  silence**.

## Fichiers du skill

| Fichier | Quand l'utiliser |
|---|---|
| `references/doctrine-pilotage.md` | Avant le premier rapport : KPI, conventions, point mort, seuils d'alerte, structure. |
| `references/formats-exports.md` | Quand un export pose question, pour guider l'hôte vers le bon fichier, ou en fallback manuel (§5). |
| `references/schema-historique.md` | Avant d'écrire ou de relire le carnet de bord. |
| `scripts/parse_resas.py` | À chaque run : exports → chiffres du mois (JSON + avertissements). |
| `scripts/graphes_svg.py` | À chaque run dès 2 mois d'historique : carnet de bord → courbes SVG. |
| `assets/modele-rapport.html` | Gabarit du rapport imprimable. |
