#!/bin/sh

if curl -f http://localhost:8080/openapi.json
then
    send_message ""
    exit 0
else
    send_message "Unavailable"
    exit 1
fi