# docker-postgres-azure-backup
make a pg_dump and ship it to azure file storage

```
docker run -it \
-e AZURE_ACCOUNT_NAME="XXXX" \
-e AZURE_ACCOUNT_KEY="XXXX" \
-e AZURE_SHARE_NAME='XXXX' \
-e SLACK_URL="XXXX" \
-e SLACK_CHANNEL="#server" \
-e AZURE_KEEP_BACKUPS=100 \
-e PGHOST="localhost" \
-e PGPORT="5432" \
-e PGUSER="XXXX" \
-e PGPASSWORD="XXXX" \
-e PGDATABASE="XXXXX" \
steffenmllr/docker-postgres-azure-backup
```