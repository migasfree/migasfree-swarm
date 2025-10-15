#!/bin/sh

if curl -f http://127.0.0.1:8080
then
    send_message ""
    exit 0
else
    send_message "Unavailable"
    exit 1
fi