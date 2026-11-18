# DESIGN — PLE Ledger Kernels (journal)

## V1 — 2026-11-18 · 3 directions pour la page principale (Writeup)

Brief : `PROMPT-DESIGN.md` du dépôt GitHub `GaiaSG94/ple-ledger-kernels`.
Écart demandé par Gaia : références prises dans la catégorie **`narratif-jeu`** de
`REFERENCES-DESIGN.md` V2 (10 captures), à la place de Santalarch + Baseten. Voir `G-DESIGN/REFS.md`.

Livré :
- `G-DESIGN/PAGES.md` (5 pages proposées, à valider)
- `G-DESIGN/REFS.md` (lecture des 10 captures `narratif-jeu`)
- `G-DESIGN/planches/v1/01-carnet-annote.html`
- `G-DESIGN/planches/v1/02-maquette-fenetre.html`
- `G-DESIGN/planches/v1/03-run-de-jeu.html` (s'écarte de la direction du brief : fond nuit)

Décisions communes aux 3 planches :
- Palette du brief tenue : encre `#101418`, gris `#5b6672`, teal `#0f766e` = chiffres validés uniquement, rouge `#b91c1c` = erreurs uniquement. Planche 03 : teal `#34c7b1` / rouge `#f26363` pour le fond nuit, retour aux hex du brief à l'impression.
- Polices système uniquement (serif de texte, linéale de titre, mono pour les valeurs), zéro réseau, zéro build.
- Desktop 1440 + feuille d'impression A4 dans chaque fichier.
- **Chiffres de résultats = démo**, signalés en tête de page et dans chaque légende de figure. Rien n'est encore mesuré (phase idée). Les catégories d'échec, les ablations, le seuil 0.138, les 29 tâches dev et l'exemple de poutre viennent de `IDEE.md` / `CRITERES.md`.

En attente : choix d'une direction par Gaia (étape B du brief), puis `STYLE.md` et déclinaison.

## V2 — 2026-11-18 · nouvelles refs : produit-dense + saas-marketing + 3D

Retour de Gaia sur la V1 : s'inspirer des catégories **produit-dense**, **saas-marketing** et
**3d-matiere** au lieu de `narratif-jeu`. V1 conservée telle quelle (`planches/v1/`).
Lecture des 31 captures : `G-DESIGN/REFS.md` § REFS V2.

Livré (`G-DESIGN/planches/v2/`) :
- `01-banc-isometrique.html` — clair. Baseten + Kivo : scène isométrique où la hauteur de chaque bloc = score dev-set de chaque configuration, carte titre qui chevauche, pastilles de faits flottantes, mur « testé sur ».
- `02-console-produit.html` — sombre. Parabola + Raycast + Framer : la Figure 1 devient un run d'agent (trajectoire cochée + canevas de nœuds), cartes par noyau.
- `03-cube-noyaux.html` — nuit puis page blanche. Noddal + Giallo + Noon + Teko : cube CSS 3D du pack de noyaux, faisceau teal, horizon qui ouvre sur le texte, figures en écrans éclairés.

Décisions : 3D uniquement en SVG / CSS (pas de Three.js, budget léger) ; mouvement coupé si
`prefers-reduced-motion` ; même contenu et mêmes chiffres de démo que la V1 ; impression A4 repasse en clair.
Écart au brief assumé : le brief disait « zéro hero » ; la demande « 3D » en implique un (planches 01 et 03).
Le run de la planche 02 (tâche 07, 1.4 k tokens, 3.1 s CPU) est un exemple de démo, comme les autres chiffres.

En attente : choix d'une direction par Gaia.

## V3 — 2026-11-18 · identité : Baseten (3D) + Psychoactive (couleur, lumière, textures)

Retour de Gaia sur la V2 : garder les modules 3D (barres, cube), s'inspirer de Baseten pour la 3D et
de Psychoactive pour couleurs / lumières / reflets / textures ; l'ensemble manquait d'identité visuelle.
Question de Gaia : « le livrable est-ce seulement un deck ? » → non (voir `G-DESIGN/PAGES.md`) :
Writeup Kaggle + README, l'identité ne passe que par les images.

Livré :
- `G-DESIGN/planches/v3/00-identite.html` — système : palette, 4 motifs (A glyphe 3×3, B bloc iso,
  C aurore, D repères/pastilles) avec leurs variantes, typo, application sur chaque surface, règles.
- `G-DESIGN/planches/v3/01-writeup.html` — le Writeup simulé dans une colonne neutre avec les 5 images.
- `G-DESIGN/tools/build_v3.py` — génère les deux pages ; chaque image est un SVG autonome (export PNG prévu).
- `PAGES.md` réécrit autour des surfaces réelles (bannière, 3 figures, module noyaux, README).

Décisions :
- Palette changée (demande de Gaia) : le teal du brief est remplacé par le vert aurore `#3df0a8`
  (`#0b8a5f` sur fond clair) comme seul accent = chiffre validé ; violet = matière ; corail = erreur ;
  magenta = lumière uniquement.
- Le cube devient un cube iso SVG (même famille que les barres, exportable) au lieu du CSS 3D de la V2.
- Glyphe de la brique retirée utilisé comme marqueur de données dans la Figure 2.

Connu, à corriger à la déclinaison : texte des figures à 11–14 px dans un fichier de 1200 px → trop petit
une fois réduit dans la colonne Kaggle ; viser ≥ 17 px. Chiffres toujours de démo.

## V4 — 2026-11-18 · lisibilité des figures + dosages de l'aurore

Retour de Gaia sur la V3 : « ajuster d'abord » → lisibilité des figures, couleurs / aurore.

Livré (`G-DESIGN/planches/v4/`, généré par `G-DESIGN/tools/build_v4.py`, V3 conservée) :
- `01-writeup.html` — les 5 images refaites : **aucun texte sous 18 px** dans un fichier de 1200 px
  (≈ 11.4 px une fois affiché à ~760 px). Le générateur échoue si une image descend sous ce seuil.
  Noms des barres écrits à la verticale sur la face gauche (Baseten) ; noms des étapes de la Figure 1
  sous les blocs ; légende de la Figure 2 sur deux lignes ; noms longs de la Figure 3 sur deux lignes ;
  pastilles de faits raccourcies.
- `02-compare-aurore.html` — même bannière + Figure 2 en trois dosages : A équilibrée (= V3), B sobre
  (fumée ×0.55, sans magenta, reflets et grain réduits), C intense (magenta ×2, second reflet, plus de grain).
- `00-identite.html` — mise à jour avec les nouvelles images ; règle de lisibilité marquée comme tenue.

Observé : en C, le titre chromé perd du contraste sur les zones magenta claires ; à surveiller si C est choisi.
En attente : choix du dosage A / B / C, puis STYLE.md et exports PNG.

## V4.1 — 2026-11-18 · style A validé, STYLE.md, README, exports

Gaia choisit le dosage **A · équilibrée**. Étape C du brief engagée.

Livré :
- `G-DESIGN/STYLE.md` — palette (hex + rôles), typo, formats, 4 composants et variantes, états, interdits.
- `planches/v4/03-readme.html` — README simulé (rendu GitHub) : bannière, glyphes inline, Fig. 1–3, tableau des étapes.
  Pas de badge « CI passing » (statut non vérifiable).
- `G-DESIGN/exports/v4/` — les 5 images en SVG et PNG 2× (2400 px), + 36 glyphes SVG (8 étapes + 10 noyaux, encre / aurore).
- `G-DESIGN/tools/export_png.sh` — rendu PNG par Firefox headless.

Statut : toutes les surfaces ont une planche, en revue. `/lock` seulement après validation de chacune.
Chiffres toujours de démo : à régénérer depuis le journal de `eval/run.py` (S6 du PLAN).
