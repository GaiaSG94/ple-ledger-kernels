# CRITERES - physical-engineering-2026 / 1st place / ple-ledger-kernels

Deadline submit : 2027-01-05
Soumission : solo moi
Depot : a confirmer
Statut : en cours

> Ce qu'il faut faire pour satisfaire les criteres dans le cadre de ce projet.
> Source des criteres : `../CRITERES.md`.

## Ce qu'il faut faire

- [ ] Compte Kaggle unique : interdiction de s'inscrire ou soumettre depuis plusieurs comptes ; 18 ans ou majorite legale ; exclus : Crimee, DNR/LNR, Cuba, Iran, Coree du Nord, sanctions OFAC (rules §A/C.1)
  - Action : _a completer_

- [ ] Equipe de 5 maximum, UNE seule soumission par equipe, fusions autorisees avant la deadline (rules §B.1/B.2) ; capacite du duo = 2 solos independants (G + B) = 2 soumissions
  - Action : _a completer_

- [ ] PAS de partage prive de code hors equipe (rules §C.5d et §C.6a) : les 2 solos doivent avoir des codebase independants ; le partage public sur les forums Kaggle est autorise
  - Action : _a completer_

- [ ] Licences gagnantes : Apache-2.0 ou MIT pour le harness/code, CC BY 4.0 pour le Writeup et la documentation ; licence visible en haut de la page About du repo (rules §B.5/§C.6b)
  - Action : _a completer_

- [ ] Donnees de competition : usage competition uniquement ; pas de transmission, duplication ou publication hors participants (rules §B.4) ; pas d'hand-labeling ni de prediction humaine des dev/test records (rules §C.4b)
  - Action : _a completer_

- [ ] Donnees externes, modeles et outils autorises s'ils sont publics et accessibles gratuitement a tous, ou conformes au Reasonableness Standard ; documenter les choix dans le Writeup (rules §B.6)
  - Action : _a completer_

- [ ] Donnees personnelles et confidentialite : W-9/W-8BEN et documents d'acceptation du prix a fournir si gagnant (rules §B.7/C.10)
  - Action : _a completer_

- [ ] Aucun post X / LinkedIn, ni video demo, ni formulaire externe exige : livrables = Writeup Kaggle + repo GitHub ; ne pas ajouter de livrable de confort
  - Action : _a completer_

- [ ] Heure exacte de fin : non publiee dans l'Overview ni les rules consultees (case vide dans le Sheet) — verifier l'onglet Timeline Kaggle
  - Action : _a completer_

- [ ] Note du Sheet 'solution 100 % IA interdite (regle YPF)' : aucune regle de ce nom retrouvee dans les sources officielles consultees le 16/11 — ne pas en deduire une contrainte, a verifier aupres de l'organisateur ; l'exigence documentee est un HARNESS code (outils, solveurs, verification, reproductibilite), pas une reponse LLM directe
  - Action : _a completer_

## A reconsidérer plus tard

