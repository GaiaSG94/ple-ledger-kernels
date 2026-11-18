# PLAN — ple-ledger-kernels (solo G)

Échéance : **05/01/2027** (heure exacte à vérifier sur l'onglet Timeline Kaggle). Départ 17/11/2026 → 7 semaines.
Budget réel : ~26 j-h de code (hors infra/figures/writeup, déjà réservés).

## Règles non négociables

- Repo public sous `GaiaSG94/`, licence **Apache-2.0** visible en About ; 1 seul commit final (code + `submission.yaml` + `artifacts/`).
- `artifacts/` décompressé ≤ 512 MiB, ≤ 10 000 fichiers, **pas de Git LFS ni symlinks**, généré par `uv run python eval/run.py`.
- `kit check` et `kit artifacts` verts **avant** chaque commit ; `serve` bind `0.0.0.0:$PORT` < 120 s ; install < 30 min ; `/opt/harness` ≤ 2 GiB compressé.
- Runtime 100 % local : ni web, ni clé API, ni modèle externe (le proxy fournit la clé d'évaluation).
- Zéro sortie codée en dur (disqualification) ; artefacts reproductibles ; seeds fixées.
- **Aucun code partagé avec ple-contract-proof** (rules §C.5d/§C.6a) : socle ré-implémenté.
- Un seul `model_api` sponsorisé par soumission → construire mono-modèle (`google-cloud/claude-opus-5-5` par défaut).

## Jalons

| Semaine | Dates | Contenu | Gate de sortie |
|---|---|---|---|
| S1 | 17–21/11 | **Spikes S1–S6** (voir plus bas) + squelette : `serve.py` minimal (bind + `done`), `submission.yaml`, `kit check` vert, repo créé, CI pr-pipeline | `kit check` vert sur un squelette qui répond `done` |
| S2 | 24–28/11 | **Campagne de mesure sur les 29 dev** : runner, journal tokens/CPU, taxonomie d'échecs manuelle ; premier **EXTRACT** (Callout Ledger sur PDF texte) + premier noyau (`beam-simple`) | **go/no-go** (IDEE.md §Métrique) : score moyen générique ≥ 0.10 |
| S3 | 1–5/12 | Noyaux `mna-ac`, `three-phase`, `cable-size`, `section-props` ; **AUDIT** (réseau de dimensions) ; SPEC en JSON + parsing tolérant | Audit : 0 violation d'unité non détectée sur les cas de référence |
| S4 | 8–12/12 | Noyaux `truss`, `frame-2d`, `buckling-euler`, `thermo-balance`, `fluid-network` ; chemin générique sympy/pint sandboxé (timeout 20 s) | 12 noyaux max ; chaque noyau avec tests golden + domaine de validité |
| S5 | 15–19/12 | **PROVE** (RoundTrip lite + linteur minimal) ; WRITE (rédacteur sur faits) ; DEADMAN/Warden/Tolerance ; FrontierKit-lite (journal → figures) | Trame `done`/`error` garantie sur 100 % des 29 dev |
| S6 | 22–26/12 | **Abalations chiffrées** (noyau off, audit off, ledger off) ; tableau multi-modèles (≥ 2 modèles sur 29 dev) ; figures 2 et 3 ; amorce du Writeup | Courbe score-vs-cost + failure breakdown produits |
| S7 | 29/12–2/1 | Génération `artifacts/` (`eval/run.py`), `kit artifacts` vert, commit final, README | Repo public, commit unique, artefacts < 512 MiB |
| S8 | 3–5/1 | Writeup ≤ 2000 mots (3 figures, 5 critères du rubric), relecture H, soumission Kaggle (Writeups tab : lien repo + SHA 40 car.) | Soumission avant deadline |

## Spikes S1–S6 (semaine 1, bloquants)

| Spike | Question | Décision selon la réponse |
|---|---|---|
| S1 | Le proxy fournit-il plusieurs modèles au runtime ? | Non → mono-modèle strict (défaut). Oui → ne pas construire de multi-modèles quand même (budget) |
| S2 | Part de PDF raster dans les 29 dev | > 30 % → prioriser OCR dans EXTRACT ; sinon PDF texte seulement |
| S3 | Part de tâches à livrable géométrique | > 40 % → passer en variante SpecForge (spec paramétrique → forge) |
| S4 | Part de tâches dépendant d'une table normative | Élever →/Ouvrir : ne pas builder de corpus normatif (illégal) ; utiliser les tables fournies |
| S5 | `kit`/`serve` démarre-t-il en < 120 s avec les wheels embarquées | Non → réduire les dépendances (OCC proscrit, numpy/pint/scipy seulement) |
| S6 | Les modèles faibles (gemma-4-26b, gpt-oss-120b) respectent-ils un JSON strict | Non → parsing tolérant + ré-émission explicite du schéma |

## Ordre de construction imposé

1. Infra (`serve.py`, `submission.yaml`, `kit check`, wheels, boot < 120 s) — **jamais** en dernier, sinon on n'a pas de harness pour tester.
2. Journal de mesure (tokens/CPU/retries) — sans lui, aucune ablation ni figure.
3. Boucle EXTRACT→SPEC→SOLVE→AUDIT minimale (1 noyau) sur les 29 dev.
4. Noyaux restants par couverture.
5. PROVE, WRITE, DEADMAN.
6. Ablations → figures → Writeup.

## Risques de planning

| Risque | Impact | Anticipation |
|---|---|---|
| Les 29 dev ne sont pas dans le repo public | tout le plan est bloqué | Semaine 1 : demander l'accès / vérifier `sample_submissions` du dépôt `google-research/ple` |
| Install > 30 min ou boot > 120 s | **zéro global** en Stage 2 | S5 spike ; wheels embarquées, imports paresseux |
| 12 noyaux ne couvrent pas assez | score moyen < 0.138 | chemin générique sympy comme filet ; ablations pour mesurer la couverture |
| Écriture volumineuse de solveurs | déborde le budget | 2 noyaux/semaine max ; un noyau = 1 formule + 1 test golden |
| Aucune présentation graphique | Stage 1 sous-noté | figures produites par le journal (FrontierKit-lite), pas à la main |
