# ufw

Adds UFW rules and enables the firewall.

- Loops through rules passed as dependency variables
- Enables the firewall at startup

## Variables

### `ufw_rules`

List of rules passed directly to the Ansible ufw module.
