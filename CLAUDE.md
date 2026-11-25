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
- État d'affichage : `TAB` (`jour` / `prog` / `prof`), `SUBV` (sous-page : `add`, `wth` historique des pesées, `my` mes aliments), `F` (feuille ou pop-up : `qty`, `qa`, `cf`, `prof`, `goal`, `wt`, `scan`, `cfg` réglages, `ask`), `CUR` (jour affiché `AAAA-MM-JJ`), `ADDM` (repas en cours d'ajout).
- Les champs des feuilles écrivent dans `F.d` via `data-fd=…` (sans re-rendu) ; les bulles de choix passent par `data-a=fset data-f=… data-v=…`.
- Sous-pages : `openSub()` + `history.pushState`, retour par `popstate` ; transitions `slide()` (View Transitions API, repli en animation de `#app`).
- Bandeaux « Annuler » : `toast(msg, undo)` dans `#toasts`, 4 s, 3 max.

## Données

- `localStorage['naafiri-v1']` → `S = { days, foods, wt, prof, del, cfg, sha }`.
- `days[AAAA-MM-JJ] = { e:[entrées], u }` (un ancien champ `w`, l’eau retirée, peut traîner : l’ignorer).
  - Entrée : `{ id, fid, n, b, m (b/l/d/s), q (grammes), un ('g' | 'p' portion), nb (nombre saisi), svn, k, p, c, f (pour 100 g, figés au moment de l'ajout), qa? (ajout rapide) }`.
- `foods[id]` : aliments utilisés, favoris et perso. `id` = `off:<code-barres>`, `g:<clé>` (aliments de base `GEN`) ou `my:<uid>`. Champs `n, b, k, p, c, f` (pour 100 g), `sv`/`svn` (portion), `su, sf, fi, sa` (sucres, saturés, fibres, sel), `img`, `ns` (Nutri-Score), `last` (récents), `fav`, `my`, `u`.
- `GEN` : table intégrée d'aliments de base (valeurs moyennes). **Ne jamais changer une clé existante** (elle sert d'id), ajouter à la fin.
- `wt[AAAA-MM-JJ] = { kg, u }` ; `prof = { sx, age, h, kg, gw (poids cible), act, obj, pace, kc (0 = auto), mac:{c,p,f} en %, u }` (ancien `wat` ignoré).
- Objectif calorique : Mifflin-St Jeor × activité, ± `pace` × 7 700 / 7 kcal par jour, minimum 1 200 (F) / 1 500 (H), arrondi à 10. Répartition par repas : 25 / 35 / 30 / 10 %.
- Un nouveau champ doit rester optionnel ; ne jamais renommer ni supprimer un champ sans migration.

## Sources

- **Open Food Facts** (sans clé) : recherche `cgi/search.pl` filtrée sur la France (limitée à ~10 requêtes/min : recherche après 700 ms de pause, résultats gardés dans `SC`), et code-barres `api/v2/product/<code>.json`. Mention ODbL obligatoire, présente en bas du Profil.
- Scan : `BarcodeDetector` natif si disponible (Android), sinon `zxing.min.js` ; saisie manuelle du code en secours.

## Synchro entre appareils

Fichier `naafiri-data.json` dans un **dépôt GitHub privé** via l'API Contents (même principe que MangaTime et Muscu), jeton fine-grained « Contents : Read and write ». Fusion par journée, par aliment et par pesée selon `u` ; suppressions datées dans `del.f` / `del.w` ; `prof` en bloc. Appeler `touch(obj)` après chaque modification. `cfg` (jeton) reste propre à chaque appareil.

## Écrans

- **Journal** : flèches + bandeau de la semaine (point violet = jour noté, rouge = objectif dépassé), anneau des calories restantes, barres glucides / protéines / lipides, quatre repas avec bouton +. Pas de suivi de l’eau (retiré à la demande de l’utilisateur).
- **Ajouter** : choix du repas, recherche (mes aliments → aliments de base → Open Food Facts), bouton scan, onglets Récents / Favoris / Mes aliments, « + » pour ajouter directement une portion, Ajout rapide, Créer un aliment.
- **Feuille quantité** : kcal et macros en direct, portion ou grammes, repas, favori (étoile), détail nutritionnel, Supprimer en modification.
- **Progrès** : poids actuel, évolution, série de jours ; courbe du poids avec objectif ; calories des 7 derniers jours ; macros moyennes.
- **Roue dentée en haut à droite** (Journal, Progrès, Profil, `gear()`) : feuille Réglages avec synchro GitHub, export / import JSON et crédits.
- **Profil** : profil, objectifs, mes aliments.

## Design

- Thème sombre ou clair automatique, accent **violet Naafiri** `#a43cf0` (`#b65cff` en sombre). Glucides ambre, protéines rose, lipides bleu.
- Toujours passer par les variables CSS de `:root` pour les couleurs.
- Mêmes composants que les autres projets : barre d'onglets en pilule flottante, cartes arrondies, feuilles par le bas (glisser pour fermer), réglages en cartes groupées, icônes SVG maison dans `IC` (en ajouter là plutôt qu'importer une librairie).
- Champs en 16 px (pas de zoom iOS), `inputmode=decimal` pour les chiffres, virgule acceptée.

## Façon de travailler

- L'utilisateur décrit ses demandes en français, souvent à l'oral : reformuler si ambigu, proposer des idées en plus.
- Tester dans Chrome headless (Playwright, vue iPhone, clair et sombre) avec des réponses d'Open Food Facts simulées, vérifier sur captures, puis **pousser directement sur `main`** (le site se met à jour seul).
- Ne jamais committer de jeton GitHub.
