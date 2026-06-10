# Limitations

Honest scope of this build, recorded as it was developed.

## Data

- The synthetic data is representative, not real GAAP hotel accounting. The line structure
  is simplified to a single revenue, labor, and other-expense layout with three lines each.
- Extraction assumes the canonical CSV layout in `docs/SPEC.md` section 6.1 and
  `skill/pnl-labor-analysis/references/extraction-schema.md`. Real P&Ls vary in format, so a
  layout-mapping step that normalizes diverse exports into this schema would be the first
  addition for production use.

## Method

- Outlier and trend detection use generic statistical rules (within-period z-score, an OLS
  slope per property, period-over-period delta). They are deliberately simple and auditable.
  They are not a forecasting model and do not attribute cause.
- The z-score uses the population standard deviation of all properties in a period. With a
  small number of properties per period, a single extreme value can move the mean and the
  spread, so z-scores should be read as a ranking signal, not an absolute probability.
- A property is compared only against its own history (slope, delta) and against its peers
  within the same period (z). There is no seasonality model beyond what the raw periods
  carry.

## Platform

- Cowork is desktop only, on paid plans. Scheduled runs happen only while the machine is
  awake with the app open.
- Cowork activity is not captured in audit logs or compliance APIs, so a regulated finance
  team would weigh that before using it on sensitive data. The synthetic demo data carries
  no such concern.
- Org-wide rollout relies on Team or Enterprise skill provisioning, where updates are
  manual, so the canonical Skill must be re-provisioned on each change.

## Dependencies

- The Skill needs `duckdb`, `pandera[pandas]`, `click`, and `pyarrow` at runtime. The Cowork
  sandbox installs these from PyPI on first use. If PyPI egress is blocked for the session,
  the aggregation step would need to fall back to the standard-library `sqlite3`. That
  fallback is documented in ADR-0002 but is not yet implemented in code; it would be the
  first change if a sandbox is found to block egress.
