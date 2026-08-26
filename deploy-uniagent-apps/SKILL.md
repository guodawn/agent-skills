---
name: deploy-uniagent-apps
description: Build and deploy the UniAgent Apps HTTPS stack, including the required Atlas migration gate for Operations backend releases.
---

# Deploy UniAgent Apps

Deploy the UniAgent Studio, Portal, Account, Operations, and IAM application stack from reviewed local source to an SSH target. Treat the remote `.env.apps` as protected deployment state and publish immutable image digests only.

For any Operations backend release, resolve the selected source checkout as `OPS_SOURCE_DIR`, then read [the migration workflow](references/ops-atlas-migrations.md) before staging files. The Operations application must never be started before its approved pending Atlas migrations complete. Directory names and sibling layouts are not deployment contracts.

## Required controls

- Read the involved repositories' deployment guidance, inspect their status/history/diff, and resolve the release commit, immutable image digest, target, and public origins first.
- Do not print, commit, or copy deployment Secret values. Back up live Compose, Nginx, and `.env.apps` before promotion.
- Use `docker compose --env-file .env.apps` consistently. Do not reset databases, delete volumes, or manually run a single migration SQL file.
- Applying target migrations is a database mutation: require explicit authorization for the selected target. A failed migration or pending revision blocks the Operations backend rollout.
- Report image digests, backup path, redacted migration evidence, service health, and any checks not run.

## Deployment order

1. Validate source, Compose interpolation, target access, and the candidate immutable image digest.
2. Build and push only the requested services, recording their digests.
3. Back up and stage Compose, Nginx, and the authorized environment manifest.
4. For Operations backend releases, stage the release-matched `migrations/` source and complete the Atlas gate.
5. Pull by digest, start services, and verify health plus the requested functional flow.
