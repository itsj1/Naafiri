# Naafiri

Mon compteur de calories perso, inspiré de Yazio : journal des repas, scan de codes-barres, macros, eau et poids.

C'est une PWA gratuite qui marche hors ligne, sans serveur, hébergée sur GitHub Pages : **https://itsj1.github.io/Naafiri**

Sur iPhone, ouvre le lien dans Safari, puis Partager → « Sur l'écran d'accueil ».

- Aliments génériques : table [CIQUAL 2025 de l'Anses](https://ciqual.anses.fr) (Licence Ouverte Etalab), fichier `ciqual.json` généré par `outils/ciqual.py`.
- Données produits : [Open Food Facts](https://world.openfoodfacts.org) (licence ODbL).
- Base facultative : [USDA FoodData Central](https://fdc.nal.usda.gov) (domaine public, clé gratuite à saisir dans les Réglages).
- Lecture des codes-barres : [ZXing](https://github.com/zxing-js/library) (`zxing.min.js`, licence Apache 2.0).
