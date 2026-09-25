# IBM Bob 2.0 Hackathon — submission draft

## Project title

**SiteCheck — a small, verifiable review loop for small websites**

## One-line description

SiteCheck turns a few observable website problems into a short, evidence-based correction
list, then runs the same checks again to prove what changed.

## The problem

Small website reviews often fail in one of two ways: they become long generic audits, or they
produce advice that is difficult to verify after the change. For a designer or independent
developer, the real question is simpler: what is broken, where is the evidence, what should
be fixed first, and did the correction actually work?

## The solution

SiteCheck is a deterministic, local Python tool with three focused checks:

1. images without alternative text;
2. form fields without an associated label;
3. internal links pointing to missing local files.

Each finding has a stable ID, severity, location, reproduction steps, evidence and a concrete
recommendation. A second command compares the before and after reports and separates fixed,
still-open and regressed findings.

## Why this workflow matters

The product does not pretend to replace a full accessibility or quality audit. It gives a
small team a reliable review loop. The same input produces the same result, and every claim
in the demo can be reproduced locally.

## Measured result

- Before: **3 findings**
- After the selected correction: **2 findings**
- Verified as fixed: **SC-002, missing form label**
- Still open by explicit prioritization: **SC-001 and SC-003**
- New regressions: **0**
- Automated tests: **42 passing**

## How IBM Bob 2.0 was used

IBM Bob supported three documented working sessions:

1. reading the kickoff brief and shaping an implementation plan;
2. implementing the deterministic MVP, report schema and tests;
3. adding the before/after recheck flow and comparison artifacts.

Athos Figueiredo made the product and editorial decisions: limiting the scope, selecting the
three checks, choosing SC-002 as the first correction, reviewing the generated code and
directing the visual language. Human review also caught a comparison-state issue that could
hide a newly introduced finding; it was corrected and covered by a dedicated test.

## What makes the submission personal

I work between design, communication and practical AI workflows. I wanted the result to feel
like a tool I would actually use: small enough to trust, clear enough to show a client or a
collaborator, and visually considered without hiding technical evidence. The report therefore
uses an editorial hierarchy instead of a generic dashboard, while remaining a single local
HTML file with no external assets.

## Technical overview

- Python 3.8+
- standard library only
- deterministic HTML parsing and local path checks
- JSON and self-contained HTML reports
- `unittest` test suite
- no login, telemetry, paid API or customer data

## Limitations

- The tool checks exactly three known patterns.
- It does not claim complete accessibility, security or website-quality coverage.
- Comparison uses stable finding IDs.
- The demo intentionally leaves two findings open to show prioritization and traceability.

## Run locally

```sh
python3 sitecheck.py demo-site/index.html --out-dir sitecheck-output/after
python3 recheck.py sitecheck-output/before/report.json sitecheck-output/after/report.json
python3 -m unittest discover test
```

## Submission assets

- Product screenshot: `docs/evidence/sitecheck-demo-designed.png`
- Before/after screenshot: `docs/evidence/sitecheck-comparison-designed.png`
- IBM Bob evidence: `docs/evidence/bob-session-01-planning.png`,
  `bob-session-02-implementation.png`, `bob-session-03-recheck.png`
- Demo script: `docs/DEMO-SCRIPT.md`

## Links to add before submission

- Public repository: `[ADD URL]`
- Demo video: `[ADD URL]`
- Team / participant profile: `[ADD URL]`
