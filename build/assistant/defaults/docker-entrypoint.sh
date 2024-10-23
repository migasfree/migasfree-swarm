#!/bin/sh
. /venv/bin/activate

function wait {
    local _SERVER=$1
    local _PORT=$2
    local counter=0
    until [ $counter -gt 30 ]
    do
        nc -z $_SERVER $_PORT 2> /dev/null
        if [ $? = 0 ]
        then
            echo "$_SERVER:$_PORT is running."
            return
        else
            echo "$_SERVER:$_PORT is not running after $counter seconds."
            sleep 1
        fi
        ((counter++))
    done
    echo "Rebooting container"
    exit 1
}



/usr/bin/send_message "waiting database"
wait $POSTGRES_HOST $POSTGRES_PORT

echo "


                   ●                          ●●
                                             ●
         ●●● ●●    ●    ●●     ●●●     ●●●  ●●●●  ●●●  ●●●    ●●●
        ●   ●  ●   ●   ●  ●       ●   ●      ●   ●    ●   ●  ●   ●
        ●   ●  ●   ●   ●  ●    ●●●●    ●●    ●   ●    ●●●●   ●●●●
        ●   ●  ●   ●   ●  ●   ●   ●      ●   ●   ●    ●      ●
        ●   ●  ●   ●    ●●●    ●●●    ●●●    ●   ●     ●●●    ●●●
                          ●
                        ●●

        $SERVICE ($TAG)
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"

/usr/bin/send_message ""
/usr/bin/reload_proxy 3

python3 /usr/bin/service.py 8080
