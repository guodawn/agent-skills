---
name: deploy-uniagent-apps
description: Build and deploy the UniAgent Apps HTTPS stack, including required Atlas migration gates for Operations and Studio backend releases.
---

# Deploy UniAgent Apps

Deploy the UniAgent Studio, Portal, Account, Operations, and IAM application stack from reviewed local source to an SSH target. Treat the remote `.env.apps` as protected deployment state and publish immutable image digests only.

Resolve source repositories by release role, not by checkout name or sibling layout. Set only the required roots (`STUDIO_SOURCE_DIR`, `FRONTEND_SOURCE_DIR`, `DESIGN_SOURCE_DIR`, `OPS_SOURCE_DIR`, `IAM_SOURCE_DIR`), normalize each with `git -C "$DIR" rev-parse --show-toplevel`, and verify the selected build entrypoint beneath it. If a role is ambiguous, request its source path or release artifact rather than guessing.

Lock every source role to an immutable commit before inspecting or building. By default, fetch `origin` and use `origin/main` at that time. `SOURCE_REF` selects a release-wide branch, tag, or commit; `STUDIO_SOURCE_REF`, `FRONTEND_SOURCE_REF`, `DESIGN_SOURCE_REF`, `OPS_SOURCE_REF`, and `IAM_SOURCE_REF` override a single role. Build from detached temporary worktrees at the resolved commits, never a developer's mutable checkout. Read [source version locking](references/source-version-locking.md) for the procedure.

For any Operations backend release, resolve the selected source checkout as `OPS_SOURCE_DIR`, then read [the migration workflow](references/ops-atlas-migrations.md) before staging files. The Operations application must never be started before its approved pending Atlas migrations complete.

For any Studio backend release, resolve its Atlas source from the locked
`STUDIO_SOURCE_DIR`, then read [the Studio migration workflow](references/studio-atlas-migrations.md) before staging files. The Studio application must never be started before its approved pending Atlas migrations complete.

## Required controls

- Read the involved repositories' deployment guidance, inspect their status/history/diff, and resolve the release commit, immutable image digest, target, and public origins first.
- Do not print, commit, or copy deployment Secret values. Back up live Compose, Nginx, and `.env.apps` before promotion.
- Use `docker compose --env-file .env.apps` consistently. Do not reset databases, delete volumes, or manually run a single migration SQL file.
- Applying target migrations is a database mutation: require explicit authorization for the selected target. A failed migration or pending revision blocks the affected Operations or Studio backend rollout.
- Before promoting IAM against a persistent authority database, run the repository's first-party bootstrap regression on a disposable database. It must provision the same first-party clients twice and exercise changed public-origin/redirect input. Do not impose a Skill-level "exactly one migration" or single-baseline assumption: use the reviewed repository's declared, ordered migration chain. If its regression rejects a legitimate appended migration because its test fixture only accepts one baseline, stop the IAM release until the repository test and migration contract are aligned; do not bypass the failed regression, delete authority rows, or regenerate persistent PEM files as a workaround.
- Report image digests, backup path, redacted migration evidence, service health, and any checks not run.

## Deployment order

1. Resolve and lock source commits, then validate release worktrees, Compose interpolation, target access, and the candidate immutable image digest.
2. Build and push only the requested services, recording their digests.
3. Back up and stage Compose, Nginx, and the authorized environment manifest.
4. For Operations or Studio backend releases, stage the release-matched migration source and complete its independent Atlas gate before recreating the backend.
5. Pull by digest, start services, and verify health plus the requested functional flow.
