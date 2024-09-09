
* TODO: Actualizar contraseña por defecto a `core`

* TODO: `CERBOT` 

       * Programar los subdominios, Comprobar y Documentar

* TODO: Documentar join node swarm

* TODO: Documentar labels del swarm y la relación con los volumenes

* TODO: Crear comando info

* TODO: Crear comando help

* BUG: `datastore_console` no crea la configuración inicial de la DB.
       Si se reinicia el service entonces si que la crea.

* BUG: proxy se despliega en modo `global`. Se debería compartir el fichero /etc/haproxy/haproxy.cfg
  
  Cuando un contenedor manda un mensaje al proxy, lo recibe una de las instancias del proxy que regenerará esta 
  configuración. Una vez hecho esto debe recargarse dicha configuracion en cada uno de los proxys.


* Repasar los test de los clientes
