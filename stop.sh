#!/bin/bash -x
/usr/bin/screen -X -d -r  com.mufield.celery quit
/usr/bin/screen -X -d -r com.mufield quit
/usr/bin/screen -wipe
