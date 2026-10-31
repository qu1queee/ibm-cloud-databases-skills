data "ibm_resource_group" "group" {
  name = "default"
}

resource "ibm_database" "this" {
  name              = "pg-demo"
  plan              = "standard-gen2"
  location          = "ca-mon"
  service           = "databases-for-postgresql"
  resource_group_id = data.ibm_resource_group.group.id
  service_endpoints = "private"
  version           = "18"

  group {
    group_id = "member"

    members {
      allocation_count = 2
    }

    disk {
      allocation_mb = 10240
    }

    host_flavor {
      id = "bx3d.4x20"
    }
  }
}

resource "ibm_resource_key" "credentials" {
  name                 = "pg-manager"
  resource_instance_id = ibm_database.this.id
  parameters           = { role = "Manager" }
}

output "db_connection" {
  value     = ibm_resource_key.credentials.credentials
  sensitive = true
}
