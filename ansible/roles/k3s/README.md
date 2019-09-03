# k3s

Installs and configures the k3s server and agents.

## Variables

### `k3s_version`

(default: `v0.9.0-rc2`) The version of k3s to install or upgrade to.

### `k3s_cluster_secret`

(default: `null`) Shared secret to bootstrap a k3s cluster.

### `k3s_command`

(default: `server`) The k3s command to install, `server` or `agent`.

### `k3s_command_args`

(default: `[]`) List of arguments to pass to the k3s command.

### `k3s_install_bin_dir`

(default: `/usr/local/bin`) Directory into which to install the k3s binary
and install, killall, and uninstall scripts.

### `k3s_install_name`

(default: `null`) Name to use for the k3s service; uses the default `k3s`
value if left unset.

### `k3s_install_systemd_dir`

(default: `/etc/systemd/system`) Directory into which to install the systemd
scripts.

### `k3s_install_type`

(default: `null`) systemd service type to install; uses the default from the
k3s install script if left unset.

### `k3s_node_labels`

(default: `{}`) Object containing keys and values to use as node labels on
provisioning.

### `k3s_node_taints`

(default: `{}`) Object containing keys and values to use as node taints on
provisioning.

### `k3s_url`

(default: `https://localhost:6443`) Address of the k3s server.
