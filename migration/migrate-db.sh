#!/bin/bash

. ../config/env/stack

DB_V5=$(docker ps | grep ${STACK}_database | awk '{print $1}')
BE_V5=$(docker ps | grep ${STACK}_core | awk '{print $1}' | head -n 1)

OLD_HOST=$1
OLD_PORT=$2
OLD_DB=$3
OLD_USER=$4
OLD_PWD=$5

function help {
    echo "Syntax: migrate-db OLD_HOST OLD_PORT [OLD_DB] [OLD_USER] [OLD_PWD]"
    echo
    echo "Samples:"
    echo "    migrate-db 192.168.1.105 5555"
    echo "    migrate_db 172.16.17.20 5432 migasfree migasfree mipass"
    exit 1
}

if [ -z "$OLD_HOST" ]
then
    help
fi

if [ -z "$OLD_PORT" ]
then
    help
fi

if [ -z "$OLD_DB" ]
then
    OLD_DB=migasfree
fi

if [ -z "$OLD_USER" ]
then
    OLD_USER=migasfree
fi

if [ -z "$OLD_PWD" ]
then
    OLD_PWD=migasfree
fi

echo
echo "WARNING !!!!"
read -p "This process import the database from the v4 instance: $OLD_HOST:$OLD_PORT. Are you sure [yes/N]?"
echo
if [[ $REPLY = "yes" ]]
then
    # MIGRATE DATABASE FROM V4 TO V5
    # ==============================
    echo "DATA MIGRATION"
    echo "=============="

    _REPLICAS_BE=$(docker service inspect --format='{{.Spec.Mode.Replicated.Replicas}}' ${STACK}_core)
    _REPLICAS_FE=$(docker service inspect --format='{{.Spec.Mode.Replicated.Replicas}}' ${STACK}_console)
    bash ../run/scale.sh ${STACK}_core 0
    bash ../run/scale.sh ${STACK}_console 0
    echo "***** CORE & CONSOLE: DISABLED *****"

    /usr/bin/time -f "Time DATA MIGRATION: %E" docker exec ${DB_V5} bash -c "echo yes| bash /usr/share/migration/migrate_from_v4 $OLD_HOST $OLD_PORT $OLD_DB $OLD_USER $OLD_PWD"

    bash ../run/scale.sh ${STACK}core $_REPLICAS_BE
    bash ../run/scale.sh ${STACK}_console $_REPLICAS_FE
    echo "***** CORE & CONSOLE: ENABLED *****"

    BE_V5=$(docker ps | grep ${STACK}_backend | awk '{print $1}' | head -n 1)

    # SUMMARIZE SYNCS
    # ================
    let _COUNTER=0
    while true
    do
        _YEAR=$(date -d "now -$_COUNTER year" +"%Y")

        echo "Calculate syncronizations ${_YEAR} ..."
        /usr/bin/time -f "Time ${_YEAR}: %E" docker exec ${BE_V5} bash -c ". /venv/bin/activate; django-admin refresh_redis_syncs --since $_YEAR --until $_YEAR > /dev/null"

        if [ "$_YEAR" = "2010" ]
        then
            break
        fi
        _COUNTER=$(($_COUNTER -1))
    done
fi