- Writeup Kaggle de 2000 mots MAXIMUM couvrant les 5 criteres du rubric (100 points) et contenant 3 figures OBLIGATOIRES : architecture diagram, score-vs-cost plot, dev-set failure breakdown ; un brouillon non soumis n'est pas juge
- 1. Insight & Failure Analysis (25 pts) : vrais echecs du dev-set (mauvaise lecture d'un callout de dessin, mauvais article de code, erreurs d'unites, arret premature), ablations controlees, idees qui ont echoue
- 2. Engineering Reasoning (25 pts) : comparer la trajectoire de l'agent au workflow d'un ingenieur license sur une tache concrete ; montrer ou le raisonnement tient et ou il prend des raccourcis (lecture CAD/PDF, tables de normes, solvers)
- 3. Cross-Model Generalizability (15 pts) : tester les 29 taches publiques de dev avec AU MOINS 2 modeles (dont un modele local open-weight ou une API personnelle), tableau comparatif accuracy/cout en tokens dans le Writeup
- 4. Efficiency & Scaling (20 pts) : tracer le score du dev-set contre le budget de calcul (appels, tokens, runtime, verification parallele) ; marquer le plateau et estimer le potentiel restant
- 5. Clarity & Visuals (15 pts) : ecrire pour un chercheur ML sans formation genie civil/mecanique/electrique ; finding principal en haut ; 3 figures ; rester sous 2000 mots
- Repo GitHub lie sous Project Links + commit SHA de 40 caracteres (git rev-parse HEAD) en haut du Writeup ; repo public a la cloture (si prive pendant la competition, installer le GitHub App ple-submission)
- Racine du repo : submission.yaml, serve.py / harness.py, licence Apache-2.0 ou MIT, dossier artifacts/ DECOMPRESSE (≤ 512 MiB, ≤ 10 000 fichiers, sans Git LFS ni symlinks) genere par uv run python eval/run.py
- uv run python -m kit check ET uv run python -m kit artifacts (PLE Competition Kit) doivent passer avant soumission
- model_api dans submission.yaml = un des 8 modeles officiels google-cloud/<id> pour Stage 2 ; changer model_api apres avoir genere les artifacts avec un modele local/perso est autorise (documenter) ; appels LLM-judge payants non requis en dev local
- Top 100 du Stage 1 seulement accede au Stage 2 ; verifications automatiques avant scoring ; pre-screening possible sur un petit sous-ensemble de taches cachees
- 56 taches cachees : 6 Structural, 9 Civil, 18 Electrical, 23 Mechanical ; 3 runs independants par finaliste = 168 task runs ; score moyen 0.0-1.0 et cout moyen ; classement sur le front de Pareto performance/cout
- Seuil : score moyen Stage 2 ≥ 0.138 pour entrer dans le front de Pareto et les prix ; classement final par score moyen parmi les finalistes du front ; departage : score Writeup Stage 1, puis horodatage de soumission Kaggle
- Evaluation : clone du commit, install une fois dans un container debian:bookworm (timeout 30 min, /opt/harness ≤ 2 Gio compresse), smoke test (serve ecoute sur 0.0.0.0:$PORT en 120 s, ecrit un fichier test, envoie done)
- Chaque tache : container isole 2 CPU / 4 Go RAM, /opt/harness en lecture seule, /tmp et $HOME accessibles en ecriture (1 Go), limite 6 HEURES par tache, protocole WebSocket
- Verification : scripts quantitatifs, geometries CAD/IFC et contraintes ; juge LLM Claude Opus 5.5 pour les livrables ouverts (0.0 a 1.0) ; une tache ungraded ou timeout sans trame done/error compte 0.0
- Reproductibilite : les artifacts soumis sont re-scores sur les 29 taches dev publiques et un echantillon aleatoire est re-joue en live ; toute sortie code en dur = disqualification
- Pendant le Stage 2, le proxy d'evaluation bloque les cles API custom (.env), les serveurs de modeles externes et la recherche web ; la cle d'evaluation Google est fournie gratuitement
- Requetes invalides (HTTP 400), crashes et timeouts non recuperes comptent contre le score ; fautes de l'evaluateur et limites de debits des endpoints sponsor retentees automatiquement sans penalite
- Modeles sponsorises (8 identifiants model_api) : google-cloud/gemini-4-argon, gemini-3.8-flash, gemini-3.1-pro-preview, gemma-4-26b, claude-opus-5-5, gpt-oss-120b, glm-5.2, llama-4-maverick
- Cloner google-research/ple + demarrer depuis physical-engineerings-last-exam/submission-template (ou sample_submissions/pi-opus, hermes-opus, agy-gemini)
- Valider : uv run python -m kit check, generer les dev outputs avec uv run python eval/run.py, verifier avec uv run python -m kit artifacts
- Commiter code + submission.yaml + artifacts en UN seul commit (git add -A && git commit -m 'PLE harness submission') et pousser sur GitHub
- Sur Kaggle : onglet Writeups > New Writeup, coller le lien du repo sous Project Links, mettre le SHA de 40 caracteres en haut, cliquer Submit
- Les inscriptions directes sur ple-bench.com sont FERMEES : toutes les soumissions officielles passent par les Kaggle Writeups
