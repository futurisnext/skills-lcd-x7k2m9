# Formats d'exports de réservations — ce que les plateformes donnent vraiment

Référence des formats que `scripts/parse_resas.py` sait lire, et de leurs pièges.
À lire quand un export ne passe pas dans le script, ou pour guider l'hôte vers le
bon fichier à télécharger.

## 1. Airbnb — export « Réservations » (le cas le plus courant)

Où : airbnb.fr → Réservations → bouton Exporter (fichier `reservations.csv`).

Colonnes observées, **dans la langue du compte** :

| FR | EN |
|---|---|
| Code de confirmation | Confirmation code |
| Statut | Status |
| Nom du voyageur | Guest name |
| Contact | Contact |
| Nombre d'adultes / d'enfants / de bébés | # of adults / children / infants |
| Date de début / Date de fin | Start date / End date |
| Nombre de nuits | # of nights |
| Réservée | Booked |
| Annonce | Listing |
| Revenus | Earnings |

Pièges :
- **« Revenus » inclut les frais de ménage** et est net de la commission hôte (~3 %).
  Il n'y a PAS de colonne ménage → passer `--menage-par-sejour <montant>` au script
  (le montant est dans le profil `mon-logement`, clé `chiffres.frais_menage`).
- **Pas de colonne taxe de séjour** : Airbnb la collecte et la reverse directement
  dans la plupart des communes françaises — elle n'est pas dans « Revenus », rien à
  retirer.
- **Dates** : `JJ/MM/AAAA` sur les comptes FR, `MM/JJ/AAAA` sur les comptes EN — et
  des cas mixtes sont rapportés par des hôtes. Le script tranche sur l'ensemble du
  fichier (un jour > 12 lève l'ambiguïté) et avertit si ça reste ambigu.
- **Statuts** : Passée / Confirmée / Annulée par le voyageur (FR) ; Checked out /
  Confirmed / Cancelled by guest (EN). Tout statut contenant « annul »/« cancel »
  est exclu du CA ; un montant > 0 sur une ligne annulée = indemnité, suivie à part.
- L'export contient les **résas futures** : normal, elles servent à l'analyse du
  remplissage à venir.

## 2. Airbnb — rapport « Revenus » (transaction history / earnings)

Où : airbnb.fr → Menu → Revenus → Obtenir un rapport (CSV, champs configurables).

Colonnes typiques : Date, Type, Code de confirmation, Date de début, Nuits, Voyageur,
Annonce, Devise, Montant, Versé / Paid out, Frais de service / Host fee,
Frais de ménage / Cleaning fee, Revenus bruts / Gross earnings,
Taxes de séjour / Occupancy taxes.

Pièges :
- **« Gross earnings » inclut le ménage**, mais ici la colonne ménage existe → le
  script la soustrait tout seul, pas besoin de `--menage-par-sejour`.
- Les taxes collectées par Airbnb sont dans leur colonne, PAS dans le montant.
- Une ligne = une transaction (versement, ajustement, indemnité), pas toujours une
  résa : les lignes sans dates de séjour sont ignorées avec avertissement — normal.

## 3. Booking.com — export de l'extranet

Où : extranet admin.booking.com → Réservations → flèche de téléchargement (CSV/XLS).
Si l'hôte a un fichier `.xls`/`.xlsx`, demande-lui de le ré-enregistrer en CSV
(le script ne lit pas les classeurs Excel).

Colonnes typiques (FR) : Numéro de réservation, Réservé par, Nom du client, Arrivée,
Départ, Statut, Personnes, Tarif, Montant de la commission, Date de réservation,
Remarques. Souvent séparées par `;` (détecté automatiquement).

Pièges :
- **Statuts** : `ok`, `cancelled_by_guest`, `no_show`. Le script exclut annulations
  et no-shows du CA.
- **« Tarif »** : montant total du séjour, souvent préfixé `EUR `. Le ménage n'a pas
  de colonne dédiée → `--menage-par-sejour` si l'hôte facture le ménage sur Booking.
- **La commission Booking (~15-17 %) n'est PAS déduite du tarif** : le CA est bien le
  tarif affiché ; la commission est suivie à part.
- Taxe de séjour : selon le paramétrage, parfois incluse dans le tarif — demander à
  l'hôte au moindre doute (le rapport doit le mentionner).

## 4. Résas en direct — format minimal

Pour les résas hors plateforme (Instagram, bouche-à-oreille), un petit tableau
suffit. Propose à l'hôte de le tenir tel quel (CSV ou tableau dicté que tu
convertis) :

```csv
arrivee,depart,voyageur,montant_hebergement,menage,canal
23/06/2026,25/06/2026,Pauline et Adrien,320,60,direct
```

Seules `arrivee`, `depart` et un montant sont obligatoires. `montant_hebergement`
= hors ménage ; si l'hôte ne connaît que le total, utiliser la colonne `montant`
et une colonne `menage`.

## 5. Format inconnu — le fallback manuel

Si le script rejette le fichier (colonnes introuvables) ou sort des avertissements
incompréhensibles :

1. Lis le fichier toi-même et reconstitue les résas (dates, montant, statut).
2. Applique les conventions de la doctrine **exactement** (ventilation à cheval,
   annulations, ménage, taxe).
3. Annonce en tête de rapport : **« chiffres établis par lecture manuelle de
   l'export — à vérifier »**, montre le détail par réservation et fais valider les
   totaux par l'hôte AVANT d'écrire l'historique.
4. Garde une trace : note dans l'historique (`notes`) que le mois est en lecture
   manuelle.

Un fichier illisible n'est jamais une impasse, c'est juste un mois où l'on est deux
fois plus transparent sur la méthode.

## Sources

Formats documentés à partir de : Airbnb Help Center — « Download your earnings »
(airbnb.com/help/article/3632, champs du rapport revenus : gross earnings, service
fees, cleaning fee, taxes) ; fils communautaires d'hôtes Airbnb sur l'export
réservations et ses formats de dates (community.withairbnb.com, airhostsforum.com) ;
documentation partenaires Booking.com sur les relevés de réservations
(partner.booking.com) et imports tiers (Guestbook 24/7, Little Hotelier) ; colonnes
équivalentes des exports PMS (help.hospitable.com — Reservations & Financials
Export). Relevé le 11/06/2026 — si une plateforme change ses colonnes, ajouter les
nouveaux intitulés dans `SYNONYMES` en tête de `scripts/parse_resas.py`.
