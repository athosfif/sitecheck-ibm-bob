# September 26 verification update

The original IBM Bob sessions and narrated video remain historical evidence of the September 25 workflow (42 tests). Athos requested an independent corrective review with Codex on September 26. These later corrections are not represented as new Bob output.

## What changed

- Local URL resolution now separates queries/fragments, decodes filenames and ignores external schemes and protocol-relative URLs.
- Label detection covers wrapping labels, nonempty ARIA references, select/textarea and supported static fallback names.
- Before/after comparison preserves repeated instances instead of collapsing findings with the same rule ID. Mixed legacy/current reports retain a location fallback.
- Browser input is parsed in an inert template; supplied markup does not execute scripts or load remote assets. Original-source line positions replace a misleading line-1 fallback.
- The browser accepts project folders and non-HTML destinations, offers a page selector, and limits the automatic example fix to the unchanged sample.
- Mobile headings and result cards stay within the viewport.

## Evidence

- 71 Python tests passed: the original 42 plus 29 regression cases.
- 17 browser verification scenarios passed, including the shared-engine Figueira edition in all six translations and 390/768/1440 px layouts.
- A fresh execution still returns 3 findings before, 2 after, 1 fixed and 0 new regressions.
- The command `python3 tools/reproduce_demo.py` recreates that result without editing historical reports.

See `verification-20260926/` for raw test output and JSON/HTML reports. Browser verification uses actual Chrome interactions; microphone/voice features are not part of SiteCheck.

## Scope

Three focused static rule families, not a complete accessibility audit or site crawler. External URLs, root-relative server routes and pages with a base URL are not checked for missing local destinations. Local file existence does not establish HTTP availability. There is no measured productivity speedup or user study; no such result is claimed.
