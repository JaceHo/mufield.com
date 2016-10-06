#!/usr/bin/env bash
if [ -d ./venv ] ; then
    cd ./venv
else
    pwd
    cd ../../venv/
fi
mkdir -p build
cd build
wget https://codeload.github.com/happyfish100/libfastcommon/zip/V1.0.7 --no-check-certificate
unzip V1.0.7
cd libfastcommon-1.0.7
./make.sh && sudo ./make.sh install
cd ..
git clone https://github.com/happyfish100/fastdfs.git
cd fastdfs
if [ -f /usr/lib/libpthread.so ] || [ -f /usr/local/lib/libpthread.so ] || [ -f /lib64/libpthread.so ] || [ -f /usr/lib64/libpthread.so ] || [ -f /usr/lib/x86_64-linux-gnu/libpthread.so ] || [ -f /usr/lib/libpthread.a ] || [ -f /usr/local/lib/libpthread.a ] || [ -f /lib64/libpthread.a ] || [ -f /usr/lib64/libpthread.a ] || [ -f /usr/lib/x86_64-linux-gnu/libpthread.a ]; then
    ./make.sh
    ./make.sh && sudo ./make.sh install
else
   cd ../../../
   exit 1
fi
sudo mkdir /var/www/fastdfs -p
sudo mkdir /var/www/fastdfs/storage -p
cd ../../../config/fastdfs
sudo cp http.conf /etc/fdfs/
sudo cp client.conf /etc/fdfs/
sudo cp storage.conf /etc/fdfs/
sudo cp tracker.conf /etc/fdfs/
cd ../../venv
rm build -rf
cd ..
