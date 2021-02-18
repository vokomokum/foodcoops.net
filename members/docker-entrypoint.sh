#!/bin/sh

# Update variables in the members app
sed -E -i "s#^(sqlalchemy\\.url\\s*=\\s*).*\$#\\1mysql+pymysql://members:${MEMBERS_DB_PASSWORD}@mariadb/members#" production.ini
sed -E -i "s#^(vokomokum\\.whitelist_came_from\\s*=\\s*).*\$#\\1${REDIRECT_URLS}#" production.ini
sed -E -i "s#^(vokomokum\\.client_secret\\s*=\\s*).*\$#\\1${VOKOMOKUM_CLIENT_SECRET}#" production.ini
sed -E -i "s#^(vokomokum\\.mail_sender\\s*=\\s*).*\$#\\1${EMAIL_SENDER}#" production.ini
sed -E -i "s#request\\.application_url#'${APPLICATION_URL}'#" members/templates/base.pt

sed -E -i "s#\\{\\{HOSTNAME\\}\\}#${HOSTNAME}#g" /etc/msmtprc

echo "Running: $@"
exec "$@"
