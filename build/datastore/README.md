
# Datastore (Redis)

This service provides a high-performance in-memory data store using **Redis**. it serves as the messaging broker for Celery and the caching layer for the entire Migasfree Swarm ecosystem.

## Diagnostic Commands

You can interact with the datastore from any container on the same network using `redis-cli`.

### Connectivity Check

Verify that the service is responding correctly:

```bash
redis-cli -h datastore -p 6379 ping
# Expected output: PONG
```

### Persistence Test

Test read and write operations:

```bash
# Set a value
redis-cli -h datastore -p 6379 set foo "migasfree"
# Expected output: OK

# Retrieve the value
redis-cli -h datastore -p 6379 get foo
# Expected output: "migasfree"
```

## Security Notes

Access to the datastore is protected by the `${STACK}_superadmin_pass` global secret. Any client connecting from outside the Swarm's trusted infrastructure must use the configured authentication.
