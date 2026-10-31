ibmcloud resource service-instance-create pg-demo databases-for-postgresql standard-gen2 ca-mon -g default -p '{
  "dataservices": {
    "postgresql": {
      "storage_gb": 10,
      "members": 2,
      "host_flavor": "b3c.8x32.encrypted",
      "version": "18"
    }
  }
}'

ibmcloud resource service-key-create pg-manager Manager --instance-name pg-demo
