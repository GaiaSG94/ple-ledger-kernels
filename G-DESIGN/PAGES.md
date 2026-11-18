# PAGES — PLE Ledger Kernels (V4 — style A validé le 2026-11-18)

**Le livrable n'est pas un deck.** `CRITERES.md` : « livrables = Writeup Kaggle + repo GitHub », pas de vidéo ni de post.
Le texte du Writeup est mis en forme par Kaggle (non maîtrisé) et le README par GitHub : **l'identité
visuelle ne passe que par les images** insérées dans ces deux textes. Les surfaces à dessiner sont donc des images.

| # | Surface | Où elle apparaît | Contenu clé | Motifs (voir `planches/v4/00-identite.html`, règles dans `STYLE.md`) | Statut |
|---|---|---|---|---|---|
| 0 | **Bannière** (image d'ouverture) | haut du Writeup, haut du README | titre, 3 chiffres-clés, barres iso du score par configuration | aurore pleine · barres iso · glyphe LEDGER · chrome | en revue · `exports/v4/00-banner` |
| 1 | **Figure 1 — Architecture** (obligatoire) | Writeup §2, README | 7 blocs EXTRACT→DONE, SPEC seul appel LLM, ledger, boucle de réparation | aurore bande · blocs iso + glyphes · pastilles de faits | en revue · `01-fig-architecture` |
| 2 | **Figure 2 — Score vs coût** (obligatoire) | Writeup §4 | courbe budget, ablations marquées par le glyphe de la brique retirée, seuil 0.138 | aurore bande · glyphes marqueurs | en revue · `02-fig-score-vs-cost` |
| 3 | **Figure 3 — Échecs du dev-set** (obligatoire) | Writeup §5 | 6 familles, avant (fantôme) / après (corail), brique responsable | aurore bande · blocs fantômes · glyphes | en revue · `03-fig-failures` |
| 4 | **Module noyaux** (optionnel) | Writeup §3 ou README | cube iso du pack, 10 noyaux avec leur glyphe | aurore pleine · cube iso · variantes de glyphe | en revue · `04-kernel-pack` |
| 5 | **README** (texte GitHub) | repo | bande d'en-tête, glyphes inline, mêmes images | bannière + Fig. 1–3 · filet · glyphes inline | en revue · `planches/v4/03-readme.html` |
| — | Writeup (texte) | Kaggle | simulé dans `01-writeup.html` pour juger l'ensemble ; non stylable | — | référence |

Points à vérifier par Gaia :
- Largeur réelle de la colonne Kaggle et format d'image accepté (PNG conseillé : les filtres SVG ne passent pas partout).
- Kaggle propose-t-il une image de carte / vignette pour le Writeup ? Si oui, la bannière s'y décline.
- La Figure 1 inclut PROVE (IDEE.md) alors que le brief écrit EXTRACT → SPEC → SOLVE → AUDIT → WRITE.
