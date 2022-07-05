#!/bin/bash

##set -euo pipefail

# TODO: 
#  Add wait for postgres connection 
#  https://stackoverflow.com/questions/35069027/docker-wait-for-postgresql-to-be-running
#  https://docs.docker.com/compose/startup-order/

sleep 15

alembic upgrade head

#celery -A src.worker.celery_app worker -c 5 --loglevel=info &