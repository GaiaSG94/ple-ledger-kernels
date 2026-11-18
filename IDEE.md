# IDEE — ple-ledger-kernels (solo G)

Source : `../../IDEES-POOL/POOL-CLASSEMENT.md` (finaliste A) + `HACKATONS/criteres/physical-engineering-2026.md`.
Validation H : 2026-11-17. Statut : voir `STATUS.md`.

## Pitch (EN, 1 phrase)

An engineering agent harness in which the LLM never reads raw documents and never computes: it specifies, a deterministic kernel pack calculates with unit-aware checks, and every number written into the deliverable is audited dimension-by-dimension against typed facts extracted with provenance from the source drawings.

## Thèse

Les deux familles d'échec les plus lourdes du rubric — *misreading a drawing callout* et *unit errors* — et la moitié « scripts quantitatifs » du score Stage 2 se traitent par **substitution de code déterministe** : le LLM est mauvais en lecture fine de plans et en arithmétique d'ingénieur, excellent en spécification. Le coût bascule des tokens vers le CPU → position naturelle sur le front de Pareto (coût tokens ~10–40 k/tâche, le plus bas du pool).

## Architecture

```
tâche → EXTRACT (facts ledger typé + provenance) → SPEC (LLM émet un calcul typé)
      → SOLVE (8-12 noyaux déterministes pint/scipy, domaine de validité déclaré)
      → AUDIT (réseau de dimensions à 0 token, verdict UNKNOWN non bloquant)
      → PROVE (RoundTrip lite : re-mesure du livrable binaire par un 2e moteur)
      → WRITE (rédacteur qui ne peut publier que des faits du ledger)
      → DONE (contrat de terminaison, exactement une frame done/error)
```

### Briques (nom, source pool, périmètre)

1. **EXTRACT — Callout/Dimension Ledger** (pool 04/10) : runs de texte → faits `{id, grandeur, valeur, unité, page, bbox, type}` ; recoupement cote-texte vs longueur mesurée du segment (~1 %) ; PDF raster → OCR tesseract avec confiance par token ; verbatim de l'énoncé toujours fourni au LLM en parallèle (le ledger est un **augment**, jamais un remplacement).
2. **SPEC — trame JSON typée** : le LLM émet `{formule, grandeurs[ref fact], unité-cible, noyau}` ; tolérance de parsing stricte, re-prompt ciblé sur erreur (héritage Tolerance, pool 16).
3. **SOLVE — pack de 8 à 12 noyaux** (pool 14/13/05 amputé au budget) : candidats, par priorité de couverture Electrical+Mechanical (41/56 tâches) :
   - `beam-simple` : flexion/cisaillement/flèche poutre isostatique (formules fermées) ;
   - `frame-2d` : portique plan par matrice de rigidité (6 DOF/nœud, numpy dense) ;
   - `truss` : treillis 3 DOF ;
   - `section-props` : A, I, S, W, r via section-properties ou formules de profils courants ;
   - `buckling-euler` : λ critique, courbe A/B ;
   - `mna-ac` : analyse nodale complexe (circuits RLC, diviseurs, Thévenin) ;
   - `three-phase` : S/P/Q, cos φ, chute de tension ligne ;
   - `cable-size` : section = max(thermique, chute) sur tables locales d'ampacité (valeur + source citée) ;
   - `thermo-balance` : bilans Q·W=ΔH, rendement, Darcy-Weisbach/Colebrook ;
   - `fluid-network` : Hardy-Cross lite sur graphe simple.
   Chaque noyau : tests sur cas de référence publiés, domaine de validité déclaré, sortie SI canonique + unités explicites. **Pas de noyau au-delà de 12** : le reste des tâches passe par le chemin générique (SPEC → sympy/pint sandboxé → AUDIT).
