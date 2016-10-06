# Select your backends from this list
BACKEND_CDB ?= no
BACKEND_MYSQL ?= yes
BACKEND_SQLITE ?= no
BACKEND_REDIS ?= no
BACKEND_POSTGRES ?= no
BACKEND_LDAP ?= no
BACKEND_HTTP ?= no
BACKEND_MONGO ?= no

# Specify the path to the Mosquitto sources here
MOSQUITTO_SRC = ../src/mosquitto-1.3.5

# Specify the path the OpenSSL here
OPENSSLDIR = /usr

