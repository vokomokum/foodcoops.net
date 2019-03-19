#!/bin/sh
set -e

/usr/sbin/postconf -e "mydomain=${DOMAIN}"
/usr/sbin/postconf -e "myhostname=${HOSTNAME}"
sed -E -i "s#^(password\\s*=\\s*).*\$#\\1${DB_PASSWORD}#" /etc/postfix/alias_maps.cf

# setup smarthost
/usr/sbin/postconf -e "relayhost=[${SMTP_ADDRESS}]:${SMTP_PORT}"
if [ "$SMTP_USER_NAME" ]; then
  /usr/sbin/postconf -e "smtp_sasl_auth_enable=yes"
  /usr/sbin/postconf -e "smtp_sasl_password_maps=static:${SMTP_USER_NAME}:${SMTP_PASSWORD}"
  /usr/sbin/postconf -e "smtp_sasl_security_options=noanonymous"
  /usr/sbin/postconf -e "smtp_tls_security_level=encrypt"
fi

# make sure newly mounted volumes are populated
/usr/sbin/postfix post-install create-missing

# figure out which certificate to use
CERT_FILE=/certs/${HOSTNAME}.pem
[ -r "$CERT_FILE" ] || CERT_FILE=/certs/dummy.pem
[ -r "$CERT_FILE" ] || CERT_FILE=
if [ "$CERT_FILE" ]; then
  /usr/sbin/postconf -e "smtpd_tls_cert_file=${CERT_FILE}"
else
  /usr/sbin/postconf -X smtpd_tls_cert_file
fi

# make sure rsyslogd can be started (in case container gets re-used)
rm -f /var/run/rsyslogd.pid

# reload on trigger
if [ -n "$POSTFIX_RELOAD_FILE" ]; then
	echo "Watching $POSTFIX_RELOAD_FILE for reload requests"
	[ -e "$POSTFIX_RELOAD_FILE" ] || touch "$POSTFIX_RELOAD_FILE"
	inotifyd "/reload-postfix.sh" "$POSTFIX_RELOAD_FILE:ec" &
fi

exec "$@"
