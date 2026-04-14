# Status & TODO List

## 🚀 Pendiente (To-Do)

### 🛠️ Infraestructura y Despliegue

* [ ] **Configuración Postgres**: Publicar el puerto de la base de datos (`database`) al exterior del cluster en `stack.template` (actualmente cerrado).

### 🛡️ Seguridad y Estandarización

* [ ] **Patrón "Root-Init, User-Run"**: Refactorizar los servicios legados (especialmente `manager` y `database`) para que sigan el patrón de inicialización como root y ejecución como usuario sin privilegios.
* [ ] **Credenciales**: Actualizar la generación de contraseñas por defecto para usar `core` (actualmente se generan aleatoriamente en `deploy.py`).

### 📚 Documentación y Pruebas

* [ ] **QA Clientes**: Revisar y actualizar los entornos de prueba de los clientes (`test/client*`) para asegurar compatibilidad total.

---

## ✅ Hecho (Done)

### 📚 Documentación

* [x] **Labels y Volúmenes**: Relación entre etiquetas de nodo (`database=true`, `datastore=true`) y persistencia. Documentado en `doc/explanation/data-persistence.md`.
* [x] **Comando `info`**: Implementado comando `migasfree-swarm info` para auditoría rápida del cluster y los stacks.
* [x] **Referencia `env.py`**: Nuevo documento de referencia detallando todas las variables de personalización. Documentado en `doc/reference/env-variables.md`.
* [x] **Comando `help`**: Implementado en el entrypoint de la imagen `swarm`. Se muestra por defecto si el comando no existe.

### 🛡️ Seguridad

* [x] **Refactorización Consolas**: `datastore_console` y otras consolas ya inicializan configuración mediante entrypoint refactorizado (patrón Root-Init).
* [x] **Limpieza de imágenes**: Implementado prune automático de imágenes `<none>` en `build.sh` y `pull.sh`. Añadido comando `migasfree-swarm prune`.
* [x] **Puertos dinámicos**: Eliminado el harcodeo de puertos 80/443 en `haproxy.template` y `stack.template`. Ahora el cluster puede servir en cualquier puerto configurado en `env.py`.

---

## 💡 Notas e Información Útil

### Visualización rápida de nodos del cluster

```bash
#!/bin/bash
for node in $(docker node ls -q); do
  id=$(docker node inspect $node --format='{{.ID}}')
  hostname=$(docker node inspect $node --format='{{.Description.Hostname}}')
  role=$(docker node inspect $node --format='{{.Spec.Role}}')
  addr=$(docker node inspect $node --format='{{.Status.Addr}}')
  if [ "$role" = "manager" ]; then
    leader=$(docker node inspect $node --format='{{if .ManagerStatus.Leader}}leader{{else}}     {{end}}')
  else
    leader="     "
  fi
  printf "%-36s %-20s %-10s %-15s %-10s\n" "$id" "$hostname" "$role" "$addr" "$leader"
done
```
