#!/bin/bash

# 2. Rodar o container
docker run -d \
  --name cloudns-updater \
  --restart unless-stopped \
  -e CLOUDNS_DOMAIN="yourdomain.com" \
  -e CLOUDNS_TOKEN="your-token-here" \
  -e CLOUDNS_INTERVAL="1800" \
  jonathapcorrea/cloudns-updater
