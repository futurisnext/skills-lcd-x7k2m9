# Protocole de relevé des prix concurrents

Pourquoi un relevé réel : les prix Airbnb changent en permanence (saisons, promos, tarification dynamique). Une recherche web renvoie des prix périmés ou des moyennes sans dates ; ta mémoire d'entraînement est encore moins fiable. Seuls comptent les prix **réellement affichés à une date de relevé connue, pour des dates de séjour précises**. C'est pour ça que tout relevé est daté dans la grille — un relevé vaut pour sa date.

## 0. Préparer le relevé (commun aux deux voies)

**Les concurrents** : 3 à 5 biens de **même typologie, capacité ±2 voyageurs** (cf. règle des comparables, `doctrine-pricing.md` § 1). Prendre ceux du profil `mon-logement-*.md` ; sinon les demander à l'hôte ; sinon les chercher sur Airbnb dans la zone (jusqu'à 45-60 min pour un bien expérientiel). Écarter ou marquer « indicatif » tout bien hors typologie.

**Les 4 fenêtres de dates** (mode CRÉATION) — toujours des dates précises, dans les 12 prochains mois, choisies d'après les calendriers déjà recherchés :

| Fenêtre | Définition | Exemple type |
|---|---|---|
| WE haute saison | vendredi → dimanche en pleine haute saison | un WE d'août, ou de Noël en montagne |
| Semaine haute saison | lundi → vendredi (4 nuits) en haute saison | une semaine d'août ou de vacances scolaires |
| WE moyenne saison | vendredi → dimanche hors vacances, demande normale | un WE de fin mai ou d'octobre |
| Semaine basse saison | lundi → vendredi (4 nuits) en creux | une semaine de novembre ou de mars hors vacances |

En mode AJUSTEMENT : 2 fenêtres suffisent (un week-end + une semaine) dans les 2-3 mois à venir.

Noter pour chaque relevé : le prix **par nuit affiché** (avant frais de ménage et frais de service — c'est le prix qui se compare), et si le bien est **déjà complet** sur la fenêtre (information précieuse : complet longtemps à l'avance = probablement sous-tarifé).

## 1. Voie principale — relevé par navigation (Claude in Chrome / navigateur piloté)

D'abord, tester la capacité : tenter d'ouvrir une page (ex. airbnb.fr). Si ça marche, dérouler ; si ça échoue ou qu'aucun outil de navigation n'est disponible, basculer en voie 2 **sans jargon** : « je vais te guider pour relever les prix nous-mêmes, c'est rapide et plus fiable ».

Déroulé, pour chaque fenêtre de dates :

1. Ouvrir airbnb.fr et chercher la zone du logement avec les dates de la fenêtre et le nombre de voyageurs du bien.
2. Retrouver chacun des concurrents de la liste (par nom d'annonce ; à défaut, par commune + type). Si un concurrent reste introuvable, le dire et continuer.
3. Sur la page de l'annonce avec les dates renseignées, relever le **prix par nuit affiché** et noter si les dates sont indisponibles (= complet).
4. Au passage, repérer 1-2 biens comparables non listés par l'hôte qui ressortent dans la recherche — les proposer comme concurrents additionnels s'ils respectent la règle des comparables.

Pièges connus : le prix « à partir de » des cartes de recherche n'est pas le prix des dates — toujours ouvrir l'annonce avec les dates ; certains affichages incluent les frais dans le total — relever le prix par nuit hors frais ; si Airbnb affiche une autre devise, le noter.

Restituer le relevé à l'hôte sous forme de petit tableau (concurrent × fenêtre) et faire valider avant de construire la grille.

## 2. Fallback — relevé guidé par l'hôte

Quand la navigation n'est pas disponible. Le présenter comme une mini-séance à deux (~10 min), une fenêtre à la fois — jamais les 4 d'un coup, ça noie l'hôte.

Script de guidage, à adapter au ton du profil :

1. « Ouvre Airbnb (le site ou l'appli) et cherche "<zone>" avec ces dates : **du <date> au <date>**, pour **<N> voyageurs**. »
2. « Dans les résultats, retrouve "<nom du concurrent>". Ouvre son annonce. »
3. « Donne-moi le **prix par nuit** affiché (pas le total avec les frais). Tu peux aussi me faire une **capture d'écran** et me l'envoyer — je sais la lire. Si les dates sont barrées ou indisponibles, dis-le moi : c'est une info utile. »
4. Répéter pour chaque concurrent, puis passer à la fenêtre suivante.

Lecture des captures : en extraire le prix par nuit, les dates affichées et le nom de l'annonce ; vérifier que les dates à l'écran sont bien celles de la fenêtre (sinon le signaler gentiment et faire reprendre). Si l'hôte donne un total de séjour, le convertir en prix/nuit en retirant les frais de ménage s'ils sont identifiables, et noter l'approximation.

Si l'hôte n'a pas le temps de tout relever : accepter un relevé partiel, le signaler comme tel dans la grille, et combler avec les prix « connus de l'hôte » marqués comme déclaratifs (moins fiables qu'un relevé).

## 3. Consigner le relevé

Dans le fichier de la grille (`schema-grille.md`, bloc `releve_concurrents`) : date du relevé, méthode (`navigation` ou `guide-par-hote`), fenêtres avec leurs dates réelles, et pour chaque concurrent ses prix par fenêtre (ou `complet`, ou `non-trouve`). Dans la version lisible : le tableau du relevé avec sa date et la mention de la méthode.
