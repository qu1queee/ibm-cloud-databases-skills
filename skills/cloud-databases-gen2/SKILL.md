---
name: cloud-databases-gen2
description: >-
  Gen 2 control plane for IBM Cloud Databases. Use when the user
  provisions or changes a standard-gen2 instance, an ibm_database resource,
  an ibmcloud resource command, or a Resource Controller service key.
---

# IBM Cloud Databases Gen 2

The engine skill supplies the service name, the `dataservices` key, member and disk limits, and how to connect.

## Steps

1. Use a plan that contains `gen2`. Done when every plan in the draft contains `gen2`. When the existing plan does not, say this skill writes Gen 2 plans and wait for confirmation before changing the generation.
2. Choose one interface. Terraform when the repo has `.tf` files. The IBM Cloud CLI otherwise. The Resource Controller HTTP API when the user asks for HTTP. Done when one interface is selected.
3. Read the reference for that interface.
   - Terraform: [references/terraform.md](references/terraform.md), the `ibm_database` group shape.
   - CLI or HTTP: [references/cli.md](references/cli.md), the `ibmcloud resource` command and the same `dataservices` body.
   - Conflicting IBM docs: [references/limits.md](references/limits.md), when a published page and these references disagree.
   Done when the draft follows the reference for the chosen interface.
4. Write one shape. Terraform uses `group` blocks and disk in `allocation_mb`. CLI and HTTP use `dataservices` and disk in `storage_gb`. Set a non-empty `host_flavor` for this location. Keep disk at its current size or larger. Done when the draft matches that interface and the engine skill's limits.
5. Lint from this skill's directory with `python scripts/lint_gen2.py <file>`. Done when the command exits 0.
6. Show `terraform plan`, or the `ibmcloud resource` command. Create or update the instance only after the user asks to apply. A short-lived token can expire during a 15–20 minute create: refresh `IC_API_KEY` and plan again. If Terraform tainted `ibm_database` after the instance exists, untaint that address. Done when the plan or command is shown, and apply has run only if the user asked.
7. Mark credential outputs `sensitive = true`. Report connection field names. Done when the secret stays in the sensitive output.
