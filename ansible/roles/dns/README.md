# dns

Set Cloudflare DNS records for each host.

## Variables

### `dns_records`

Dict of keys whose values are passed as arguments to the `cloudflare_dns`
module. If there is no `record` value, the key is used as the record. By
default, creates a solo `A` record for the host's FQDN.
