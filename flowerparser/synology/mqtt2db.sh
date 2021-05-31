#!/bin/bash
#
# startscript for synology ds
# to be install in /usr/local/etc/rc.d
#
# When the system boots up, it will call mqtt2db.sh start; 
# when it shuts down, it will call mqdb2db.sh stop

logger -p user.warn "mqtt2db"

if [[ $1 == "start" ]]
then
  ( 
  export PATH=$PATH:/usr/local/bin/
  cd /var/services/homes/admin/Projects/solar-esp/flowerparser
  python3 -u ./MQTTParser.py >> /var/log/mqtt2db.log 2>&1 ) &
fi
