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


# TEMP_DIR, FULL_FRONT_HOSTNAME: are env variables:
# -------------------------------------------------
if test "${TEMP_DIR}" == ""
then
TEMP_DIR=/tmp
fi
echo "TEMP_DIR is: ${TEMP_DIR}"

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
    echo $(openssl rand -hex 32)
}


# PREPARING DIRS:
# ---------------
KAST_DIR=/opt/kastmenu/current

ETC_KEYS=/etc/kastmenu/keys
if [ ! -d "${ETC_KEYS}" ]; then mkdir ${ETC_KEYS};fi
if [ ! -d "${ETC_KEYS}/caclients" ]; then mkdir ${ETC_KEYS}/caclients;fi

CNF_DIR_FROM=${KAST_DIR}/core/kwadlib/security/sslkeygen/CNF/kastserver
KEY_PASSPHASE=$(gen_serial_hex)
echo $KEY_PASSPHASE > ${ETC_KEYS}/fpass.txt

rm -fr ${ETC_KEYS}/caclients/to_kastweb
if test $? -ne 0
then
echo "sslkeygen Error Trying to create directory: ${ETC_KEYS}/CNF  !"
exit 1
fi
mkdir ${ETC_KEYS}/caclients/to_kastweb
if test $? -ne 0
then
echo "sslkeygen Error Trying to create directory: ${ETC_KEYS}/CNF  !"
exit 1
fi


rm -fr ${ETC_KEYS}/CNF
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

sed -e "s/{{HOSTNAME}}/${HOSTNAME}/g" ${CNF_DIR_FROM}/kastmenu.ca.cnf.tmpl > ${CNF_DIR}/kastmenu.ca.cnf


# ================================
# ROOT CA: kastmenu.{hostname}.ca:
# ================================
# With password: remove -nodes use aes256 (des3 depraceted)
openssl genrsa  -aes256 -out ${ETC_KEYS}/kastmenu.${HOSTNAME}.ca.key -passout file:${ETC_KEYS}/fpass.txt  4096 > /dev/null
openssl rsa -in ${ETC_KEYS}/kastmenu.${HOSTNAME}.ca.key -pubout -out ${ETC_KEYS}/kastmenu.${HOSTNAME}.ca.pub -passin file:${ETC_KEYS}/fpass.txt

openssl req -new -x509 -sha256 -days 36000 -key ${ETC_KEYS}/kastmenu.${HOSTNAME}.ca.key   -out ${ETC_KEYS}/kastmenu.${HOSTNAME}.ca.crt -config ${CNF_DIR}/kastmenu.ca.cnf  -extensions req_ext -passin file:${ETC_KEYS}/fpass.txt > /dev/null



# ================
# KASTSERVER CERT:
# ================
# kwad.client
# "/CN=kwad/OU=users/OU=clients/O=kwad"
# CSR:
openssl genrsa  -aes256 -out ${ETC_KEYS}/${FULL_FRONT_HOSTNAME}.key -passout file:${ETC_KEYS}/fpass.txt  4096 > /dev/null
openssl rsa -in ${ETC_KEYS}/${FULL_FRONT_HOSTNAME}.key -pubout -out ${ETC_KEYS}/${FULL_FRONT_HOSTNAME}.pub -passin file:${ETC_KEYS}/fpass.txt > /dev/null

openssl req -new -sha256 -subj  "/CN=${FULL_FRONT_HOSTNAME}/OU=kastserver/OU=kastmenu/O=${HOSTNAME}/DC=${FULL_FRONT_HOSTNAME}" -key ${ETC_KEYS}/${FULL_FRONT_HOSTNAME}.key -out ${ETC_KEYS}/${FULL_FRONT_HOSTNAME}.csr  -passin file:${ETC_KEYS}/fpass.txt  > /dev/null

openssl x509 -req -days 3600 -in ${ETC_KEYS}/${FULL_FRONT_HOSTNAME}.csr -CA ${ETC_KEYS}/kastmenu.${HOSTNAME}.ca.crt -CAkey ${ETC_KEYS}/kastmenu.${HOSTNAME}.ca.key -set_serial 0x$(gen_serial_hex) -out ${ETC_KEYS}/${FULL_FRONT_HOSTNAME}.crt  -passin file:${ETC_KEYS}/fpass.txt > /dev/null


cp ${ETC_KEYS}/kastmenu.${HOSTNAME}.ca.crt ${ETC_KEYS}/caclients/to_kastweb
cp ${ETC_KEYS}/${FULL_FRONT_HOSTNAME}.crt ${ETC_KEYS}/caclients/to_kastweb

# See: 
# - https://stackoverflow.com/questions/25889341/what-is-the-equivalent-of-unix-c-rehash-command-script-on-linux
# openssl c_rehash in order to be used by Apache and Python ssl.context capath:
# - https://stackoverflow.com/questions/30344893/how-to-force-apache-2-2-to-send-the-full-certificate-chain
# You can also use the SSLCACertificatePath directive and put the original .crt files into the directory specified. However, you also have to create hash 
# symlinks to them. This is done with the c_rehash tool, which is part of openssl. For example,
c_rehash ${ETC_KEYS}/caclients/to_kastweb

# Only if launch by root:
if (( $EUID != 0 )); then
chown -R kastserver:kastserver ${ETC_KEYS}
fi
chmod -R u+rwx ${ETC_KEYS}
chmod -R go-rwx ${ETC_KEYS}
chmod -R g+rx ${ETC_KEYS}


echo "SSL Kastserver Keys finishing:
a) Copy: /etc/kastmenu/keys/caclients/to_kastweb/. to /etc/kastmenu/kastweb/keys/caclients and
to /etc/kastmenu/keys/caclients if exist:"
mkdir -p /etc/kastmenu/kastweb/keys/caclients
cp -r /etc/kastmenu/keys/caclients/to_kastweb/. /etc/kastmenu/kastweb/keys/caclients
sudo chmod o+r /etc/kastmenu/kastweb/keys/caclients/*.crt
if [ -d /etc/kastmenu/keys/caclients ] ; then
    cp -r /etc/kastmenu/keys/caclients/to_kastweb/.  /etc/kastmenu/keys/caclients
    sudo chmod o+r /etc/kastmenu/keys/caclients/*.crt
fi


echo ""
echo "To be copied to each machine/kastmenu-base installation:"
echo "e.g.: sudo cp -r /etc/kastmenu/keys/caclients/to_kastweb/.  /etc/kastmenu/keys/caclients"
