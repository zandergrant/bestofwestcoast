# Repository development instructions


## Build validation and delivery standard

- Treat related changes as one coherent batch; stage them together and push one validated commit where practical. Avoid incremental remote pushes as a substitute for local iteration.
- Before pushing, use the repository's pinned toolchain and lockfile. Inspect package scripts and CI; run available lint, typecheck, tests and production build locally (or in an authorized isolated runner). Update affected regression tests in the same batch as code, schema or branding changes.
- If local execution is unavailable, explicitly state that limitation, push a coherent batch to a non-production branch, and use CI and preview checks for verification. Do not claim unexecuted checks passed.
- Verify GitHub checks and Vercel preview for the exact final commit. If a check fails, inspect the actual logs, fix the root cause, and revalidate. Do not disable, bypass or weaken tests merely to obtain a green result.
- Do not report work complete while required checks are failing or pending. Report the commit, check results, preview status and any remaining configuration or integration blockers. Distinguish successful builds from functional readiness.
- Do not merge, promote, deploy to production, change secrets or run production migrations without authorization. Keep production alerts and existing safety gates intact.
