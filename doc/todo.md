# TODO List

* TODO: tag `<none>` al hacer docker-compose

* TODO: Actualizar contraseña por defecto a `core`

* TODO abrir postgres al exterior del cluster

* TODO: Cambiar HTTP_PORT y HTTPS_PORT funciona a medias -> Repasar configuración en haproxy.

* TODO: Crear comando info

* TODO: Crear comando help

* TODO: Documentar Personalizacion del stack (env.py)

* TODO: Documentar labels del swarm y la relación con los volumenes

* BUG: `datastore_console` no crea la configuración inicial de la DB.
       Si se reinicia el service entonces si que la crea.

* Repasar los test de los clientes

## Para información

```bash
#!/bin/bash

for node in $(docker node ls -q); do

# Obtener la información del nodo

  id=$(docker node inspect $node --format='{{.ID}}')
  hostname=$(docker node inspect $node --format='{{.Description.Hostname}}')
  role=$(docker node inspect $node --format='{{.Spec.Role}}')
  addr=$(docker node inspect $node --format='{{.Status.Addr}}')

# Determinar si el nodo es un manager y si es el líder

  if [ "$role" = "manager" ]; then
    leader=$(docker node inspect $node --format='{{if .ManagerStatus.Leader}}leader{{else}}     {{end}}')
  else
    leader="     "
  fi

# Imprimir la información en formato tabulado

  printf "%-36s %-20s %-10s %-15s %-10s\n" "$id" "$hostname" "$role" "$addr" "$leader"
done
```
