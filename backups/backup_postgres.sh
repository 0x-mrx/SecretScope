#!/usr/bin/env bash
# Database Backup Script for SecretScope

# Config
BACKUP_DIR="/var/lib/secretscope/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/secretscope_db_${TIMESTAMP}.sql.gz"
CONTAINER_NAME="secretscope-db"
DB_USER="secretscope"
DB_NAME="secretscope"

# Ensure backup dir exists
mkdir -p "${BACKUP_DIR}"

echo "[*] Initializing Database Backup for SecretScope..."
# Dump database using pg_dump inside Postgres container
docker exec -t "${CONTAINER_NAME}" pg_dump -U "${DB_USER}" -d "${DB_NAME}" | gzip > "${BACKUP_FILE}"

if [ $? -eq 0 ]; then
  echo "[+] Backup successfully compiled: ${BACKUP_FILE}"
  # Retain only last 7 backups
  find "${BACKUP_DIR}" -name "secretscope_db_*.sql.gz" -mtime +7 -delete
  echo "[*] Retention script completed. Older backups pruned."
else
  echo "[-] Critical: Database backup failed!"
  exit 1
fi
