# PostgreSQL on Gen 2

Fill the `cloud-databases-gen2` shape with this table.

| Field | Value |
| --- | --- |
| Terraform `service` / CLI `SERVICE_NAME` | `databases-for-postgresql` |
| Plan | `standard-gen2` |
| CLI `dataservices` key | `postgresql` |
| Default database | `postgres` |
| Port | `5432` |
| Members | `2` or `3` in production. `1` is the single-node beta: one member, and failover is manual |
| Disk | `storage_gb` 10–9600 on the CLI. Terraform `allocation_mb` is that size in MB (`10` GB is `10240`) |
| Version | Set the major version at create. Omit it to take the current major |

CLI body:

```json
{
  "dataservices": {
    "postgresql": {
      "storage_gb": 10,
      "members": 2,
      "host_flavor": "<flavor-for-this-region>",
      "version": "18"
    }
  }
}
```

Configuration parameters set at create live under `dataservices.postgresql.configuration`. Keep `max_connections` at or below 500, and use a pooler when the workload needs more client connections.

## Users and connection

A `Manager` key inherits `ibm_admin`. A `Writer` key inherits `ibm_writer`. The username looks like `ibmcloud_<hex>`. Customers connect as that service-key user.

Connect with `psql` over the private endpoint:

```text
sslmode=verify-full
host=<id>.private.<region>.postgresql.dataservices.appdomain.cloud
port=5432
dbname=postgres
```

Source: [Connecting with psql](https://cloud.ibm.com/docs/databases-for-postgresql-gen2?topic=databases-for-postgresql-gen2-connecting-psql).

Change a password in a session:

```sql
ALTER ROLE <user> WITH PASSWORD '<new>';
```

## Operations

Source: [Gen 1 vs Gen 2 feature parity](https://cloud.ibm.com/docs/databases-for-postgresql-gen2?topic=databases-for-postgresql-gen2-postgresql-gen1-vs-gen2-differences-feature-parity).

- Restore from a snapshot or a backup CRN.
- Change flavor or disk explicitly.
- Add members to spread reads.
- Cancel backends from a `Manager` session with `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid();`, or restart the instance.
- Scope a Key Protect service-to-service policy to the Key Protect instance or one key CRN.
