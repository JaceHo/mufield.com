#!/usr/bin/env bash
if [ -d ./venv ] ; then
    cd ./venv
else
    cd ../../venv
fi
mkdir -p build
cd build
git clone  https://github.com/nginx/nginx.git  -b nginx-1.7
cd nginx
git clone https://github.com/happyfish100/fastdfs-nginx-module.git
mkdir -p /var/lib/nginx/body
sudo cp ../../config/nginx/mod_fastdfs.conf /etc/fdfs/
git clone https://github.com/bpaquet/ngx_http_enhanced_memcached_module.git
yum -y install gcc automake autoconf libtool make gcc-c++ pcre* zlib openssl openssl-devel
./configure --prefix=/usr/share/nginx --sbin-path=/usr/sbin/nginx --conf-path=/etc/nginx/nginx.conf --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --http-client-body-temp-path=/var/lib/nginx/tmp/client_body --http-proxy-temp-path=/var/lib/nginx/tmp/proxy --http-fastcgi-temp-path=/var/lib/nginx/tmp/fastcgi --http-uwsgi-temp-path=/var/lib/nginx/tmp/uwsgi --http-scgi-temp-path=/var/lib/nginx/tmp/scgi --pid-path=/var/run/nginx.pid --lock-path=/var/lock/subsys/nginx --user=nginx --group=nginx --with-file-aio --with-ipv6 --with-http_ssl_module --with-http_realip_module --with-http_addition_module --with-http_xslt_module --with-http_image_filter_module --with-http_geoip_module --with-http_sub_module --with-http_dav_module --with-http_flv_module --with-http_mp4_module --with-http_gzip_static_module --with-http_random_index_module --with-http_secure_link_module --with-http_degradation_module --with-http_stub_status_module --with-http_perl_module --with-mail --with-mail_ssl_module --with-debug '--with-cc-opt=-O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m64 -mtune=generic ' --add-module=./fastdfs-nginx-module/src --with-ld-opt=-Wl,-E

cp
make -j `cat /proc/cpuinfo | grep processor| wc -l` &&sudo make install
 cd ../../
 rm build -rf
 cd ..
