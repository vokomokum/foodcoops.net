Vokomokum deployment setup
==========================

This is the production setup for [Vokomokum](http://vokomokum.nl/), a food
cooperative in Amsterdam, NL for: members, finances and ordering.

If you want to run it for yourself, see [setup](#setup), or if you'd like to modify the configuration,
please proceed to [common tasks](#common-tasks).


_**Please note** that this is currently under development._


## Setup

To get it running yourself, you need to provide the private information via environment variables to
`docker-compose`. Here is an example to build and start the project locally:

```shell
export DOMAIN=vkmkm.localhost
export HOSTNAME_ORDER=order.vkmkm.localhost
export HOSTNAME_MEMBERS=members.vkmkm.localhost
export MEMBERS_DB_PASSWORD=secret_mb
export SMTP_DB_PASSWORD=secret_ms
export FOODSOFT_DB_PASSWORD=secret_fs
export FOODSOFT_SECRET_KEY_BASE=1234567890abcdefghijklmnoprstuvwxyz
export MYSQL_ROOT_PASSWORD=mysql
export SHAREDLISTS_DB_PASSWORD=secret_sl
export SHAREDLISTS_SECRET_KEY_BASE=abcdefghijklmnopqrstuvwxyz1234567890
export VOKOMOKUM_CLIENT_SECRET=secret_cc
# remove the following line on production when ready
export CERTBOT_DISABLED=1

docker-compose build --pull
docker-compose pull
docker-compose up -d
```

You can also store the variables in `.env` instead.

The above setup should work on a development machine. Depending on your setup, you may need
to point `order.vkmkm.localhost` and `members.vkmkm.localhost` in your `/etc/hosts` to `127.0.0.1`.


### Initial database setup

On first time run, you'll need to setup the database. Start and connect to it as root:

```shell
docker-compose up -d mariadb redis
docker exec -it vkmkm-deploy_mariadb_1 mysql -u root -p
```

Then run the following SQL commands:

```sql
-- create foodsoft database
CREATE DATABASE foodsoft_vkmkm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci;
GRANT ALL ON foodsoft_vkmkm.* TO foodsoft@'%' IDENTIFIED BY 'secret_fs';

-- create sharedlists database
CREATE DATABASE sharedlists CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci;
GRANT ALL ON sharedlists.* TO sharedlists@'%' IDENTIFIED BY 'secret_sl';
GRANT SELECT ON sharedlists.suppliers TO foodsoft@'%';
GRANT SELECT ON sharedlists.articles TO foodsoft@'%';

-- create members database
CREATE DATABASE members CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci;
GRANT ALL ON members.* TO members@'%' IDENTIFIED BY 'secret_mb';
GRANT SELECT ON members.members TO smtp@'%' IDENTIFIED BY 'secret_ms';
GRANT SELECT ON members.workgroups TO smtp@'%';
GRANT SELECT ON members.wg_leadership TO smtp@'%';
GRANT SELECT ON members.wg_membership TO smtp@'%';
```

Note that some `GRANT` statements may only work after you've populated the database. If
an error happens because of that, try again after doing so in the next step.

Subsequently you need to populate the databases:

```shell
docker-compose run --rm foodsoft bundle exec rake db:setup
docker-compose run --rm sharedlists bundle exec rake db:setup
docker-compose run --rm members ./dbsetup.py
```

You may want to load a database seed for Foodsoft:

```shell
docker-compose run --rm foodsoft bundle exec rake db:drop db:create db:schema:load db:seed:small.nl
```

### SSL certificates

By default, a dummy SSL certificate will be generated (for `localhost`). This is useful for
development, and to bootstrap easily.

For production, you need proper SSL certificates. These are provided by
[letsencrypt](https://letsencrypt.org). Set `DOMAIN` and make sure the DNS is setup correctly.
Then remove `CERTBOT_DISABLED=1` from the environment and restart the certbot instance.

### Deployment

Deployment happens by running a script on the server, which pulls the latest changes from
the remote repository, rebuilds the docker images and runs them when needed.

You need to clone the repository and configure it for group access:

```sh
git clone --config core.sharedRepository=true https://github.com/vokomokum/vkmkm-deploy.git
chgrp -R docker vkmkm-deploy
chmod -R g+sw vkmkm-deploy
```

Finally, setup a daily cronjob to ensure security updates for the docker images:

```sh
echo `readlink -f deploy.sh` > /etc/cron.daily/deploy.sh
chmod u+x /etc/cron.daily/deploy.sh
```

## Common tasks

* [Deploying](#deploying)
* [Upgrading Foodsoft](#upgrading-foodsoft)


### Deploying

When you've made a change to this repository, you'll likely want to deploy it to production.
First push the changes to the [Github repository](https://github.com/vokomokum/vkmkm-deploy),
then run `deploy.sh` on the server.

### Upgrading Foodsoft

**Note:** this section has not been tested yet!

To update Foodsoft to a new version:

* Update version in number in [`foodsoft/Dockerfile`](foodsoft/Dockerfile)
* Look at the [changelog](https://github.com/foodcoops/foodsoft/blob/master/CHANGELOG.md) to see if anything is required for migrating, and prepare it.
* Test it locally, especially our customizations. Don't forget this!
* [Deploy](#deploying)
* Without delay, run database migrations and restart the foodsoft images.

```shell
cd /home/deploy/vkmkm-deploy
docker-compose run --rm foodsoft bundle exec rake db:migrate
docker-compose restart foodsoft foodsoft_worker foodsoft_smtp
```

