# STATUS ple-ledger-kernels

Phase: idee
Etat: doing
Round: R1
Maj: 2026-11-17 00:00

## opencode
- 2026-11-19 (suite 4) : amorce S5. WRITE (harness/write.py) : rendu markdown a
  partir de placeholders {F1} / {K1.cle}, tableau Sources automatique, placeholder
  inconnu = erreur. PROVE (harness/prove.py) : extraction des nombres, tolerance
  relative 0,5 %, identifiants (F1, K1.x, S-101, 2D), titres markdown et tableau
  Sources ignores ; sortie = nombres non traçables + contexte. Outils serve
  `deliverable` et `verify` (9 outils au total), prompt systeme mis a jour.
  57 tests pytest verts, cablage verifie sur un livrable rendu (traçable) et sur
  un chiffre invente (118,2 kN.m signale). Reste : campagne 29 dev (dataset + proxy).
- 2026-11-19 (suite 3) : noyaux S4 ajoutes -> 12 noyaux au catalogue (plafond du PLAN).
  buckling-euler (Pcr + sigma_cr), thermo-balance (Q, T sortie, residu + balanced),
  truss (stiffness directe, forces axiale et reactions), frame-2d (3 ddl/noeud, efforts
  d'extremite, equilibre force/moment), fluid-network (mailles a resistance lineaire,
  injections, residu de continuite hors reservoirs). Tests golden : triangle a 7,5/-12,5 kN,
  cantilever 45 mm et 30 kN.m, Pcr 2193,25 kN, 501,6 kW, diviseur de pression 150 kPa.
  Boucle : arguments optionnels enfin facultatifs (mna-ac sans probe_nodes) et donnees
  structurees citables via {"fact": "F1"} (provenance remontee dans cited). 50 tests.
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
