# Livret d'expériences locales — méthode

La pièce « waouh » du kit : les recommandations brutes du profil, transformées en
carnet d'adresses digne d'une conciergerie. Sa valeur tient à UNE chose : chaque
info pratique est vraie. Un voyageur qui fait 25 minutes de route vers un
restaurant fermé le mardi ne pardonnera ni au livret, ni à l'hôte.

## Matière première

1. **Section « Recommandations locales » du profil** : la liste de l'hôte, avec ses
   « pourquoi on l'aime ». C'est le cœur — le ton personnel est irremplaçable.
2. **Le contexte** : `logement.commune`, `logement.zone`, `marche.evenements`
   (les événements saisonniers font d'excellentes recos « selon la période »).
3. **L'hôte lui-même** : si le profil compte moins de 4-5 recos, demander 2-3
   adresses de plus (« le resto où TU emmènes tes amis ? ») plutôt que de combler
   avec des choix impersonnels trouvés en ligne.

## Enrichissement par recherche web

Pour CHAQUE lieu recommandé, chercher en ligne (si la recherche web est disponible) :

- **Distance et temps de route** depuis la commune du logement — l'info que tout
  voyageur veut et qu'aucun hôte ne pense à écrire. Format pastille : « 10 min · 6 km ».
  En zone rurale, le temps compte plus que les kilomètres.
- **Infos pratiques vérifiables** : adresse ou point de repère, période d'ouverture
  (saisonnier ?), jour de fermeture, fourchette de prix, réservation conseillée ?
- **Pièges connus** : fermeture définitive (ça arrive — alerter l'hôte plutôt que
  publier), accès payant, sentier fermé hors saison…

Règles d'exactitude, dans l'ordre :
1. Ce que dit l'hôte (profil) prime sur le web pour le ressenti et le ton.
2. Le web prime pour les faits récents (horaires, prix, fermetures) — mais
   uniquement des sources fiables : site officiel du lieu, office de tourisme,
   pages institutionnelles. Pas un blog de 2019.
3. **Une info introuvable ou douteuse ne s'invente pas** : écrire « se renseigner
   sur place » ou omettre, et signaler à l'hôte la liste des points à confirmer.
4. Horaires précis = piège (ils changent) : préférer « ouvert à l'année »,
   « l'été uniquement », « fermé le lundi (à confirmer) » + le colophon du gabarit
   qui invite à vérifier avant de se déplacer, avec la date de vérification.
5. Sans recherche web disponible : livret quand même, avec les seules infos du
   profil + distances estimées marquées « ~ », et dire à l'hôte de relire les
   infos pratiques avant impression.

## Rédaction

- **Organiser en 2-4 sections** selon la matière : « À table / Eating out »,
  « À voir, à vivre / See & do », « Pépites locales / Local gems »… Adapter les
  intitulés au lieu (« Sur l'eau », « Côté neige »…), pas de section d'un seul item.
- **Description FR (2-3 phrases)** : le ressenti de l'hôte reformulé dans le ton du
  profil, + un détail concret appris en recherche qui donne envie. Pas de superlatifs
  vides (« incontournable », « magnifique ») — du spécifique.
- **EN (1-2 phrases)** : l'essentiel, pas une traduction mot à mot.
- **Ligne pratique** : 3-5 faits maximum, séparés par des « · » :
  `Ilay, au bord du sentier des cascades · ouvert à l'année · ~25 € · réservation conseillée le week-end`.
- 6 à 12 recos au total : en dessous le livret est maigre, au-dessus il devient un
  annuaire. La sélection EST le service.
- Ordonner chaque section du plus proche au plus lointain, ou du plus emblématique
  au plus confidentiel — un ordre voulu, pas l'ordre du profil.
- **Cible d'impression : 2 OU 4 pages, jamais 1 ni 3.** Le livret s'imprime soit en
  recto-verso (2 pages), soit en feuille A4 pliée en livret (4 pages) ; 3 pages ne
  tombe sur aucun des deux et gâche du papier. Calibre la matière pour viser l'un
  des deux : s'il déborde à 3 pages, soit resserrer à 2 (sélection plus stricte,
  descriptions plus courtes), soit enrichir à 4 (étoffer les recos, ajouter une
  section, ou une page « infos pratiques » : marché, pharmacie, numéros utiles).
  Annoncer à l'hôte la cible retenue. C'est un arbitrage de contenu, jamais de mise
  en page : règle le compte de pages via `--pages-attendues` sur le total visé.

## Avant livraison

- Relire chaque ligne pratique en se demandant « d'où je tiens ça ? » : profil,
  source web fiable, ou estimation marquée comme telle.
- Renseigner `{{date_maj}}` (mois + année de la vérification) dans le colophon.
- Donner à l'hôte la courte liste des points non vérifiés à confirmer, et rappeler
  que le livret se régénère en 5 minutes quand une adresse change.
