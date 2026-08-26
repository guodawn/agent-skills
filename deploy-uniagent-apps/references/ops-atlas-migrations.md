# Operations Atlas migration gate

The Operations backend uses Atlas with the `golang-migrate` source format. The canonical source is the release-matched `migrations/` directory, and Atlas' revision ledger records application. Do not depend on a particular checkout name or a sibling directory layout.

Before deployment, resolve the approved Operations source repository once and use that path for every migration operation:

```bash
export OPS_SOURCE_DIR=/path/to/operations-backend-source
OPS_SOURCE_DIR=$(git -C "$OPS_SOURCE_DIR" rev-parse --show-toplevel)
test -f "$OPS_SOURCE_DIR/migrations/atlas.sum"
test -f "$OPS_SOURCE_DIR/docker/atlas/README.md"
```

If these checks fail or multiple candidate repositories exist, stop and obtain the source path or release artifact. Never infer it from a name such as `uniagent-ops-platform`.

Before deployment, from the same reviewed Operations source revision used for the image:

```bash
cd "$OPS_SOURCE_DIR"
make atlas-hash
export UNIAGENT_OPS_ATLAS_DEV_URL='postgres://.../ops_atlas_dev?sslmode=disable'
make migrate-validate
```

The development URL must identify a disposable empty database. It is not the deployment target.

Stage `migrations/*.sql` and `migrations/atlas.sum` beside the deployment configuration. Before recreating `uniagent-ops-platform`, run the pinned Atlas image against that staged source and the target DSN supplied by the protected `.env.apps` file:

```yaml
services:
  ops-migrate:
    image: arigaio/atlas@sha256:e21623d79e164afeb9df421b1025789a14254f30307b0aed384572cb268dd56b
    network_mode: host
    volumes:
      - ./ops-migrations:/work/migrations:ro
    environment:
      UNIAGENT_OPS_POSTGRES_DSN: ${UNIAGENT_OPS_POSTGRES_DSN:?set}
    command: ["migrate", "apply", "--url", "${UNIAGENT_OPS_POSTGRES_DSN:?set}", "--dir", "file:///work/migrations?format=golang-migrate"]
```

Run it with `docker compose --env-file .env.apps -f ops-migrate.compose.yml run --rm ops-migrate`. Require explicit authorization for the target database. A non-zero result, a checksum discrepancy, or a pending revision after apply blocks rollout.

After apply, inspect Atlas status and the released feature's schema shape without exposing the DSN or business data. Do not use manual `ALTER TABLE`, execute individual SQL migrations, or use `atlas migrate set` unless a separately approved baseline-reconciliation plan applies.
