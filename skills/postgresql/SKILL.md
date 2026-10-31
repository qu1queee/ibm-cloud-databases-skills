---
name: postgresql
description: >-
  PostgreSQL on IBM Cloud Databases Gen 2. Use when the user provisions
  databases-for-postgresql, or connects to that instance with psql.
---

# Databases for PostgreSQL Gen 2

## Steps

1. Apply the `cloud-databases-gen2` skill. Done when its lint exits 0.
2. On a provision or scale task, read [references/engine.md](references/engine.md) and fill the shared shape from that table. Done when `service`, `plan`, the `dataservices` key, members, and disk match the table.
3. On a connection or password change, read the connection section of [references/engine.md](references/engine.md). Done when the `psql` command matches that section.