4. **AUDIT — réseau de dimensions** (pool 02 DimType + 05 DimCheck + 14 UnitForge, fusionné) : chaque `{grandeur, valeur, unité}` du livrable vérifiée (dimension, plage plausible, cohérence inter-grandeurs) ; violation → réparation ciblée (réémettre la grandeur fautive) ; doute → `UNKNOWN`, jamais bloquant.
5. **PROVE — RoundTrip lite** (pool 10) : si un fichier géométrique est produit, re-lecture par un second parseur (ezdxf ↔ trimesh), mesures bbox/volume/entités, delta numérique renvoyé au LLM pour réparation ; linteur minimal (solide valide, échelle mm-vs-m).
6. **SOCLE** (ré-implémenté, zéro copie avec ple-contract-proof) : DoneGuard/Warden (frame `done`/`error` garantie, enveloppes temps, sentinelle anti-boucle), Tolerance (cascade de parsing), FrontierKit-lite (journal tokens/CPU → les 3 figures du Writeup en une commande).

### Hors périmètre (abandonnés et pourquoi)

- Tables de normes payantes (Eurocode/NEC) : corpus non légalement embarquable → les valeurs normatives utilisées viennent des tables **fournies avec la tâche** ou sont recalculées, source citée.
- `ShadowVerifier` : répliquer les verify.py publics lit comme « sortie codée en dur » → disqualification.
- >12 noyaux, portique 3D, fatigue, plastification : hors budget solo (~26 j-h de code après infra).

## Contrat de livrable

- Réponse structurée : `DATA` (faits du ledger, id cités) → `ASSUMPTIONS` (hypothèses affichées) → `METHOD` (noyau appelé, paramètres) → `RESULTS` (valeurs SI + unité + marge) → `LIMITS`. Une section par sous-question.
- Tout chiffre du rapport pointe vers un id de fait ou un résultat de noyau ; le rédacteur ne peut inventer.

## Protocole done/error

- Budget temps : enveloppes par phase (extract 15 %, solve 40 %, audit 10 %, rédaction 20 %, réserve 15 %) ; sentinelle anti-boucle (hash d'état) ; à T-12 min : finalisation forcée du meilleur artefact partiel + `done`.
- Toute exception → `error` avec diagnostic ; jamais de silence.

## Figures du Writeup (reproductibles via FrontierKit-lite)

1. **Architecture** : EXTRACT → SPEC → SOLVE → AUDIT → PROVE → WRITE.
2. **Score-vs-cost** : ablations `noyau off / audit off / ledger off` × budget tokens (plateau attendu : le coût est CPU).
3. **Failure breakdown** : taxonomie des échecs dev (cote mal typée, échelle, dimension incohérente, solide invalide, livrable manquant, timeout) avant/après chaque brique.

## Risques + repli

| Risque | Mitigation | Repli |
|---|---|---|
| Parseur de plans : faux positif qui contamine le ledger | recoupement géométrique + confiance par token + verbatim toujours fourni | mode « verbatim seul » (le ledger devient optionnel) |
| Noyau faux silencieusement | tests golden sur cas publiés, domaine de validité, double voie sympy sur écarts | noyau désactivé par feature-flag |
| 12 noyaux insuffisants sur les 56 cachées | chemin générique sympy/pint sandboxé pour tout le reste | accepter un score plus bas sur les familles non couvertes |
| sympy diverge | timeout 20 s + repli numérique | réponse partielle notée > 0 |
| Install/boot (OCC, scipy) > limites | wheels embarquées, imports paresseux, OCC proscrit au profit d'ezdxf/trimesh | noyaux purs Python (numpy/pint) uniquement |

## Pourquoi ça gagne (Stage 1)

Insight non évident et démontrable : « le LLM doit-il lire les plans ? Non — extraire des faits typés oui, lire non ». Ablations chiffrées sur les 29 dev, comparaison multi-modèles (le chemin textuel marche avec les 8 modèles, y compris text-only), courbe de coût dominée par le CPU, failure breakdown par familles. Racontable à un chercheur ML sans formation d'ingénieur.

## Métrique de go/no-go (fin semaine 2)

Score moyen du chemin générique seul sur les 29 dev ≥ 0.10, et ≥ 0.20 avec noyaux sur les familles couvertes ; sinon : réduire le périmètre aux noyaux `beam-simple`, `mna-ac`, `three-phase` + audit, et renforcer le chemin générique.
