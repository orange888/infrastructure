path "database/creds/monitoring__grafana" {
  capabilities = ["read"]
}

path "database/roles/monitoring__grafana" {
  capabilities = ["read", "update"]
}

path "secrets/data/monitoring/grafana" {
  capabilities = ["read"]
}

path "secrets/data/monitoring/grafana/*" {
  capabilities = ["read"]
}
