---
name: fiches-voyageurs
description: Génère le kit d'accueil imprimable complet d'une location courte durée — guide d'accueil recto-verso, fiche WiFi avec QR code, checklist de sortie, fiches équipement (spa, poêle…), livret d'expériences locales enrichi par recherche web — bilingue FR/EN, au design et au ton du logement, livré en HTML + PDF prêts à imprimer. À utiliser dès que l'hôte parle de livret ou guide d'accueil, de fiches à afficher, du WiFi des voyageurs, du check-in/check-out, de recommandations locales à partager, de questions répétitives des voyageurs (« c'est quoi le code WiFi ? », « comment marche le spa ? »), ou de quelque chose à imprimer pour le logement — même s'il ne prononce jamais le mot « fiche ».
---

# Fiches voyageurs — kit d'accueil du logement

Tu produis pour un hôte de location courte durée (souvent non-technicien) un kit
d'accueil **imprimable, charté et bilingue FR/EN** : des documents physiques qui
améliorent l'expérience voyageur, réduisent les questions répétitives et donnent
au logement une image professionnelle. La qualité visée est celle d'un produit
payant : l'hôte doit avoir envie d'encadrer ses fiches.

## Les deux règles non négociables

**Exactitude.** N'invente JAMAIS un horaire, un code, un prix, un réglage ou une
recommandation. Tout vient du profil logement, de l'hôte, ou (pour le livret
local) de recherches web sourcées. Une donnée manquante se demande à l'hôte ou
s'omet — une fiche fausse affichée au mur fait plus de dégâts qu'une fiche absente.

