# Tailscale Host Discovery Reference

## ARP Table — Identifying Tailscale Hosts

Tailscale interfaces on macOS appear as `bridge100`, `bridge101`, etc. Use `arp -a` and grep for Tailscale hostnames:

```
macbook-pro-m2max.tail7c2425.ts.net (100.79.251.70)
macbook-pro-personal.tail7c2425.ts.net (100.120.35.86)
```

The machine-name prefix before `.tail` is the Tailscale machine name (user-configurable in Tailscale admin panel).

## Hostname Format

`<machine-name>.tail<random-id>.ts.net`

- `tail7c2425` is the Tailscale network ID (org-specific)
- The full hostname resolves to the Tailscale IP wherever the client is connected
- Works across subnets, NAT, and different physical networks

## Known Machines From This Session

| Short Name | Tailscale Hostname | Tailscale IP | Local User |
|---|---|---|---|
| macbook-pro | macbook-pro-personal.tail7c2425.ts.net | 100.120.35.86 | admin |
| (current) | macbook-pro-m2max.tail7c2425.ts.net | 100.79.251.70 | eric |
