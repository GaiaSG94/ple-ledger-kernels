# STYLE — PLE Ledger Kernels (V4, dosage A, validé par Gaia le 2026-11-18)

Source de vérité exécutable : `G-DESIGN/tools/build_v4.py` (toutes les valeurs ci-dessous y sont des constantes).
Planche de référence : `planches/v4/00-identite.html`.

## 0. Où vit le style

Le livrable = Writeup Kaggle + README GitHub (pas de deck). Leurs textes sont mis en forme par Kaggle et GitHub.
**Le style ne s'applique qu'aux images** (bannière, 3 figures, module noyaux) et aux glyphes SVG insérés dans le README.

## 1. Palette

| Token | Hex | Rôle | Règle |
|---|---|---|---|
| `VOID` nuit | `#08071c` | fond de toutes les images | — |
| `INDIGO` | `#151340` | panneau du graphe (Fig. 2) | — |
| `VIOLET` | `#5b5bf0` | matière : fumée, nœud SPEC | jamais pour un chiffre |
| `LILAC` | `#a9a6ff` | texte secondaire sur nuit, ablations | — |
| `AUR` aurore | `#3df0a8` | **seul accent** : chiffre validé, harness complet, brique qui corrige | sur fond clair : `#0b8a5f` |
| `ERR` corail | `#ff5c7a` | erreur, LLM seul, échecs restants | sur fond clair : `#c42a45` ; jamais en décor |
| `MAG` magenta | `#e14bd6` | lumière uniquement (fumée, traînée) | jamais en texte, trait ou donnée |
| `PAPER` | `#f6f5fc` | README, impression | — |
| `INK` | `#0f0e26` | texte sur clair, glyphes inline | — |

Blocs iso (dessus / gauche / droite) : verre `#3b3894 / #2a2774 / #1c1a56`, validé `#8cf8cf / #33d996 / #17a571`,
erreur `#ff9cae / #e4496b / #b5304f`, SPEC `#8d8cff / #5b5bf0 / #3f3fc4`.

## 2. Typographie (polices système, zéro réseau)

| Usage | Famille | Taille dans l'image 1200 px |
|---|---|---|
| Titre bannière | Helvetica Neue / Arial 600, approche −2.4, dégradé chrome | 64 |
| Chiffres-clés | ui-monospace 600 | 44 |
| Sous-titre | linéale | 23 |
| Titres de module | linéale 600 | 34 |
| Étiquettes, axes, légendes, valeurs | mono ou linéale | **18 minimum** |

**Règle de lisibilité (vérifiée à la génération)** : aucun texte < 18 px dans un fichier de 1200 px → ≥ 11.4 px
affiché dans une colonne de ~760 px (largeur Kaggle à vérifier). `build_v4.py` échoue sinon.

## 3. Formats

- Images : 1200 px de large (hauteurs 500–620), coins arrondis 26 px, export **PNG 2×** (2400 px) + SVG.
- Fichiers : `exports/v4/00-banner`, `01-fig-architecture`, `02-fig-score-vs-cost`, `03-fig-failures`, `04-kernel-pack`.
- Glyphes inline README : `exports/v4/glyphs/<nom>-ink.svg` et `-aurora.svg`, 20 px.

## 4. Composants (les 4 motifs)

**A · Glyphe 3×3** — 9 cases, cellule 1, espace 0.18, rayon 0.12.
EXTRACT `111000111` · SPEC `000010000` · SOLVE `010111010` · AUDIT `101010101` · PROVE `111101111` ·
WRITE `100110111` · DONE `111111111` · LEDGER `101101101`. Dix variantes pour les noyaux (voir `KERNELS`).
Emplois : titre de section (Writeup, README), étiquette de module, dessus des blocs, **marqueur de donnée**
(Fig. 2 : le point d'une ablation porte le glyphe de la brique retirée ; Fig. 3 : la brique qui a supprimé l'échec).

**B · Bloc isométrique** — projection 30°, arête claire 55 %, bande de reflet 10 % sur la face avant.
Nom sur la face gauche (vertical si la barre est haute), valeur sur la face droite, glyphe sur le dessus.
Variantes : barre de score (hauteur = valeur), barre d'ablation (verre), bloc fantôme (pointillé lilas = avant),
bloc erreur (corail = restant), tuile de fait (blanche, à plat), cube de noyaux (3×3×3).
Sol : tuiles nuit à bandes diagonales, quelques tuiles teintées à 32 %.

**C · Aurore (dosage A)** — fumée (ellipses violettes déplacées par bruit, flou 22), traînée aurore 55 %,
traînée magenta 45 % (pleine seulement), bande de reflet diagonale 4.5 %, grain 9 %, trames 3.5 %.
Variantes : *pleine* (bannière, module noyaux — une seule par surface), *bande* (figures), *filet* (séparateur README).

**D · Repères et provenance** — cadre arrondi, liseré blanc 12 %, trois croix « + » (gauche, droite, bas),
étiquette glyphe + TITRE en mono haut-gauche, légende courte haut-droite. Pastilles de faits : blanches, point
aurore, texte mono 18 (`F-03 · 6 000 mm · S-101 p.2`).

## 5. États

| État | Rendu |
|---|---|
| Chiffre validé (ledger) | aurore ; bloc validé ; pastille pleine |
| Erreur / LLM seul | corail ; bloc erreur ; valeur barrée dans les tableaux |
| UNKNOWN | contour pointillé lilas, jamais de couleur pleine |
| Ablation | verre violet + glyphe de la brique retirée |
| Avant (référence) | bloc fantôme pointillé |

## 6. Mouvement

Aucun dans les images (PNG). Les planches HTML n'animent rien de porteur de sens.

## 7. Interdits

Couleur d'accent autre que l'aurore ; magenta sur une donnée ; bloc iso sans chiffre ni glyphe ; aurore pleine
deux fois sur la même surface ; texte < 18 px dans une image ; chiffres non marqués « demo » tant que
`eval/run.py` n'a pas tourné ; badge ou statut non vérifié dans le README.
