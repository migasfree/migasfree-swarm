# Migasfree Swarm

This project runs the Migrasfree Server Suite 5 on [Docker Swarm](https://docs.docker.com/engine/swarm/).


## Project Directory Structure

* `build`: Source code for the Docker images.
* `doc`: Documentation.
* `images`: Directory containing pre-built Docker images.
* `migration`: Migration script from version 4.
* `test`: Testing scripts.

## Testing Environment Architecture

![cluster-testing](doc/cluster-testing.png)

* The environment variable `DATASHARE_FS` should be set to `local`.
* All data is stored in `local volumes` on `node 1`.

## Production Environment Architecture


![cluster-production](doc/cluster-production.png)


* The Swarm cluster handles both **port 80** and **port 443**; however, only port 443 is shown in the diagram for clarity.

* The environment variable `DATASHARE_FS` should be set to `nfs`.

* Data is stored on an `external NFS volume` outside the Swarm cluster, except for the `database volume` ([PostgreSQL](https://www.postgresql.org/)) and the `datastore volume` ([Redis](https://redis.io/)), which are kept local for better performance.


## Requirements

#### 1. FQDN & DNS

* Choose a suitable `FQDN` for your Migasfree server, e.g., `migasfree.mydomain.com`. 

  The `FQDN` and the following `subdomains` must resolve to the server's IP. Configure them in your `Domain Name Service (DNS)`.

* For `testing purposes` only, you can add the domain names to your `desktop machine` to access Migasfree services by editing the `/etc/hosts` file:

  ```/etc/hosts
  x.x.x.x <FQDN>
  x.x.x.x portainer.<FQDN>
  x.x.x.x datastore.<FQDN>
  x.x.x.x database.<FQDN>
  x.x.x.x datashare.<FQDN>
  x.x.x.x worker.<FQDN>
  ```

#### 2. NFS

* In a `Production Environment`, an `NFS server` is required so each Swarm cluster node has access to the data. Refer to [NFS install](doc/nfs.md)

  * Disk SPACE VOLUME >= 1TB

  During deployment, set `DATASHARE_FS` to `nfs`

  ```txt
  DATASHARE_FS (local | nfs): nfs
  ```

* In a `Testing Environment` you can use a `local` volume on the swarm manager node where the stack is deployed.

  During deployment, set `DATASHARE_FS` to `local`

  ```txt
  DATASHARE_FS (local | nfs): local
  ```
  
  In this `local mode`, data will only be accessible on the manager node where the deployment takes place, used for testing on a `single-node` Swarm cluster.

#### 3. Swarm node hardware

* RAM >= 16 GB
* CPU >= 4
* Disk SPACE SYSTEM >= 80 GB

#### 4. Swarm node software 

* [Install docker engine](https://docs.docker.com/engine/install) on each Swarm node.

## Deployment

* On the host that will act as the `Swarm manager`, create an empty directory and run:



  ```bash
  # Example of creating an empty directory
  #     mkdir /data/cluster
  #     cd /data/cluster

  docker run --detach=false --rm -ti -v $(pwd):/stack -v /var/run/docker.sock:/var/run/docker.sock  migasfree/swarm:5.0-beta config
  ```


* Initial configuration:
  ```txt
  (for nfs)

  DATASHARE_FS (local | nfs): nfs
  DATASHARE_SERVER (x.x.x.x): 172.0.0.20 
  DATASHARE_PATH (/exports/migasfree-swarm):
  ```
  
  ```txt
  (for local)
  
  DATASHARE_FS (local | nfs): local
  ```


 * Two files will be created in the directory: `env.py` and `migasfree-swarm`.

  * Check the contents of `env.py`
  
    ```bash
    cat env.py 
    ```
    Example output:

    ```txt
    DATASHARE_FS='nfs'
    DATASHARE_SERVER='172.0.0.20'
    DATASHARE_PATH='/exports/migasfree-swarm'
    DATASHARE_PORT='2049'
    ```
## Downloading images

* Although it is not strictly necessary, you can pre-download the images we will need now.

  ```
  ./migasfree-swarm pull
  ```


## Deploying the Stack

  * Deploy the `Migasfree stack` by running:

    ```bash
    ./migasfree-swarm deploy
    ```
    
    During deployment:
    ```txt
    STACK (): inv 
    FQDN (migasfree.acme.com): inv.org

    Warning! This system is not a Swarm node.
    Do you want to create a manager node? (Y/n):y

    ```

  * You can monitor the services by visiting  https://<FQDN>/services/status.

## Undeploying the Stack

* To `undeploy` the `Migasfree stack`, run:

  ```bash
  ./migasfree-swarm undeploy
  ```

  You can redeploy it with:

  ```bash
  ./migasfree-swarm deploy
  ```
  


## Logins

  * To access the `administration consoles`, visit `https://<FQDN>/services/status`. View the credentials by running:

    ```bash
    ./migasfree-swarm secret
    ```

    Example credentials:

    ```txt
    proxy & portainer:

        ryuPnPkU:rPi3iHdjBUoE0RudZZo6R53tPDifRD

    Stack inv:

        admin:ajwtcC788fkipE5nh2ZU0Hcmlrj4tR

    ```
  
    The format is `username:password`.

    ![consoles](doc/consoles.png)

    More information about the [consoles](doc/consoles.md)

## Production Consoles

* To disable consoles that are unnecessary in production:

  ```bash
  ./migasfree-swarm consoles-pro
  ```
  
  This disables the database, datastore, and worker consoles.

## Development Consoles

* Enable all development consoles:

  ```bash
  ./migasfree-swarm consoles-dev
  ```

## Certificates

TODO Certicates

## Persistence

In Docker, volumes provide persistence by allowing data generated and used by containers to be stored outside the container's lifecycle. While a container can be deleted or recreated, volumes store data on the host’s filesystem, ensuring that it is not lost when the container no longer exists. By using volumes, containers can securely and efficiently access shared or persistent data, ensuring that critical information, such as databases or configuration files, remains intact beyond the lifespan of the container.

Migasfree Swarm uses three volumes:

1. `migasfree-swarm` (local|nfs)

    ```txt
    * portainer       
    * certificates
    * credentials
    * datashares     
      * inv    
    ```
    This shared volume will be present on `all nodes` in the Swarm cluster.

2. `inv_database`    (local)

   A single `local volume` on a specified Swarm node.
3. `inv_datastore`   (local) 

   A single `local volume` on a specified Swarm node.

## Backups

TODO backups

## Installing and Synchronizing with Migasfree Client 5

  * If you are testing Migasfree, go to `https://<FQDN>/pool/install/` and check the migasfree-client.txt file to manually install a client. However, this is not the recommended method for installation. Ideally, the client configuration should be packaged for proper deployment.

## Leaving the Swarm

* To leave the Swarm cluster without deleting volumes:

  ```bash
  ./migasfree-swarm leave
  ```

## Deleting volumes

* If you are testing Migasfree and no longer need the data on your Migasfree server, you can list and delete the volumes on a specific node by running the following commands:

    To list volumes: 
    
    ```bash
    docker volume ls
    ```

    To remove a volume: 
    
    ```
    docker volume rm <volume>
    ```


## Building images

* To build the Docker images:

  ```bash
  cd build
  bash build.sh
  ```

## TODO
  Refer to the [todo list](doc/todo)
