#!/bin/bash

PROJECT_ROOT=$(dirname "${BASH_SOURCE[0]}")/..
CERT_DIR=".certs"
OPENSSL_CNF="hack/openssl.cnf"
COLOR_GREEN="\033[0;32m"
COLOR_END="\033[0m"

cd ${PROJECT_ROOT}

generator_token_csv(){
  token_id=$(< /dev/urandom tr -dc a-z0-9 | head -c${1:-6})
  token_secret=$(< /dev/urandom tr -dc a-z0-9 | head -c${1:-16}) 
  token_csv="${token_id}.${token_secret}"
}

generator_kube_ca_cert(){
  openssl genrsa -out ${CERT_DIR}/kube_ca.key 2048 2> /dev/null
  openssl req -x509 -new -nodes -key ${CERT_DIR}/kube_ca.key \
    -config ${OPENSSL_CNF} -subj "/CN=kubernetes" \
	-extensions v3_ca -out ${CERT_DIR}/kube_ca.crt -days 36500
}

generator_etcd_ca_cert(){
  openssl genrsa -out ${CERT_DIR}/etcd_ca.key 2048 2> /dev/null
  openssl req -x509 -new -nodes -key ${CERT_DIR}/etcd_ca.key \
	-config ${OPENSSL_CNF} -subj "/CN=etcd-ca" \
	-extensions v3_ca -out ${CERT_DIR}/etcd_ca.crt -days 36500
}

generator_front_proxy_ca_cert(){
  openssl genrsa -out ${CERT_DIR}/front-proxy-ca.key 2048 2> /dev/null
  openssl req -x509 -new -nodes -key ${CERT_DIR}/front-proxy-ca.key \
	-config ${OPENSSL_CNF} -subj "/CN=front-proxy-ca" \
	-extensions v3_ca -out ${CERT_DIR}/front-proxy-ca.crt -days 36500
}

generator_sa_key_pair(){
  openssl genrsa -out ${CERT_DIR}/sa.key 2048 2> /dev/null
  openssl rsa -in ${CERT_DIR}/sa.key -outform PEM -pubout -out ${CERT_DIR}/sa.pub 2> /dev/null
}

if ! [ -d ${CERT_DIR} ]; then
	mkdir -p ${CERT_DIR}
fi

if ! [ -f "${CERT_DIR}/token.csv" ];then
	generator_token_csv
	echo "generator ${COLOR_GREEN}token_csv${COLOR_END} cert done."
	echo "${token_csv}" > ${CERT_DIR}/token.csv
fi

if ! [ -f "${CERT_DIR}/kube_ca.crt" ];then
	generator_kube_ca_cert
	echo "generator ${COLOR_GREEN}kube_ca${COLOR_END} cert done."
fi

if ! [ -f "${CERT_DIR}/etcd_ca.crt" ];then
	generator_etcd_ca_cert
	echo "generator ${COLOR_GREEN}etcd_ca${COLOR_END} cert done."
fi

if ! [ -f "${CERT_DIR}/front-proxy-ca.crt" ];then
	generator_front_proxy_ca_cert
	echo "generator ${COLOR_GREEN}front-proxy-ca${COLOR_END} cert done."
fi

if ! [ -f "${CERT_DIR}/sa.pub" ];then
	generator_sa_key_pair
	echo "generator ${COLOR_GREEN}sa.key sa.pub${COLOR_END} key pair done."
fi
