#!/bin/sh -x
export PYTHONPATH=$PYTHONPATH:/home/rmongia/kido

SERVICE_NAME="IPVS Status of Real Proxies"
if [ $# -eq 1 ]; then
  SITE=`echo $1 | cut -d'-' -f1`
  LLB01="$SITE-DNS01"
  LLB02="$SITE-DNS02"
  /$HOME/kido/tools/production/proxy_controller.py schedule_downtime $1
  /$HOME/kido/tools/production/proxy_controller.py schedule_svc_downtime $LLB01 "$SERVICE_NAME"
  /$HOME/kido/tools/production/proxy_controller.py schedule_svc_downtime $LLB02 "$SERVICE_NAME"
fi
