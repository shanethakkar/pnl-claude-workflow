# Decision Log

Running, human-readable journal of decisions made while building the pnl-skill. Newest
entries at the top. Binding architectural decisions also get a formal numbered ADR in
`docs/adr/`; those are linked from here. Smaller calls live only here. See
[plan.md](plan.md) for current status and [CLAUDE.md](CLAUDE.md) for the working
agreement.

Format per entry: date, decision, why, and (if applicable) the ADR it maps to.

---

## 2026-06-10 Phase 8 decisions

### Skill zip is versioned in the filename and tracked in the repo
`tools/build_skill.py` produces `dist/pnl-labor-analysis-v0.1.0.zip`, excluding
`__pycache__` and compiled files, with `pnl-labor-analysis/` as the top-level folder. The
zip is committed so it can be downloaded directly from the repo and sent to interviewers.
Why: the deliverable is a portfolio artifact; a tracked, versioned zip makes install a clean
re-install on each update (SPEC.md section 13).

### sqlite3 egress fallback documented, not implemented
ADR-0002's fallback to standard-library sqlite3 (for when a sandbox blocks PyPI) is
described and listed in LIMITATIONS.md but not yet coded, because the dev environment
installs the deps cleanly and the only place egress might be blocked is the user's live
Cowork run.
Why: avoid building a contingency path that may never be needed; implement it only if the
live run actually hits blocked egress.

## 2026-06-10 Phase 2 decisions

### Skill scripts use flat imports; tests add scripts dir to sys.path
The Skill's scripts import each other flatly (`from schema import ...`) rather than as a
package. In the Cowork sandbox the model runs `pipeline.py` from the scripts directory,
which Python puts on `sys.path[0]`, so flat imports resolve with zero packaging. To keep
the Skill self-contained and dependency-free, we do not make it an installable package.
`tests/conftest.py` adds the scripts directory to `sys.path` so the dev-side tests can
import the same modules.
Why: the Skill must zip and run standalone in the sandbox with no install step beyond its
`requirements.txt`.

### Quarantine reasons are explicit and structural, with pandera as the final guard
`validate.py` runs explicit structural checks first (missing or unknown or duplicate line
codes, wrong section, non-positive or non-numeric amounts) so each quarantine reason names
the specific defect a non-technical user can act on. `TIDY_SCHEMA` runs last as the
authoritative type guard.
Why: a finance user needs a readable reason ("missing required line codes: LAB_ADMIN"),
not a raw schema traceback.

## 2026-06-10 Setup decisions

### Project name is "pnl-skill" for now, not LedgerLens
The spec uses `LedgerLens` as a placeholder. For this round (a portfolio piece for
interviewers) we keep the working name "pnl-skill". The skill identifier stays
`pnl-labor-analysis` as the spec requires. Consequently the pipeline output folder is
`_pnl_output`, not `_ledgerlens_output`.
Why: simpler, avoids a half-applied rebrand. User confirmed.

### Output folder name is `_pnl_output`
Neutral name following from dropping the LedgerLens brand. Lives inside the user's working
folder so results are visible, per spec section 8.
Why: results must land where the user can see them, not a temp path.

### pyproject is a non-packaged uv application (`tool.uv.package = false`)
First attempt used a hatchling build backend, which failed because it expected a buildable
package (README and a package dir). This project is scripts plus tools, not a distributable
library, so we run everything via `uv run` and skip the build backend.
Why: the project is an application and a Skill, not a pip-installable package.

### pandera installed with the `pandas` extra (`pandera[pandas]`)
pandera 0.31 split its backends. `import pandera` alone does not pull numpy/pandas, and the
DataFrameSchema validation API needs them. We depend on `pandera[pandas]`, which brings
pandas 3 and numpy 2.
Why: we need the pandas validation backend. Note: this does not violate the scale
guardrail. Validation runs per file on a single 9-row frame. The guardrail forbids loading
the whole portfolio into pandas at once, which we still never do (DuckDB handles the
portfolio-scale aggregation).

### Synthetic data (`data/synthetic/`) is gitignored; answer key is tracked
The 1200 generated CSVs are regenerated deterministically with seed 42, so committing them
would add noise without adding reproducibility. `data/answer_key.json` is tiny and stays
tracked so the seeded ground truth is visible.
Why: keep the repo clean and reproducible. The generator command is documented in README
and CLAUDE.md.

### Git over HTTPS via credential manager; no `gh` CLI
The GitHub CLI is not installed on this machine. git 2.53 with the system credential
manager handles authentication to `origin` over HTTPS. We do not require `gh` unless PR
automation is later wanted.
Why: tooling available on the machine; push access verified during setup.

### Cowork phases (7 live run and 8 install/recording) are owned by the user
The agent builds everything up to and including the Phase 7 dev-side eval (running the
Skill directly in Claude Code) and prepares the SOP and demo script. The actual Cowork
install and screen recording are done by the user, since they cannot be performed from
Claude Code.
Why: environment boundary. Confirmed with user.