**Sécurité WiFi.** Un QR code WiFi contient le mot de passe **en clair** :
n'importe qui peut le décoder depuis une photo. La fiche WiFi est destinée à
l'**intérieur du logement uniquement**. Dis-le explicitement à l'hôte : ne JAMAIS
publier la fiche WiFi (ni en photo d'annonce, ni sur les réseaux) ; si une photo
du logement la montre, flouter **le QR ET le texte** du mot de passe. Cette mise
en garde figure aussi dans le `LISEZMOI.md` livré.

## Étape 0 — Charger le profil du logement

1. Cherche `mon-logement-*.md` dans le dossier de travail (plusieurs fichiers =
   plusieurs logements : demande lequel). Vérifie `type_fiche: mon-logement` et
   `version_schema: 2` dans le frontmatter YAML, puis parse-le avec un parseur
   YAML (`yaml.safe_load`) — pas d'extraction de valeurs à la main.
2. Profil v1 (sans frontmatter) : lecture best-effort possible, mais propose de
   lancer le skill **mon-logement** pour migrer.
3. Pas de profil du tout : propose **mon-logement** (5 skills s'en nourrissent),
   ou pose uniquement les questions nécessaires aux fiches demandées.
4. `"à compléter"`, `null` ou `[]` = donnée manquante : demande à l'hôte si la
   fiche en a besoin, sinon ignore proprement.

Le frontmatter donne les faits (`sejour.*`, `equipements.*`, `contacts`…) ; le
corps markdown donne l'âme : « Ton & univers de marque » (registre, style),
« Recommandations locales », « Notes libres ». Les deux servent.

## Étape 1 — Cadrer le kit avec l'hôte

Propose le **kit complet (5 pièces)** ou à la carte :

| Pièce | Gabarit (`assets/`) | Pages |
|---|---|---|
| 1. Guide d'accueil | `gabarit-guide-accueil.html` | 2 (recto-verso) |
| 2. Fiche WiFi + QR | `gabarit-fiche-wifi.html` | 1 |
| 3. Checklist de sortie | `gabarit-checklist-sortie.html` | 1 |
| 4. Fiches équipement | `gabarit-fiche-equipement.html` | 1 par équipement |
| 5. Livret d'expériences locales | `gabarit-livret-local.html` | 2-4 |

À clarifier avant de produire (uniquement ce qui manque) :
- **Mot de passe WiFi** : jamais stocké dans le profil (qui ne garde que le nom du
  réseau) — demande-le à l'hôte pour la fiche WiFi.
- **Contact à afficher** : numéro direct ou « via la messagerie Airbnb » ?
- **Fiches équipement** : lesquels le méritent ? (en général les
  `equipements.differenciants` à mode d'emploi : spa, poêle, vidéoprojecteur…)
  Et récupère les consignes réelles d'usage (réglages, durées) auprès de l'hôte
  si le profil ne les donne pas.
- **Code d'accès dans le guide** : si le guide peut sortir du logement, pas de
  code boîte à clés dedans — demande à l'hôte ce qu'il préfère.
- Bilingue FR/EN sur le même document par défaut (EN discret) ; autre langue ou
  monolingue sur demande.

## Étape 2 — Thème : la marque du logement

Lis `references/gabarits-et-theme.md` (section thème). Principe : les gabarits ont
une **structure intouchable** et un bloc `:root` de variables CSS — palette et
polices — que tu adaptes aux couleurs/ambiance du profil (`ton.couleurs`,
`logement.theme`). Trois ambiances de départ sont fournies (Forêt, Lin, Encre) ;
choisis la plus proche, tire-la vers les couleurs réelles du logement, applique
**la même palette aux 5 pièces** et annonce-la à l'hôte en une phrase pour
validation. Jamais de fond de page sombre (impression), jamais d'emojis en pluie,
pas de violet « IA ».

## Étape 3 — Produire les fiches

Pour chaque pièce, pars du gabarit (copie-le, ne modifie jamais `assets/`) et
remplace les `{{variables}}` et blocs répétables `↻` — liste complète par gabarit
dans `references/gabarits-et-theme.md` §5.

- **Ton** : celui du profil (tutoiement/vouvoiement, chaleur, humour). On écrit
  comme l'hôte parle à ses voyageurs, pas comme un hôtel-chaîne. La checklist de
  sortie reste positive et complice — une aide entre amis, pas un règlement.
- **Bilingue** : FR d'abord, EN en dessous via la classe `.en` (plus discret mais
  complet sur l'essentiel — un anglophone doit pouvoir tout utiliser). L'EN est une
  adaptation naturelle, pas du mot à mot.
- **Livret local** : lis `references/livret-local.md` AVANT de le rédiger —
  recherche web pour distances/temps de route et infos pratiques vérifiées,
  sources fiables uniquement, « se renseigner sur place » plutôt qu'une invention.
- Nettoie les commentaires de gabarit du HTML final livré.

**QR code WiFi** :
```bash
python scripts/make_qr.py "NomDuReseau" "MotDePasse" qr-wifi.png
```
(module manquant : `pip install --user "qrcode[pil]"`). Place `qr-wifi.png` à côté
du HTML de la fiche. Si rien ne permet de générer le QR : utilise le bloc FALLBACK
commenté dans le gabarit (cadre « coller le QR ici ») et donne à l'hôte la chaîne
exacte à encoder dans un générateur fiable :
`WIFI:T:WPA;S:<nom_du_reseau>;P:<mot_de_passe>;;`

## Étape 4 — PDF et vérification

Convertis chaque fiche et vérifie sa pagination d'un même geste :
```bash
python scripts/html_to_pdf.py fiche.html fiche.pdf --pages-attendues 1
```
(guide d'accueil : `--pages-attendues 2` ; livret : le nombre de pages construit).
Le script essaie Chrome/Chromium headless puis WeasyPrint ; code de sortie 3 =
aucun convertisseur → livre les HTML seuls, ils s'impriment très bien depuis un
navigateur (le LISEZMOI explique comment). Code 4 = débordement → raccourcis ou
rééquilibre le **contenu** (jamais les styles) et reconvertis, jusqu'à ce que
chaque pièce tombe juste. Cette boucle n'est pas optionnelle : les polices de
substitution varient selon la machine, seul le compte de pages fait foi.

Relis ensuite chaque fiche en te demandant pour chaque fait « d'où je tiens ça ? »
— profil, hôte, ou source web fiable. Vérifie le bilingue et la cohérence de la
palette entre les pièces.

## Étape 5 — Livrer

Dossier `fiches-<slug-du-logement>/` dans le dossier de travail :
- un HTML (+ PDF si la conversion a marché) par pièce, noms parlants
  (`guide-accueil.html`, `fiche-wifi.html`, `checklist-sortie.html`,
  `fiche-spa.html`, `livret-local.html`…), `qr-wifi.png` ;
- un `LISEZMOI.md` rédigé pour un non-technicien : ce que contient le kit, comment
  imprimer (A4, « graphiques d'arrière-plan » cochés, recto-verso pour le guide,
  papier 160-200 g conseillé, plastifier checklist et fiches équipement), **où
  placer chaque fiche** dans le logement (entrée, près de la box, près de
  l'équipement…), la **mise en garde WiFi complète** (jamais publier, flouter QR
  ET texte sur toute photo), et le rappel : relancer ce skill à chaque changement
  (code, équipement, adresse) — le kit se régénère en quelques minutes.

Termine la conversation par : la liste des fichiers produits, la palette utilisée,
les éventuels points à confirmer (infos non vérifiées du livret, données
manquantes), et la mise en garde WiFi une dernière fois.

## Ressources du skill

| Fichier | Quand le lire/utiliser |
|---|---|
| `assets/gabarit-*.html` | base de chaque pièce — copier, jamais modifier |
| `references/gabarits-et-theme.md` | avant le thème (Étape 2) et le remplissage (Étape 3) |
| `references/livret-local.md` | avant de rédiger le livret local |
| `scripts/make_qr.py` | QR WiFi (Étape 3) |
| `scripts/html_to_pdf.py` | conversion + contrôle pagination (Étape 4) |
