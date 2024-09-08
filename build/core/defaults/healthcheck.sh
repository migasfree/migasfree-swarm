#!/bin/sh

if [ "$SERVICE" = "${STACK}_core" ]
then

    # core    
    timeout 1 curl --fail --silent --head --request GET http://127.0.0.1:8080 > /dev/null
    if [ $? -eq 0 ]
    then
        if ! [ -f /var/tmp/healthy ]
        then
            touch /var/tmp/healthy
            send_message ""
            # Important: Reconfigure in the background after 3 seconds; this container must be healthy first.
            reload_proxy 3
        fi
    else
        rm /var/tmp/healthy || :
        send_message "Service Unavailable"
        exit 1  
    fi

elif [ "$SERVICE" = "${STACK}_worker" ]
then

    # worker
    MIGASFREE_SECRET_DIR=/var/run/secrets
    BROKER_URL=redis://default:$(cat ${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass)@datastore:6379/0
    . /venv/bin/activate
    timeout 1 celery -b ${BROKER_URL} inspect ping -d celery@${HOSTNAME} > /dev/null
    if [ $? -eq 0 ]
    then
        if ! [ -f /var/tmp/healthy ]
        then
            touch /var/tmp/healthy
            send_message ""
            # Important: Reconfigure in the background after 3 seconds; this container must be healthy first.
            reload_proxy 3
        fi 
    else
        rm /var/tmp/healthy || :
        send_message "Unavailable"
        exit 1
    fi

else

    # beat
    ps -p $(cat /var/tmp/celery.pid)
    if [ $? -eq 0 ]
    then
        if ! [ -f /var/tmp/healthy ]
        then
            touch /var/tmp/healthy
            send_message ""
            # Important: Reconfigure in the background after 3 seconds; this container must be healthy first.
            reload_proxy 3
        fi 
    else
        rm /var/tmp/healthy || :
        send_message "Unavailable"
        exit 1
    fi

fi

exit 0