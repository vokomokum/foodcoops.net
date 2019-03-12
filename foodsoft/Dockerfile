FROM foodcoops/foodsoft:4.6

# First add plugin files dealing with dependencies, and install them
# (this avoids having to bundle install each time other source files change)
USER root
COPY plugins/vokomokum/foodsoft_vokomokum.gemspec ./plugins/vokomokum/
COPY plugins/vokomokum/lib/foodsoft_vokomokum/version.rb ./plugins/vokomokum/lib/foodsoft_vokomokum/
RUN echo "gem 'foodsoft_vokomokum', path: 'plugins/vokomokum'" >>Gemfile && \
    bundle config --delete frozen && \
    echo 'gem: --no-document' >> ~/.gemrc && \
    bundle install --without development test -j 4 && \
    rm -Rf ~/.gemrc ~/.bundle

# Then add migrations and update database schema
# (copy them, because `rake foodsoft_vokomokum_engine:install:migrations` needs full source tree)
COPY plugins/vokomokum/db ./plugins/vokomokum/db
RUN export DATABASE_URL=mysql2://localhost/temp && \
    export SECRET_KEY_BASE=thisisnotimportantnow && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y mysql-server && \
    /etc/init.d/mysql start && \
    cp config/app_config.yml.SAMPLE config/app_config.yml && \
    bundle exec rake db:setup && \
    cp plugins/vokomokum/db/migrate/* db/migrate/ && \
    bundle exec rake db:migrate && \
    rm -Rf config/app_config.yml tmp/* && \
    /etc/init.d/mysql stop && \
    rm -Rf /run/mysqld /tmp/* /var/tmp/* /var/lib/mysql /var/log/mysql* && \
    apt-get purge -y --auto-remove mysql-server && \
    rm -Rf /var/lib/apt/lists/* /var/cache/apt/*

# apply temporary patches - remove when merged upstream
COPY patch-*.diff ./
RUN for i in patch-*.diff; do patch -p1 -s -i $i; done

# Then add the remaining plugin files
COPY plugins ./plugins

USER nobody

COPY app_config.yml ./config/
