# Consoles 

To access the various consoles, go to `http://<FQDN>/services/status`

![consoles](consoles.png)

## proxy
  
  * [HAProxy](https://github.com/haproxy/haproxy) provides a detailed view of the status and statistics of the servers and services managed by  in real-time. This console is useful for monitoring connection performance, requests, response times, and the health of backend servers.

    ![proxy-console](proxy-console.png)
    
    
## portainer

* [Portainer](https://github.com/portainer/portainer) offers a user-friendly interface for managing [Docker](https://github.com/docker) environments. 

  ![portainer-console](portainer-console.png)

## console

* Through the [migasfree console](https://github.com/migasfree/migasfree-frontend), and utilizing `package deployments`, you can manage a `fleet of computers` by specifying which `packages` should be installed or removed from each computer based on its `attributes`.

  This allows you to customize and control the software environment on each machine according to its specific requirements.

  You'll have access to an extensive range of information about each computer, including both hardware and software details.


  ![migasfree-console](migasfree-console.png)

## public pool

* We can also serve static files for any purpose, making them accessible to users and applications at  `https://<FQDN>/pool`.

  To upload files to this space, go to `https://datashare.<FQDN>/files/pool/`

  ![public-console](public-console.png)


## core

* [Swagger UI](https://github.com/swagger-api/swagger-ui) allows visualize and interact with the [migasfree backend](https://github.com/migasfree/migasfree-backend)' API  without having any of the implementation logic in place
  ![core-console](core-console.png)

## worker

* [Flower](https://github.com/mher/flower)  is a application for monitoring and managing [Celery](https://github.com/celery/celery) clusters. It provides real-time information about the status of Celery workers and tasks.

  ![worker-console](worker-console.png)

## database

* [pgAdmin](https://github.com/pgadmin-org/pgadmin4) provides a powerful and user-friendly interface for [PostgreSQL](https://github.com/postgres/postgres) database administration and management.

  ![database-console](database-console.png)

## datastore

* [RedisInsight](https://github.com/RedisInsight/RedisInsight) provides a comprehensive and intuitive interface for managing [Redis](https://github.com/redis/redis) databases and optimizing their performance.

  ![datastore-console](datastore-console.png)

## datashare

* [Filebrowser](https://github.com/filebrowser/filebrowser) simplifies file management and provides a convenient way to access and organize files through a web interface.

  ![datashare-console](datashare-console.png)

