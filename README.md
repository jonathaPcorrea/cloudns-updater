# ClouDNS Dynamic DNS Updater

Lightweight Docker container that automatically keeps your [ClouDNS](https://www.cloudns.net) dynamic DNS record in sync with your current public IP address.

---

## Quick Start

```bash
docker run -d \
  --name cloudns-updater \
  --restart unless-stopped \
  -e CLOUDNS_DOMAIN="yourdomain.com" \
  -e CLOUDNS_TOKEN="your-token-here" \
  seuusuario/cloudns-updater
```

---

## Docker Compose

```yaml
services:
  cloudns-updater:
    image: seuusuario/cloudns-updater:latest
    container_name: cloudns-updater
    restart: unless-stopped
    environment:
      CLOUDNS_DOMAIN: "yourdomain.com"
      CLOUDNS_TOKEN: "your-token-here"
      CLOUDNS_INTERVAL: "1800"
      CLOUDNS_DNS_SERVER: "8.8.8.8"
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `CLOUDNS_DOMAIN` | ✅ | — | Domain to update |
| `CLOUDNS_TOKEN` | ✅ | — | ClouDNS dynamic DNS token |
| `CLOUDNS_INTERVAL` | ❌ | `1800` | Update interval in seconds |
| `CLOUDNS_DNS_SERVER` | ❌ | `8.8.8.8` | DNS server used for resolution |

### How to get your token

1. Log in to [cloudns.net](https://www.cloudns.net)
2. Go to **Dynamic DNS** records
3. Copy the **Dynamic URL** token for your domain

---

## How It Works

On every interval cycle the container will:

1. Fetch the current public IP via `api.ipify.org`
2. Resolve the domain's existing DNS record using the configured DNS server
3. Call the ClouDNS update API only if the IPs differ

---

## Logs

```bash
docker logs -f cloudns-updater
```

Example output:
```
2026-03-05 10:00:00  INFO  Daemon iniciado
2026-03-05 10:00:00  INFO  Domínio  : yourdomain.com
2026-03-05 10:00:00  INFO  Intervalo: 1800 segundos
2026-03-05 10:00:00  INFO  --------------------------------------------------
2026-03-05 10:00:00  INFO  Iniciando processo de atualização de IP...
2026-03-05 10:00:01  INFO  IP real: 189.100.200.10
2026-03-05 10:00:01  INFO  IP atual no DNS para yourdomain.com: 189.100.200.10
2026-03-05 10:00:01  INFO  Atualização não necessária para yourdomain.com
2026-03-05 10:00:01  INFO  Processo de atualização finalizado
```

---

## Source Code

[github.com/jonathaPcorrea/cloudns-updater](https://github.com/jonathaPcorrea/cloudns-updater)
