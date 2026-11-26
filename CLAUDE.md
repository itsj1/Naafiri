# Naafiri — notes pour Claude

App personnelle (un seul utilisateur) pour **compter les calories**, inspirée de **Yazio** : journal des repas, macros, poids, objectifs. Même architecture que mes PWA **MangaTime** (`itsj1/MangaTime`) et **Muscu** (`itsj1/FitnessTracker`).

- En ligne : https://itsj1.github.io/Naafiri (GitHub Pages, branche `main`).
- Tout doit rester **gratuit** : pas de serveur, pas de service payant.
- Langue de l'interface, des commentaires et des messages de commit : **français**, avec tutoiement et apostrophes typographiques (’).

## Architecture

- PWA en **un seul fichier `index.html`** (CSS + JS inline, sans framework ni build), plus `sw.js`, `manifest.json`, les icônes et `zxing.min.js`.
- Code **compact** comme les autres projets (noms courts `S`, `F`, `$`, `esc`, `uid`, une fonction par ligne, template literals) : ne pas reformater.
- `sw.js` : réseau d'abord, cache en secours après 3 s. **Incrémenter `CACHE` (`naafiri-vN`) à chaque version publiée.** Il n'intercepte que les fichiers du site (jamais Open Food Facts ni `api.github.com`).
- `zxing.min.js` : `@zxing/library` 0.21.3 (UMD, licence Apache 2.0), chargé seulement au premier scan quand le navigateur n'a pas `BarcodeDetector` (iPhone). Ne pas le modifier.
- **La page ne défile pas** : `main#app` est fixé plein écran et c'est lui qui défile (le rebond d'iOS ne bouge pas la barre d'onglets).
- Rendu : `render()` reconstruit `#app` (vue) et `#dlg` (feuille ouverte) en `innerHTML` ; toutes les actions passent par `data-a=…` dans un seul écouteur de clic. Toujours échapper le texte avec `esc()`.
- Onglets dans l’ordre **Progrès · Journal · Profil** (Journal au milieu, ouvert au démarrage).
- État d'affichage : `TAB` (`jour` / `prog` / `prof`), `SUBV` (sous-page : `add`, `meal` aliments du repas `ADDM`, `nut` détail nutritionnel du jour ou d’un repas `NUTM` ('all' ou b/l/d/s), `wth` historique des pesées, `my` mes aliments ; pile `SST` pour revenir à la sous-page précédente), `F` (feuille ou pop-up : `qty`, `qa`, `cf`, `prof`, `goal`, `wt`, `scan`, `cfg` réglages, `ask`), `CUR` (jour affiché `AAAA-MM-JJ`), `ADDM` (repas en cours d'ajout).
- Les champs des feuilles écrivent dans `F.d` via `data-fd=…` (sans re-rendu) ; les bulles de choix passent par `data-a=fset data-f=… data-v=…`.
- Sous-pages : `openSub()` + `history.pushState`, retour par `popstate` ; transitions `slide()` (View Transitions API, repli en animation de `#app`).
- Bandeaux « Annuler » : `toast(msg, undo)` dans `#toasts`, 4 s, 3 max.
- Gestes horizontaux (`HZ`) : ligne d’aliment `.sw` glissée vers la gauche → poubelle (`edel`, `delEntry()`) ; bulle du jour `#sumc` glissée → jour précédent / suivant. Le clic qui suit un glissé est ignoré (`NOCL`).
- `localStorage['naafiri-ui']` (`UI`, propre à l’appareil, non synchronisé) : repas dépliés dans le Journal (`UI.o[m]`).

## Données

- `localStorage['naafiri-v1']` → `S = { days, foods, wt, prof, del, cfg, sha }`.
- `days[AAAA-MM-JJ] = { e:[entrées], u }` (un ancien champ `w`, l’eau retirée, peut traîner : l’ignorer).
  - Entrée : `{ id, fid, n, b, m (b/l/d/s), q (grammes), un (unité : 'g', 'kg', 'ml', 'l', ou portion 'p' / 'p1', 'p2'… / 'pk' paquet), nb (nombre saisi dans cette unité), svn (nom de la portion), k, p, c, f (pour 100 g, figés au moment de l'ajout), qa? (ajout rapide) }`.
- `foods[id]` : aliments utilisés, favoris et perso. `id` = `off:<code-barres>`, `g:<clé>` (aliments de base `GEN`) ou `my:<uid>`. Champs `n, b, k, p, c, f` (pour 100 g), `sv`/`svn` (portion principale), `ps` (portions en plus `[[nom, g]]`, table `GENP` pour les aliments de base), `pk` (poids du paquet, Open Food Facts), `nu` (tous les nutriments détaillés connus, pour 100 g, en grammes, clés Open Food Facts listées dans `NUTS` ; alcool converti de % vol en g), `su, sf, fi, sa` (anciens champs sucres, saturés, fibres, sel, encore lus par `nv()`), `img`, `ns` (Nutri-Score), `last` (récents), `lq` (dernière quantité utilisée `{un, nb}`, proposée par défaut la fois suivante via `defQ()`, aussi pour le « + » direct ; sans `lq`, la feuille s’ouvre **en grammes** : poids d’une portion, sinon 100 g), `fav`, `my`, `u`.
- `GEN` : table intégrée d'aliments de base (valeurs moyennes). **Ne jamais changer une clé existante** (elle sert d'id), ajouter à la fin.
- `wt[AAAA-MM-JJ] = { kg, u }` ; `prof = { sx, age, h, kg, gw (poids cible), act, obj, pace, kc (0 = auto), mac:{c,p,f} en %, u }` (ancien `wat` ignoré).
- Objectif calorique : Mifflin-St Jeor × activité, ± `pace` × 7 700 / 7 kcal par jour, minimum 1 200 (F) / 1 500 (H), arrondi à 10. Répartition par repas : 25 / 35 / 30 / 10 %.
- Un nouveau champ doit rester optionnel ; ne jamais renommer ni supprimer un champ sans migration.

