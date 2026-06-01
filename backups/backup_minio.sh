#!/usr/bin/env bash
# MinIO Object Storage Backup Script for SecretScope

# Config
BACKUP_DIR="/var/lib/secretscope/backups/minio"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/secretscope_minio_${TIMESTAMP}.tar.gz"
MINIO_VOLUME_PATH="/var/lib/docker/volumes/secretscope_minio_data/_data" # adjust if custom volume is mapped

# Ensure backup dir exists
mkdir -p "${BACKUP_DIR}"

echo "[*] Initializing MinIO Buckets Backup for SecretScope..."
# Compress minio storage volume
tar -czf "${BACKUP_FILE}" "${MINIO_VOLUME_PATH}" 2>/dev/null

if [ $? -eq 0 ]; then
  echo "[+] MinIO backup successfully compiled: ${BACKUP_FILE}"
  # Retain only last 7 backups
  find "${BACKUP_DIR}" -name "secretscope_minio_*.tar.gz" -mtime +7 -delete
  echo "[*] Retention script completed. Older backups pruned."
else
  echo "[-] Critical: MinIO data backup failed!"
  exit 1
fi
