#!/bin/sh

sed -E -i "s#^(vokomokum\\.whitelist_came_from\\s*=\\s*).*\$#\\1${REDIRECT_URLS}#" development.ini
sed -E -i "s#^(vokomokum\\.client_secret\\s*=\\s*).*\$#\\1${VOKOMOKUM_CLIENT_SECRET}#" development.ini
sed -E -i "s#request\\.application_url#'${APPLICATION_URL}'#" members/templates/base.pt

echo "Running: $@"
exec "$@"
