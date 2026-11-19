# STATUS ple-ledger-kernels

Phase: idee
Etat: doing
Round: R1
Maj: 2026-11-17 00:00

## opencode
- 2026-11-19 (suite) : boucle SPEC->SOLVE->AUDIT branchee (harness/spec.py).
  Workspace : assert_facts (provenance obligatoire, batch tout-ou-rien, ids uniques),
  resolve (tout argument porteur d'unite doit citer un id de fait ; verification de
  dimension contre ARG_DIMS), compute (sorties numeriques enregistrees comme faits
  derives K<n>.<cle>, chainables), audit (faits + derives, bandes de plausibilite).
  serve.py expose desormais assert_facts / ledger / audit en plus de kernel et du
  socle bash/read/write ; prompt systeme mis a jour. Au passage : l'audit ne compare
  plus que les faits de meme kind (avant, deux quantites differentes declenchaient
  un faux VIOLATION des que kN/m etait enregistre). 37 tests pytest.
- 2026-11-19 : noyaux S3 ajoutes (section-props-rect/circle, mna-ac en MNA complexe
  pure Python, three-phase, cable-size) + catalog() ; tool `kernel` expose dans
  serve.py (le helper tool() reserve le parametre `name`, d'ou l'argument `kernel`).
  31 tests pytest verts. Reste S3 : boucle SPEC->SOLVE->AUDIT autour du ledger.
- 2026-11-17 : idee validee par H (finaliste A du pool 112, cf. ../IDEES-POOL/POOL-CLASSEMENT.md).
  IDEE.md + PLAN.md ecrits en relais opencode (Claude CLI non logge). Gate H avant build.
- Soumission : solo G. Repo a creer : github.com/GaiaSG94/ple-ledger-kernels (public + Apache-2.0).
- Kaggle : compte Gaia, 1 seule soumission (writeup + SHA). Deadline 05/01/2027 (heure ?).

## Claude
