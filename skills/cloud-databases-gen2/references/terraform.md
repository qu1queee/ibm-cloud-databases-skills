# Terraform

Source: the "Gen2 database instance example" on the [`ibm_database`](https://registry.terraform.io/providers/IBM-Cloud/ibm/latest/docs/resources/database) resource.

Copy this shape. The engine skill fills `service`, `plan`, `version`, and `allocation_count`.

```hcl
data "ibm_resource_group" "group" {
  name = "<your_group>"
}

resource "ibm_database" "this" {
  name              = "<name>"
  plan              = "<plan-with-gen2-suffix>"
  location          = "<region>"
  service           = "<databases-for-...>"
  resource_group_id = data.ibm_resource_group.group.id
  service_endpoints = "private"

  group {
    group_id = "member"

    members {
      allocation_count = 2
    }

    disk {
      allocation_mb = 10240
    }

    host_flavor {
      id = "<flavor-for-this-region>"
    }
  }
}

resource "ibm_resource_key" "credentials" {
  name                 = "<credential-name>"
  resource_instance_id = ibm_database.this.id
  parameters           = { role = "Manager" }
}

output "db_connection" {
  value     = ibm_resource_key.credentials.credentials
  sensitive = true
}
```

`parameters.role` is `Manager` or `Writer`. The registry's Gen 2 example omits the role. Set it. A key with a role is what yields the database user.
