# run - Run local server with --nostatic
run:
	@echo "------------------------------------------"
	@echo "***  run local server ***"
	@echo "=========================================="
	#@sudo /usr/bin/fdfs_trackerd /etc/fdfs/tracker.conf restart
	#@sudo /usr/bin/fdfs_storaged /etc/fdfs/storage.conf restart
	#@sudo /usr/bin/fdfs_monitor /etc/fdfs/client.conf restart
	@python3.4 manage.py runserver --nostatic 
	#@celery -A musicfield worker -B -l info 

index:
	@python3.4 manage.py rebuild_index 

static:
	@python3.4 manage.py collectstatic

# celery - run celery task for chat clean
celery:
	@celery -A musicfield worker -B -l info 

# help - Display callable targets.
help:
	@egrep "^# [a-z,\",=,_,-]+ - " Makefile

# bower - Install dependences components with bower
bower:
	@cd ./mufield/static/bower_components && rm ./* -Rf
	@cd ./bin/bower && bower install

# install - install dependenses
install:
	@pip3 install -r config/requirements.txt
	#@cd ./bin/bower && bower install
	#make restframework support markdown tables syntax
	@sed -i "s/'headerid(level=2)']/'headerid(level=2)', 'tables']/g" venv/lib/python3.4/site-packages/rest_framework/compat.py
	#@./config/fastdfs/fastdfs.sh
	#@./config/nginx/nginx.sh

test:
	@python3.4 manage.py test

# style - Check PEP8 and others
PEP8IGNORE=E22,E23,E24,E302,E401
style:
	@echo "PyFlakes check:"
	@echo
	-pyflakes .
	@echo
	@echo "PEP8 check:"
	@echo
	-pep8 --ignore=$(PEP8IGNORE) .


# pylint - Run pylint with pylint-django
# pylint:
# 	pylint *.py --load-plugins pylint_django --py3k

# clean - Clean all temporary files
clean:
	find . -name "*.pyc" -print0 | xargs -0 rm -rf
	find . -name "*.*~" -print0 | xargs -0 rm -rf
	find . -name "__pycache__" -print0 | xargs -0 rm -rf
	@echo "Clean was successfully done!"

