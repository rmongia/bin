#!/bin/sh -x
export PYTHONPATH=$PYTHONPATH:/home/rmongia/kido

SERVICE_NAME="Logshipper Client Status"
if [ $# -eq 1 ]; then
  SITE=`echo $1 | cut -d'-' -f1`
  SERVER=$1
  /$HOME/kido/tools/production/proxy_controller.py schedule_svc_downtime $SERVER "$SERVICE_NAME"
fi
