#!/bin/bash
###############################################################################
## Copyright (c) 2007-2024, Patrick Germain Placidoux
## All rights reserved.
##
## This file is part of KastMenu (Unixes Operating System's Menus Broadkasting).
##
## KastMenu is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## KastMenu is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with KastMenu.  If not, see <http://www.gnu.org/licenses/>.
##
## Home: http://www.kastmenu.org
## Contact: kastmenu@kastmenu.org
###############################################################################



# set -x
set -e # Fail at first Error.

umask 0007


# KAST_DIR, ETC_KEYS, HOSTNAME and TEMP_DIR: are env variables:
# -------------------------------------------------------------
if test "${KAST_DIR}" == ""
then
echo "Error: Parameter 1: KAST_DIR cannot not be null !"
exit 1
fi

# Default Values:
# ---------------
if test "${TEMP_DIR}" == ""
then
TEMP_DIR=/tmp
fi
echo "TEMP_DIR is: ${TEMP_DIR}"

if test "${ETC_KEYS}" == ""
then
ETC_KEYS='/etc/kastmenu/kastweb/keys'
fi
echo "ETC_KEYS is: ${ETC_KEYS}"

HOSTNAME=$(hostname)
if test "${FULL_FRONT_HOSTNAME}" == ""
then
FULL_FRONT_HOSTNAME=${HOSTNAME}
fi
echo "FULL_FRONT_HOSTNAME is: ${FULL_FRONT_HOSTNAME}"



RANDOM=$$ # seeds RANDOM from process id of script.

gen_serial_int() {
    value=$(echo $RANDOM | md5sum |  awk '{$0=$1};NF' | cksum |  awk '{$0=$1};NF')
    echo $value
}

gen_serial_hex() {
    # See: https://mta.openssl.org/pipermail/openssl-users/2017-August/006351.html
    echo $(openssl rand -hex 18)
}


# PREPARING DIRS:
# ---------------
if [ ! -d "${ETC_KEYS}" ]; then mkdir ${ETC_KEYS};fi
if [ ! -d "${ETC_KEYS}/caclients" ]; then mkdir ${ETC_KEYS}/caclients;fi

CNF_DIR_FROM=${KAST_DIR}/core/kwadlib/security/sslkeygen/CNF/kastweb

rm -fr ${ETC_KEYS}/caclients/to_kastserver > /dev/null 2>&1 || echo '' > /dev/null 2>&1
if test $? -ne 0
then
echo "sslkeygen Error Trying to create directory: ${ETC_KEYS}/CNF  !"
exit 1
fi
mkdir ${ETC_KEYS}/caclients/to_kastserver
if test $? -ne 0
then
echo "sslkeygen Error Trying to create directory: ${ETC_KEYS}/CNF  !"
exit 1
fi


rm -fr ${ETC_KEYS}/CNF > /dev/null 2>&1 || echo '' > /dev/null 2>&1
if test $? -ne 0
then
echo "sslkeygen Error Trying to create directory: ${ETC_KEYS}/CNF  !"
exit 1
fi
mkdir ${ETC_KEYS}/CNF
if test $? -ne 0
then
echo "sslkeygen Error Trying to create directory: ${ETC_KEYS}/CNF  !"
exit 1
fi

## cd $ETC_KEYS
CNF_DIR=${ETC_KEYS}/CNF

sed -e "s/{{FULL_FRONT_HOSTNAME}}/${FULL_FRONT_HOSTNAME}/g" ${CNF_DIR_FROM}/kastweb.kastmenu.cnf.tmpl > ${CNF_DIR}/kastweb.kastmenu.cnf


# ================================
# ROOT CA: kastmenu.{hostname}.ca:
# ================================
# No password: remove -nodes and aes256 (des3 depraceted)
openssl genrsa  -aes256 -out ${ETC_KEYS}/${FULL_FRONT_HOSTNAME}.key -passout file:${TEMP_DIR}/fpass.txt  4096
openssl rsa -in ${ETC_KEYS}/${FULL_FRONT_HOSTNAME}.key -pubout -out ${ETC_KEYS}/${FULL_FRONT_HOSTNAME}.pub -passin file:${TEMP_DIR}/fpass.txt

openssl req -new -x509 -sha256 -days 36000 -key ${ETC_KEYS}/${FULL_FRONT_HOSTNAME}.key   -out ${ETC_KEYS}/${FULL_FRONT_HOSTNAME}.crt -config ${CNF_DIR}/kastweb.kastmenu.cnf -passin file:${TEMP_DIR}/fpass.txt
rm ${TEMP_DIR}/fpass.txt

cp ${ETC_KEYS}/${FULL_FRONT_HOSTNAME}.crt ${ETC_KEYS}/caclients/to_kastserver

# See:
# - https://stackoverflow.com/questions/25889341/what-is-the-equivalent-of-unix-c-rehash-command-script-on-linux
# openssl c_rehash in order to be used by Apache and Python ssl.context capath:
# - https://stackoverflow.com/questions/30344893/how-to-force-apache-2-2-to-send-the-full-certificate-chain
# You can also use the SSLCACertificatePath directive and put the original .crt files into the directory specified. However, you also have to create hash
# symlinks to them. This is done with the c_rehash tool, which is part of openssl. For example,
c_rehash ${ETC_KEYS}/caclients/to_kastserver

chmod -R u+rwx ${ETC_KEYS}
chmod -R go-w ${ETC_KEYS}
chmod -R go+rx ${ETC_KEYS}


if [ -d /etc/kastmenu/keys/caclients/to_kastweb ] &&  [ -d /etc/kastmenu/keys/caclients ] ; then
    echo "SSL Kastmenu Keys finishing:
Copy: Found local /etc/kastmenu/keys/caclients/to_kastweb/. to /etc/kastmenu/keys/caclients"
    cp -r /etc/kastmenu/keys/caclients/to_kastweb/.  /etc/kastmenu/keys/caclients
    sudo chmod o+r /etc/kastmenu/keys/caclients/*.crt
fi
