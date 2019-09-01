# service_user

Creates a service user for running Ansible playbooks.

- Creates the service user and pirmary group
- Adds the SSH public key to the service user
- Gives the service user passwordless `sudo` permissions
- Locks the service user's password

## Variables

### `service_user_group`

(default: `ansible`) Name of the primary group for the service user.

### `service_user_name`

(default: `ansible`) Name of the service user.
