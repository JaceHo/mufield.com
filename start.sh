#!/bin/bash
source `pwd`/venv/bin/activate
/usr/bin/screen -S com.mufield -d -m uwsgi --ini config/uwsgi.ini --enable-threads --thunder-lock # the --ini option is used to specify a file
export C_FORCE_ROOT="true" && /usr/bin/screen -S com.mufield.celery -d -m celery -A musicfield worker -B 
/usr/bin/fdfs_trackerd  /etc/fdfs/tracker.conf restart
/usr/bin/fdfs_storaged /etc/fdfs/storage.conf restart
/usr/bin/fdfs_monitor /etc/fdfs/client.conf 
#these only used on production env
service nginx restart &
service mysqld restart &
service rabbitmq-server restart &
service memcached restart &
service redis restart &

