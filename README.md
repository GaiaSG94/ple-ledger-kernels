# ple-ledger-kernels

Harness entry for the [Physical-Engineering's Last Exam](https://www.kaggle.com/competitions/physical-engineerings-last-exam) competition (Google PLE): an engineering agent harness where **the LLM never reads raw documents and never computes** — it specifies. A typed fact ledger with provenance, a pack of unit-aware deterministic solver kernels, a zero-token dimensional audit, and an independent geometric re-measurement of anything the harness produces.

Status: in progress. The agent loop is the official `minimal` sample (Apache-2.0, Google LLC, vendored from `sample_submissions/minimal`) with one added `kernel` tool; the ledger/kernel architecture replaces it incrementally. Twelve deterministic kernels are implemented and tested (beams, sections, AC nodal analysis, three-phase, cable sizing, Euler buckling, sensible-heat balance, truss, plane frame, and linearized pipe networks). Kernel calls are ledger-bound: every unit-bearing argument must cite a fact with provenance, and each numeric output becomes a new auditable fact that later calls can cite. Deliverables are rendered from those facts through placeholders, and the `verify` tool reports any number in the text that the ledger cannot vouch for. See `../IDEE.md` and `../PLAN.md` in the project folder of our private pipeline for the roadmap.

## Layout

```
submission.yaml   entry manifest (name, model_api, install, serve)
serve.py          the harness: WebSocket server (minimal loop + ledger, kernel and audit tools)
taskbridge.py     session helper vendored from the official sample (Apache-2.0, Google LLC)
harness/          typed fact ledger, dimensional audit, deterministic solver kernels
  facts.py        Fact + Ledger (value, unit, provenance)
  dimensions.py   zero-token dimensional audit (OK / UNKNOWN / VIOLATION)
  spec.py         SPEC -> SOLVE -> AUDIT: cited facts in, derived facts out
  write.py        WRITE: markdown deliverable from {fid} placeholders + Sources table
  prove.py        PROVE: number-traceability lint against the ledger
  kernels.py      solver kernels, each with its domain of validity and a catalog()
tests/            pytest suite: golden cases per kernel, ledger and audit checks
requirements.txt  python deps for the serve container
artifacts/        produced by eval/run.py on the 29 public dev tasks (not committed yet)
```

## License

Apache-2.0. `serve.py` and `taskbridge.py` originate from the official
`google-research/ple` `sample_submissions/minimal` starter (Apache-2.0,
Copyright 2026 Google LLC) and retain their notices; all other code is
Copyright 2026 the repository owner, Apache-2.0.

## Independent entry

This harness is developed and submitted as an independent competition entry; it
shares no code with any other entry (competition rules §C.5d/§C.6a).
