#!/bin/sh

pg_isready -d "${POSTGRES_DB}" -U "${POSTGRES_USER}"
