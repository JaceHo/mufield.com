#!/bin/bash -x
git archive --format=tar.gz HEAD > mufield.com.tar
scp -rp mufield.com.tar root@mufield.com:/var/www/
ssh root@mufield.com "
mkdir -p /var/www/mufield.com/;
rm /var/www/mufield.com/* -rf;
mv /var/www/mufield.com.tar /var/www/mufield.com/;
rm /etc/nginx/conf.d/mufield.com.conf;
mv /var/www/mufield.com/config/mufield.com.conf /etc/nginx/conf.d/;
cd /var/www/mufield.com/;
virtualenv-3.4 venv --no-site-packages;
source venv/bin/activate;
tar zxvf mufield.com.tar;
./stop.sh;
make install;
./manage.py migrate;
./manage.py flush --noinput;
./manage.py syncdb --noinput;
sed -i 's/DEBUG = True/DEBUG = False/g' musicfield/settings.py;
./start.sh;
"
rm mufield.com.tar
