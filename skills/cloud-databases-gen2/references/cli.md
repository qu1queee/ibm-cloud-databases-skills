# CLI and HTTP

Source: the [Gen 2 Cloud Databases CLI reference](https://cloud.ibm.com/docs/cloud-databases-gen2?topic=cloud-databases-gen2-cdb-reference).

Commands go through `ibmcloud resource`. The engine skill sets `<engine>`, which fields are valid, and the member and disk bounds.

## Create

```sh
ibmcloud resource service-instance-create <INSTANCE_NAME> <SERVICE_NAME> <SERVICE_PLAN_NAME> <LOCATION> -g <RESOURCE_GROUP> -p '{
  "dataservices": {
    "<engine>": {
      "storage_gb": 10,
      "members": 2,
      "host_flavor": "<flavor-for-this-region>",
      "version": "<major>"
    }
  }
}'
```

`<SERVICE_PLAN_NAME>` contains `gen2`, for example `standard-gen2`.

## Read and update

```sh
ibmcloud resource service-instance <INSTANCE_NAME> -o JSON

ibmcloud resource service-instance-update <INSTANCE_NAME> -p '{
  "dataservices": {
    "<engine>": {
      "storage_gb": 20,
      "members": 2,
      "host_flavor": "<flavor-for-this-region>"
    }
  }
}'
```

Send the new size at or above the current `storage_gb`.

## Restore

```sh
ibmcloud resource service-instance-create <INSTANCE_NAME> <SERVICE_NAME> <SERVICE_PLAN_NAME> <LOCATION> -g <RESOURCE_GROUP> -p '{
  "dataservices": {
    "restore_backup_id": "crn:v1:..."
  }
}'
```

Create and list backups in the console. Restore with `dataservices.restore_backup_id`.

## Service keys

```sh
ibmcloud resource service-key-create <NAME> <ROLE_NAME> --instance-name <INSTANCE_NAME>
ibmcloud resource service-key-delete <NAME>
```

`<ROLE_NAME>` is `Manager` or `Writer`. Create a new key to change a role.

The PostgreSQL getting-started page also shows `-p '{"role_crn":"crn:v1:bluemix:public:iam::::serviceRole:Manager"}'`. Use the positional `<ROLE_NAME>` from this reference. If that command returns a key with no database user, send `role_crn` for the same role.

## HTTP

`POST https://resource-controller.cloud.ibm.com/v2/resource_instances` with an IAM bearer token. Put the same `dataservices` object in `parameters`. Set `resource_plan_id` to the Gen 2 plan id, the same plan the CLI passes as `<SERVICE_PLAN_NAME>`.
