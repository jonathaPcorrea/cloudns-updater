#!/usr/bin/env python3
"""
ClouDNS Dynamic DNS Updater
Equivalente Python do projeto: https://github.com/pferraris/docker-cloudns

Variáveis de ambiente:
  CLOUDNS_DOMAIN      - Domínio a ser atualizado (obrigatório)
  CLOUDNS_TOKEN       - Token dinâmico do ClouDNS (obrigatório)
  CLOUDNS_INTERVAL    - Intervalo em segundos (padrão: 1800 = 30 min)
  CLOUDNS_DNS_SERVER  - Servidor DNS para resolução (padrão: 8.8.8.8)
"""

import os
import sys
import time
import socket
import urllib.request
import urllib.error
import signal
import logging

# --- Configuração de logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# --- Variáveis de ambiente ---
DOMAIN      = os.environ.get("CLOUDNS_DOMAIN")
TOKEN       = os.environ.get("CLOUDNS_TOKEN")
INTERVAL    = int(os.environ.get("CLOUDNS_INTERVAL", 30 * 60))   # segundos
DNS_SERVER  = os.environ.get("CLOUDNS_DNS_SERVER", "8.8.8.8")


def get_real_ip() -> str:
    """Obtém o IP público real via api.ipify.org."""
    url = "https://api.ipify.org/"
    with urllib.request.urlopen(url, timeout=10) as resp:
        return resp.read().decode("utf-8").strip()


def get_current_ip(domain: str) -> str:
    """Resolve o IP atual do domínio usando o servidor DNS configurado."""
    # Usa o servidor DNS definido pela variável de ambiente
    resolver = socket.getaddrinfo.__module__  # apenas para fins de referência

    # Para usar um DNS customizado, fazemos a query diretamente via socket UDP
    import struct

    def build_dns_query(domain: str) -> bytes:
        qname = b"".join(
            bytes([len(part)]) + part.encode() for part in domain.split(".")
        ) + b"\x00"
        return (
            b"\xaa\xbb"   # ID
            b"\x01\x00"   # flags: standard query
            b"\x00\x01"   # QDCOUNT = 1
            b"\x00\x00\x00\x00\x00\x00"  # ANCOUNT, NSCOUNT, ARCOUNT
            + qname
            + b"\x00\x01"  # QTYPE  = A
            + b"\x00\x01"  # QCLASS = IN
        )

    query = build_dns_query(domain)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    try:
        sock.sendto(query, (DNS_SERVER, 53))
        data, _ = sock.recvfrom(512)
    finally:
        sock.close()

    # Parse simplificado: pula cabeçalho (12 bytes) + question section
    offset = 12
    # Pula QNAME
    while data[offset] != 0:
        if data[offset] >= 0xC0:   # ponteiro de compressão
            offset += 2
            break
        offset += data[offset] + 1
    else:
        offset += 1
    offset += 4  # QTYPE + QCLASS

    # Lê primeira resposta
    # Pula NAME (pode ser ponteiro)
    if data[offset] >= 0xC0:
        offset += 2
    else:
        while data[offset] != 0:
            offset += data[offset] + 1
        offset += 1

    offset += 10  # TYPE(2) + CLASS(2) + TTL(4) + RDLENGTH(2)
    ip = ".".join(str(b) for b in data[offset: offset + 4])
    return ip


def call_cloudns_update(token: str) -> str:
    """Chama a API de atualização dinâmica do ClouDNS."""
    url = f"https://ipv4.cloudns.net/api/dynamicURL/?q={token}"
    with urllib.request.urlopen(url, timeout=10) as resp:
        return resp.read().decode("utf-8").strip()


def update_ip() -> None:
    """Ciclo principal: verifica e atualiza o IP se necessário."""
    log.info("-" * 50)
    log.info("Iniciando processo de atualização de IP...")

    try:
        real_ip = get_real_ip()
        log.info(f"IP real: {real_ip}")

        current_ip = get_current_ip(DOMAIN)
        log.info(f"IP atual no DNS para {DOMAIN}: {current_ip}")

        if current_ip != real_ip:
            response = call_cloudns_update(TOKEN)
            log.info(f"IP {real_ip} atualizado com sucesso para {DOMAIN}: {response}")
        else:
            log.info(f"Atualização não necessária para {DOMAIN}")

    except Exception as err:
        log.error(f"Erro: {err}")

    finally:
        log.info("Processo de atualização finalizado")


def main() -> None:
    log.info("Daemon iniciado")

    # Validações obrigatórias
    if not DOMAIN:
        log.error("Variável CLOUDNS_DOMAIN não definida")
        sys.exit(1)
    if not TOKEN:
        log.error("Variável CLOUDNS_TOKEN não definida")
        sys.exit(1)

    log.info(f"Domínio  : {DOMAIN}")
    log.info(f"Intervalo: {INTERVAL} segundos")
    log.info(f"DNS      : {DNS_SERVER}")

    # Encerramento gracioso
    def handle_exit(signum, frame):
        log.info("Daemon encerrado.")
        sys.exit(0)

    signal.signal(signal.SIGINT,  handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # Primeira execução imediata
    update_ip()

    # Loop periódico
    while True:
        time.sleep(INTERVAL)
        update_ip()


if __name__ == "__main__":
    main()