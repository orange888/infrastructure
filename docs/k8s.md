# Kubernetes

## Deployment order

### Core services

#### Phase 1

* Kilo
* CRDs (`_crd.yml`)

#### Phase 2

* CoreDNS
* Metrics Server
* Namespace annotations (`_namespace.yml`)

#### Phase 3

1. Consul
2. Vault

    * Initialize and unseal
    * Vault intermediate CA
    * Add Vault intermediate CA to Ansible group variables
    * Run Ansible manifests tasks
    * Cycle and unseal Vault pods
    * Vault Kubernetes authentication config
