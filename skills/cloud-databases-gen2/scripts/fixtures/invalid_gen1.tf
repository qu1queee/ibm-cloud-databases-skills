resource "ibm_database" "this" {
  name           = "pg-classic"
  plan           = "standard"
  location       = "us-south"
  service        = "databases-for-postgresql"
  adminpassword  = "secret-secret-secret"
  service_endpoints = "public"

  users {
    name     = "admin"
    password = "secret-secret-secret"
  }

  group {
    group_id = "member"
    memory {
      allocation_mb = 4096
    }
    disk {
      allocation_mb = 5120
    }
  }
}

output "db_connection" {
  value = ibm_database.this.id
}