## Sources

- **Open Food Facts** (sans clé) : recherche `cgi/search.pl` filtrée sur la France (limitée à ~10 requêtes/min : recherche après 700 ms de pause, résultats gardés dans `SC`), et code-barres `api/v2/product/<code>.json`. Mention ODbL obligatoire, présente dans la feuille Réglages.
- Scan : `BarcodeDetector` natif si disponible (Android), sinon `zxing.min.js` ; saisie manuelle du code en secours.

## Synchro entre appareils

Fichier `naafiri-data.json` dans un **dépôt GitHub privé** via l'API Contents (même principe que MangaTime et Muscu), jeton fine-grained « Contents : Read and write ». Fusion par journée, par aliment et par pesée selon `u` ; suppressions datées dans `del.f` / `del.w` ; `prof` en bloc. Appeler `touch(obj)` après chaque modification. `cfg` (jeton) reste propre à chaque appareil.

## Écrans

- **Journal** : flèches + bandeau de la semaine (point violet = jour noté, rouge = objectif dépassé), bulle avec anneau des calories restantes et barres glucides / protéines / lipides (glisser à gauche / droite = jour suivant / précédent), quatre repas avec bouton + et flèche pour déplier / replier leurs aliments (repliés par défaut). Pas de suivi de l’eau (retiré à la demande de l’utilisateur).
- **Ajouter** : choix du repas, rond en haut à droite avec le nombre d’aliments de ce repas (ouvre la page `meal` : liste, glisser pour supprimer), recherche (mes aliments → aliments de base → Open Food Facts), bouton scan, bulles Récents / Favoris / Mes aliments de même largeur, « + » pour ajouter directement une portion (coche violette si l’aliment est déjà dans le repas choisi), Ajout rapide, Créer un aliment.
- **Feuille quantité** : kcal, macros et tableau nutritionnel mis à jour en direct (`paintQty()`) ; **deux roulettes** façon iOS côte à côte : quantité (`#wh`, `whVals()` selon l’unité : g / mL **de 1 en 1** jusqu’à 1 000 puis de 10 en 10, deux colonnes centrées et bien espacées, chacune avec son propre rectangle violet `.whb` autour de la valeur choisie) et unité (`#whu` : portions de l’aliment, puis g / kg / mL / L, 1 mL compté comme 1 g, `units()`, `setUnit()` garde le poids) ; défilement aimanté, valeur au centre = valeur choisie ; la feuille ne se ferme pas en les faisant tourner. Pas de bulles de raccourcis ni d’unités (retirées à la demande de l’utilisateur) ; bouton Ajouter juste sous les roulettes, puis plusieurs repas cochables à la fois (`F.ms`, ajout simultané ; en modification l’entrée garde son id dans son repas s’il reste coché) ; favori (étoile), Supprimer en modification.
- **Détail nutritionnel** (page `nut`, comme Yazio) : Calories, Protéines, Glucides (fibres, sucre, sucres ajoutés), Matières grasses (saturées, mono, poly, trans), Autre (alcool, cholestérol, eau, sel, sodium), Vitamines, Minéraux ; « - » si aucun aliment ne donne la valeur. Ouvert par une flèche en bas de la bulle du jour, en bas d’un repas déplié et dans la page du repas. La feuille quantité a aussi « Tout le détail » (`F.full`) : le bouton reste au même endroit, au-dessus du tableau, et seule sa flèche tourne.
- **Progrès** : poids actuel, évolution, série de jours ; courbe du poids avec objectif ; calories des 7 derniers jours ; macros moyennes.
- **Roue dentée en haut à droite** (Journal, Progrès, Profil, `gear()`) : feuille Réglages avec synchro GitHub, export / import JSON et crédits.
- **Profil** : profil, objectifs, mes aliments.

## Design

- Thème sombre ou clair automatique, accent **violet Naafiri** `#a43cf0` (`#b65cff` en sombre). Le thème sombre est volontairement assez clair (fond `#241e2b`, cartes `#302839`) : l’utilisateur trouvait l’ancien trop sombre. Glucides ambre, protéines rose, lipides bleu.
- Toujours passer par les variables CSS de `:root` pour les couleurs.
- Mêmes composants que les autres projets : barre d'onglets en pilule flottante, cartes arrondies, feuilles par le bas (glisser pour fermer), réglages en cartes groupées, icônes SVG maison dans `IC` (en ajouter là plutôt qu'importer une librairie).
- Champs en 16 px (pas de zoom iOS), `inputmode=decimal` pour les chiffres, virgule acceptée.

## Façon de travailler

- L'utilisateur décrit ses demandes en français, souvent à l'oral : reformuler si ambigu, proposer des idées en plus.
- Tester dans Chrome headless (Playwright, vue iPhone, clair et sombre) avec des réponses d'Open Food Facts simulées, vérifier sur captures, puis **pousser directement sur `main`** (le site se met à jour seul).
- Ne jamais committer de jeton GitHub.
