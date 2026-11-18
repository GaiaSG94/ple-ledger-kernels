# REFS — PLE Ledger Kernels (V1, 2026-11-18)

> Base : `REFERENCES-DESIGN.md` V2 du hub, catégorie **`narratif-jeu`** (demande de Gaia :
> s'appuyer sur les refs design de la catégorie jeu / narratif jeu, à la place des 2 refs
> du brief Santalarch + Baseten).
> Les 10 refs ont été lues **en capture** (`REFERENCES-CAPTURES/narratif-jeu/`, commit
> `b7dba3d`, branche `design/temoignages-v1`). Les sites eux-mêmes n'ont pas été ouverts en
> direct pendant ce passage : les observations ci-dessous portent sur le premier écran capturé.
> On prend des **principes**, jamais un layout, un texte, un asset, un personnage ou une marque.

## Ce que chaque capture apprend

| Ref | Observé (capture 1440) | Principe retenu pour un Writeup de recherche |
|---|---|---|
| **Don't Look Up (jeu)** | Papier blanc cassé, titre noir énorme dessiné, foule de petits personnages au trait avec bulles (« hm », « yeah »), 2 boutons pilule à contour épais + ombre décalée pleine, cadre noir arrondi autour de tout l'écran. | **Annoter au trait** : des bulles et filets fins posés sur la figure disent ce qui se passe. Ombre décalée pleine = seul relief autorisé. |
| **Gemeos** | Crème granuleux, titre linéale grasse serrée, un mot encadré par une boîte de sélection (poignées bleues), stickers illustrés en marge, preuve chiffrée (« 4.9/5 ») collée au CTA. | **Le chiffre sélectionné** : encadrer la valeur auditée comme un objet sélectionné dans un éditeur ; preuve juste à côté de l'affirmation. |
| **Gapsy Studio** ★ | Lettres en relief rouges sur mur blanc 3D, griffonnages main (« WOW », flèche) par-dessus, « Scroll to Explore ». | Griffonnage par-dessus un rendu propre : la marge annotée du ledger. |
| **Raben Rifaie** ★ | Sable chaud monochrome, fenêtre ouverte sur un paysage, serif italique + linéale mêlées dans le titre, une seule pilule claire. | **La fenêtre** : chaque figure vit dans un cadre lumineux posé dans une page plus sombre ; serif italique pour la voix, linéale pour le fait. |
| **Dairy Food Bulgaria** | Île flottante en maquette 3D sur nuages, chemin qui serpente entre les bâtiments, produit posé comme une pièce. | **Le système comme maquette** : la chaîne EXTRACT→WRITE racontée comme un chemin qui traverse des stations. |
| **Matchball** | Titre linéale condensée noire, rangée d'objets alignés qui défilent, une consigne de jeu en 2 lignes, bouton noir rectangulaire. | **La rangée de spécimens** : les catégories d'échec alignées comme des objets à collectionner, chacun nommé. |
| **MemoryQuest** | Borne d'arcade dans le noir, halo magenta/bleu, écran CRT en tunnel. | Écarté en tant que style (cliché rétro, 3D coûteuse) ; retenu : **l'écran dans l'écran**, le noir qui fait briller une seule zone. |
| **Experience Funtech** | Scène néon nocturne 3D, personnage, barre d'outils flottante en bas avec onglets (Creator, Score…). | **La barre d'onglets flottante** : naviguer entre les 3 figures comme entre des modes de jeu. Néon écarté. |
| **Merci Studio** | Aplat rouge-corail, typo ronde grasse, arches 3D à contour coloré. | Écarté (aplat saturé + 3D décorative = contraire du ton papier de recherche). |
| **Sponge** | Créature 3D dans une fumée rouge-brun, boutons à contour pointillé. | **Contour pointillé = état provisoire** : réservé aux valeurs `UNKNOWN` de l'audit. |

## Les 3 familles de tokens qu'on en tire (une par direction)

