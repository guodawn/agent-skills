# Studio Atlas migration gate

The Studio backend owns the Atlas source at
`docker/atlas/studio/migrations/`. The complete ordered migration chain and
`atlas.sum` must come from the same locked `STUDIO_SOURCE_DIR` commit used for
the Studio image. Do not reuse an old remote bootstrap directory, run an
individual SQL file, or repair a missing table manually.

Before deployment, validate the locked source and use a disposable development
database for replayability checks:

```bash
test -f "$STUDIO_SOURCE_DIR/docker/atlas/studio/migrations/atlas.sum"
test -f "$STUDIO_SOURCE_DIR/docker/atlas/README.md"
atlas migrate validate --dir "file://$STUDIO_SOURCE_DIR/docker/atlas/studio/migrations"
cd "$STUDIO_SOURCE_DIR"
make migrate-validate
```

Stage every `*.sql` file and `atlas.sum` read-only beside the deployment
configuration. Before recreating `agentstudio-server`, inspect status and apply
only after the user explicitly authorizes the Studio database target. Use the
Studio revision schema explicitly: an integration database can also contain
Operations objects and its separate Operations Atlas ledger.

```yaml
services:
  studio-migrate:
    image: arigaio/atlas@sha256:e21623d79e164afeb9df421b1025789a14254f30307b0aed384572cb268dd56b
    network_mode: "container:uniagent-apps-agentstudio-server-1"
    volumes:
      - ./studio-migrations:/work/migrations:ro
    environment:
      POSTGRES_DSN: ${POSTGRES_DSN:?set}
```

Run the Atlas command through the service environment so the DSN is never
printed:

```bash
docker compose --env-file .env.apps -f studio-migrate.compose.yml run --rm \
  --entrypoint /bin/sh studio-migrate -ceu \
  'atlas migrate status --url "$POSTGRES_DSN" --dir file:///work/migrations \
  --revisions-schema atlas_schema_revisions'

docker compose --env-file .env.apps -f studio-migrate.compose.yml run --rm \
  --entrypoint /bin/sh studio-migrate -ceu \
  'atlas migrate apply --url "$POSTGRES_DSN" --dir file:///work/migrations \
  --revisions-schema atlas_schema_revisions'
```

Run status again and require `Pending Files: 0`, then verify the migration's
required schema object and restart `agentstudio-server`. If the Studio ledger
does not exist, stop before applying: first audit that all objects owned by the
claimed baseline match exactly, while excluding unrelated Operations and
runtime-created tables. Only then, and with separately explicit baseline
reconciliation approval, use `atlas migrate set` for that verified Studio
baseline. Never use ledger adoption to hide a mismatch.