1. **Carnet annoté** (Don't Look Up + Gemeos + Gapsy) : papier, encre, trait main, ombre décalée pleine.
2. **Maquette & fenêtre** (Dairy Food + Raben Rifaie + Matchball) : sable chaud, la chaîne comme chemin, figures encadrées dans une lumière.
3. **Run de jeu** (MemoryQuest + Funtech + Sponge) : fond nuit, une seule zone éclairée, barre d'onglets, pointillé pour l'incertain.

## Ce qu'on n'emprunte pas

- Aucun personnage, logo, titre, police propriétaire ou rendu 3D de ces sites.
- Pas de néon multicolore, pas de dégradé de fond, pas d'aplat saturé : le brief impose un accent unique (teal) et le rouge réservé aux erreurs.
- Polices : uniquement des familles système (Georgia / Charter, Helvetica / Arial Narrow, ui-monospace), aucune dépendance réseau.

## Refs du brief non utilisées

Santalarch et Baseten (brief §4) ne sont pas utilisées dans ce passage, sur demande de Gaia.

---

# REFS V2 — 2026-11-18 · produit-dense + saas-marketing + 3d-matiere

> Demande de Gaia après la V1 : « inspire-toi plutôt des catégories produit dense, saas
> marketing et 3D ». Les refs `narratif-jeu` ci-dessus sont abandonnées pour ce projet.
> 31 captures lues (`REFERENCES-CAPTURES/{produit-dense,saas-marketing,3d-matiere}/`,
> commit `b7dba3d`), premier écran seulement, sites non ouverts en direct.
> Budget léger : toute la 3D est en SVG isométrique ou en CSS 3D, sans Three.js.

## Refs retenues (et ce qu'on en prend)

| Ref | Cat. | Observé | Retenu |
|---|---|---|---|
| **Baseten** | produit-dense | Blocs isométriques verts sur un sol à damier pastel, chiffres posés sur les faces (« 28.6K », « 177 »), carte texte blanche qui chevauche la scène, mur de logos en grille. | **Planche 01** : la hauteur des blocs = le score ; la carte du titre chevauche la scène ; le mur de logos devient le mur « testé sur » (modèles, noyaux). |
| **Kivo** (kivoagentic) | saas-marketing | Objet central (sphère) entouré de petites pastilles flottantes (« Unit availability », « Floor plans »), fond crème, titre léger gris. | **Planche 01** : les pastilles flottantes = des faits du ledger (F-03, K-1, AUDIT, UNKNOWN). |
| **Trois Pas de Côté** | saas-marketing | Écran produit avec carte en isométrique + 2 chiffres clés (4.5 / 1.2M). | Confirme : 3D iso + chiffres-clés au même endroit. |
| **Parabola** | produit-dense | Volet de gauche = conversation d'agent avec liste de tâches cochées ; à droite = canevas de nœuds reliés ; bouton « Run flow » vert. | **Planche 02** : la Figure 1 devient un *run* réel — trajectoire à gauche, chaîne en nœuds à droite. |
| **Raycast** | produit-dense | Fond nuit, cartes d'extension (icône, titre, une ligne) en rangée. | **Planche 02** : une carte par noyau (beam-simple… fluid-network), avec domaine de validité. |
| **Framer (Agents)** | 3d-matiere | Champ de prompt lumineux dans le noir, une seule lueur bleue. | Planche 02 : un seul élément clair (le nœud SPEC = l'appel LLM). |
| **Noddal** | 3d-matiere | Cube de cubes lumineux traversé d'un faisceau vertical, titre léger « Built for compute. » | **Planche 03** : le pack de noyaux en cube CSS 3D, faisceau teal vertical. |
| **Giallo Studio** | 3d-matiere | « One window still lit » : une fenêtre claire posée dans une scène noire. | Planche 03 : chaque figure = un écran blanc dans un cadre noir. |
| **Noon** | 3d-matiere | Noir + une seule couleur d'accent, titre fin centré. | Planche 03 : titre linéale fine/grasse mêlées, un seul accent. |
| **Teko** | saas-marketing | Courbe colorée qui monte du bas comme un horizon, preuve sociale juste sous le CTA. | Planche 03 : horizon teal qui fait la transition nuit → page blanche ; les 4 chiffres de preuve posés juste au-dessus. |

## Refs regardées et écartées

Spectup, 5lab, Brainy, Concept Studio, Craft, Dovv, Dozfx, Genomines, Guillaume Zhu, Outseta,
The Way, Trendtrack, `-.png` (URL inconnue), Defy the Current, Igloo, Köm, Primal Instinct,
Psychoactive, Shutabug, Yogi Suria : dégradés saturés, personnages ou photos produit, néon,
3D réaliste coûteuse — contraires au ton « papier de recherche » ou hors budget.

## Ce qu'on n'emprunte pas

Aucun logo, texte, asset, couleur de marque (vert Baseten, bleu Framer, jaune Giallo). L'accent reste
le teal du brief, le rouge reste réservé aux erreurs.

---

# REFS V3 — 2026-11-18 · Baseten (3D) + Psychoactive (couleur, lumière, reflets, textures)

> Demande de Gaia : s'appuyer davantage sur Baseten pour la 3D (garder les barres et le cube) et
> sur Psychoactive pour les couleurs, lumières, reflets et textures ; donner une identité par des
> motifs récurrents avec variantes. Captures relues en pleine taille.

**Baseten** (`produit-dense/baseten.co.png`) — observé : volumes isométriques verts posés sur un sol à
bandes diagonales pastel ; texte et chiffres **imprimés sur les faces** (« 28.6k requests/min » avec une
courbe en pointillé sur la face, « REPLICAS 4/4 RUNNING », « 177 ms ») ; petites icônes en **pixels 3×3**
servant d'onglets ; carte texte blanche qui chevauche la scène ; grille de logos à cellules teintées.
→ retenu : motif B (bloc iso avec valeur sur la face droite, nom sur la face gauche, courbe sur la face),
motif A (glyphe 3×3), sol à bandes (version nuit).

**Psychoactive** (`3d-matiere/psychoactive.co.nz.png`) — observé : fumée indigo/violette, traînées
d'aurore vert-cyan et magenta, une large bande de lumière en diagonale, grain et lignes de balayage,
carte arrondie dont l'image déborde en halo flou autour, croix « + » sur l'axe médian, titre chromé
argent, chiffres mono (« 01:07 SEC »), bouton pilule blanc.
→ retenu : palette (nuit #08071c, violet #5b5bf0, lilas, aurore #3df0a8 comme seul accent, magenta en
lumière seulement), motif C (aurore : fumée + traînées + reflet + grain + trames, en filtres SVG),
motif D (cadre arrondi, croix « + », pastilles), titres chromés.
Halo débordant : retiré des images du Writeup (il salit le fond blanc de Kaggle), gardé en option sur fond sombre.

Ce qu'on n'emprunte pas : le vert Baseten, les logos de clients, le logo grenouille et le titre
« SUPER AI » de Psychoactive, la vidéo.
